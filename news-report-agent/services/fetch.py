# services/fetch.py — RSS/검색/스크레이퍼/오케스트레이션 통합 모듈

from __future__ import annotations

# Standard library
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

# Third-party
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import feedparser
import requests
from newspaper import Article, Config
from playwright.sync_api import sync_playwright

# (선택) .env 로드 위치는 앱 엔트리에서 하는 걸 권장하지만,
# 필요하면 아래 주석 해제
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# 0) 공통 상수/유틸
# ─────────────────────────────────────────────────────────────────────────────
REJECT_PATHS = ["/tag/", "/topic/", "/hub/", "/section/", "/category/"]

def is_hub(url: str) -> bool:
    """
    허브/토픽 인덱스 페이지 판별
    url.lower() 안에 REJECT_PATHS의 문자열들이 포함되었는지 판별
    """
    return any(p in url.lower() for p in REJECT_PATHS)

def _extract_domain(url: str) -> str:
    """
    url에서 도메인 이름만 추출하는 함수
    urlparse(url) : 리턴값은 아래와 같음
        ParseResult(
            scheme='https',
            netloc='www.bbc.com',
            path='/news/world-asia-12345',
            params='',
            query='',
            fragment=''
        )
    """
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host

# for extract_fox()
DEFAULT_HEADERS = {
    # 최신 크롬 UA 흉내 (윈도우)
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

REQ_TIMEOUT = 60

def _polite_delay():
    time.sleep(0.6 + random.random() * 0.6)

def _normalize_authors(cands: List[str]) -> List[str]:
    out, seen = [], set()
    for s in cands:
        x = (s or "").strip()
        if not x:
            continue
        # 잡음 제거
        if x.startswith("@"):  # 트위터 핸들 제거
            continue
        if x.startswith(("http://", "https://")):  # URL 값 제거(France24 페북 등)
            continue
        x = re.sub(r'^\s*(by|BY)\s+', '', x).strip()   # 'By ' 제거
        x = re.sub(r'\s*기자$', '', x).strip()         # 한글 '기자' 접미사 제거
        x = re.sub(r'\s*\|\s*$', '', x).strip()        # 끝의 |
        x = re.sub(r'^[\-–—|·,:;\s]+|[\-–—|·,:;\s]+$', '', x).strip()  # 양끝 구두점
        k = x.lower()
        if x and k not in seen:
            out.append(x); seen.add(k)
    return out

def _norm_url(u: str) -> str:
    """비교/맵핑용 URL 정규화: 스킴/호스트 소문자, 경로 끝 슬래시 제거, 쿼리/프래그먼트 제거"""
    if not u:
        return ""
    p = urlparse(u)
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme.lower(), p.netloc.lower(), path, "", "", ""))

def _amp_variant(url: str) -> Optional[str]:
    """가능하면 AMP URL로 변환 (폭스 등 다수 매체가 /amp 지원)."""
    try:
        parsed = urlparse(url)
        # 이미 amp면 None
        if re.search(r"/amp/?$", parsed.path):
            return None
        # 뉴욕타임스는 ?outputType=amp, 폭스/가디언 등은 path에 /amp
        host = parsed.netloc.lower()
        if "nytimes.com" in host:
            q = f"{parsed.query}&outputType=amp" if parsed.query else "outputType=amp"
            return urlunparse(parsed._replace(query=q))
        # 기본: path 뒤에 /amp 붙이기
        amp_path = parsed.path.rstrip("/") + "/amp"
        return urlunparse(parsed._replace(path=amp_path))
    except Exception:
        return None

def _requests_get_html(url: str, headers: dict | None = None, timeout: int = REQ_TIMEOUT) -> tuple[int, Optional[str], str]:
    """단순 requests GET로 HTML을 가져온다. (리다이렉트 따라감)
       반환: (status_code, final_url or None, text)
    """
    hdrs = DEFAULT_HEADERS.copy()
    if headers:
        hdrs.update(headers)
    resp = requests.get(url, headers=hdrs, timeout=timeout, allow_redirects=True)
    # 일부 사이트는 인코딩 헤더가 부정확 → requests가 추정
    resp.encoding = resp.encoding or resp.apparent_encoding
    return resp.status_code, resp.url, resp.text

def _newspaper_from_html(url: str, html: str) -> dict:
    """이미 확보한 HTML을 newspaper로 파싱."""
    cfg = Config()
    cfg.browser_user_agent = DEFAULT_HEADERS["User-Agent"]
    cfg.request_timeout = REQ_TIMEOUT
    article = Article(url=url, config=cfg)
    article.set_html(html)
    article.parse()
    return {
        "title": article.title,
        "authors": article.authors,
        "published_date": str(article.publish_date) if article.publish_date else None,
        "text": article.text,
        "url": url,
    }

# ─────────────────────────────────────────────────────────────────────────────
# 1) RSS 수집기
# ─────────────────────────────────────────────────────────────────────────────
def rss_articles(feed_url: str) -> List[dict]:
    """
    RSS 한 개의 feed에서 기사 항목(dict) 목록을 반환.
    각 항목엔 최소 'link' 키가 있어야 함.
    """
    feed = feedparser.parse(feed_url)
    articles: List[dict] = []
    for entry in feed.entries[:10]:  # 상위 10개만
        articles.append({
            "title": entry.get("title"),
            "link": entry.get("link"),
            # feedparser는 published/updated 등의 형태로 제공할 수 있음
            "published": entry.get("published", "") or entry.get("updated", "") or entry.get("pubDate", ""),
            "summary": entry.get("summary", "")
        })
    return articles

# ─────────────────────────────────────────────────────────────────────────────
# 2) 검색(Serper)
# ─────────────────────────────────────────────────────────────────────────────
def search(query: str, *, n_results: int = 10) -> List[Dict[str, Any]]:
    """
    구글 뉴스에서 주제에 맞는 최신 뉴스 기사를 검색합니다.
    title, link, source, published를 반환합니다. (본문 미포함)
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [{"error": "❌ SERPER_API_KEY 환경변수가 설정되지 않았습니다."}]

    url = "https://google.serper.dev/news"
    headers = {"X-API-KEY": api_key}
    payload = {"q": query}

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        return [{"error": f"❌ 뉴스 검색 실패: {res.status_code}"}]

    articles = res.json().get("news", [])[:n_results]
    output: List[Dict[str, Any]] = []
    for article in articles:
        output.append({
            "title": article.get("title"),
            "link": article.get("link"),
            "source": article.get("source"),
            "published": article.get("date"),
        })
    return output

# ─────────────────────────────────────────────────────────────────────────────
# 3) 스크레이퍼들
#   — 모든 스크레이퍼는 (url, rss_pub) 시그니처를 갖고,
#     published_date는 rss_pub이 있으면 그것을 우선 사용합니다.
# ─────────────────────────────────────────────────────────────────────────────
def extract(url: str, rss_pub: Optional[str] = None) -> str:
    """기본 스크레이퍼(newspaper3k)"""
    try:
        cfg = Config()
        cfg.browser_user_agent = DEFAULT_HEADERS["User-Agent"]
        cfg.request_timeout = REQ_TIMEOUT

        article = Article(url, config=cfg)
        article.download()
        article.parse()

        result = {
            "title": article.title,
            "authors": article.authors,
            "published_date": rss_pub or (str(article.publish_date) if article.publish_date else None),
            "text": article.text,
            "url": url,
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"❌ 기사 추출 실패: {str(e)}"

def extract_fox(url: str, rss_pub: Optional[str] = None) -> str:
    """FOX 전용(UA + AMP 재시도)"""
    try:
        # 1) 기본 시도
        status, final_url, html = _requests_get_html(url)
        _polite_delay()
        if status == 200 and html and len(html) > 300:
            try:
                data = _newspaper_from_html(final_url or url, html)
                if len(data.get("text") or "") >= 400:
                    if rss_pub:
                        data["published_date"] = rss_pub
                    return json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                pass  # 아래 단계로

        # 2) AMP 변형 재시도
        if status in (401, 403, 406, 451) or (html and "Access Denied" in html) or (len(html or "") < 300):
            amp_url = _amp_variant(final_url or url)
            if amp_url:
                _polite_delay()
                status2, final_url2, html2 = _requests_get_html(amp_url)
                if status2 == 200 and html2 and len(html2) > 300:
                    try:
                        data = _newspaper_from_html(final_url2 or amp_url, html2)
                        if len(data.get("text") or "") >= 300:
                            if rss_pub:
                                data["published_date"] = rss_pub
                            return json.dumps(data, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

        # 3) 마지막 비상: newspaper 자체 download()
        try:
            cfg = Config()
            cfg.browser_user_agent = DEFAULT_HEADERS["User-Agent"]
            cfg.request_timeout = REQ_TIMEOUT
            article = Article(url, config=cfg)
            article.download()
            article.parse()
            result = {
                "title": article.title,
                "authors": article.authors,
                "published_date": rss_pub or (str(article.publish_date) if article.publish_date else None),
                "text": article.text,
                "url": url,
            }
            if len(result.get("text") or "") >= 300:
                return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception:
            pass

        return f"❌ 기사 추출 실패: (status={status}) {final_url or url}"
    except requests.RequestException as e:
        return f"❌ 네트워크 오류: {str(e)}"
    except Exception as e:
        return f"❌ 기사 추출 실패: {str(e)}"

def extract_nyt(url: str, rss_pub: Optional[str] = None) -> str:
    amp_url = _amp_variant(url)
    if amp_url:
        status, final_url, html = _requests_get_html(amp_url)
        if status == 200 and html and len(html) > 300:
            try:
                data = _newspaper_from_html(final_url or amp_url, html)
                if len(data.get("text") or "") >= 300:
                    if rss_pub:
                        data["published_date"] = rss_pub
                    return json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                pass
    return extract_firecrawl(url, rss_pub)

def extract_newsmax(url: str, rss_pub: Optional[str] = None) -> str:
    try:
        status, final_url, html = _requests_get_html(url)
        if status == 200 and html and len(html) > 300:
            data = _newspaper_from_html(final_url or url, html)
            if rss_pub:
                data["published_date"] = rss_pub
            return json.dumps(data, ensure_ascii=False, indent=2)
        amp_url = _amp_variant(url)
        if amp_url:
            status2, final_url2, html2 = _requests_get_html(amp_url)
            if status2 == 200 and html2 and len(html2) > 300:
                data = _newspaper_from_html(final_url2 or amp_url, html2)
                if rss_pub:
                    data["published_date"] = rss_pub
                return json.dumps(data, ensure_ascii=False, indent=2)
        return extract_firecrawl(url, rss_pub)
    except requests.RequestException:
        return extract_firecrawl(url, rss_pub)

def extract_france24(url: str, rss_pub: Optional[str] = None) -> str:
    amp_url = _amp_variant(url)
    if amp_url:
        status, final_url, html = _requests_get_html(amp_url)
        if status == 200 and html and len(html) > 300:
            try:
                data = _newspaper_from_html(final_url or amp_url, html)
                if len(data.get("text") or "") >= 300:
                    if rss_pub:
                        data["published_date"] = rss_pub
                    return json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                pass
    return extract_firecrawl(url, rss_pub)

def extract_firecrawl(url: str, rss_pub: Optional[str] = None) -> str:
    """
    newspaper3k / AMP 모두 실패했을 때, Playwright로 렌더링된 HTML을 직접 파싱합니다.
    날짜는 RSS에서 받은 rss_pub만 사용합니다(메타/DOM 파싱 비활성).
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            time.sleep(5)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")

        # --- 불필요 태그 제거 ---
        unwanted_tags = [
            "header", "footer", "nav", "aside", "script", "style", "noscript",
            "iframe", "form", "button", "input", "select", "textarea", "img",
            "svg", "canvas", "audio", "video", "embed", "object",
        ]
        for tag in soup.find_all(unwanted_tags):
            tag.decompose()

        # --- 메타데이터: author만 수집, 날짜는 rss_pub만 사용 ---
        author_candidates: List[str] = []
        for tag in soup.find_all("meta"):
            name = (tag.get("name") or "").lower()
            prop = (tag.get("property") or "").lower()
            content = (tag.get("content") or "").strip()
            if not content:
                continue
            if (name in ["author", "dc.creator"]) or ("author" in prop) or (prop in ["article:author", "og:article:author", "twitter:creator"]):
                author_candidates.append(content)
        # DOM 힌트 (author)
        for el in soup.select('[rel="author"], [itemprop="author"] [itemprop="name"]'):
            t = el.get_text(" ", strip=True)
            if t:
                author_candidates.append(t)

        title = (soup.title.string.strip() if soup.title and soup.title.string else None)
        authors = _normalize_authors(author_candidates)
        text = soup.get_text(separator=" ", strip=True)

        return json.dumps({
            "title": title,
            "authors": authors,
            "published_date": rss_pub,   # ← 핵심: 날짜는 RSS에서만
            "text": text[:20000],
            "url": url
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"❌ Firecrawl 실패: {str(e)}"

# ─────────────────────────────────────────────────────────────────────────────
# 3-1) 스크레이퍼 선택 (호출 시 rss_pub 함께 넘길 예정)
# ─────────────────────────────────────────────────────────────────────────────
def pick_scraper(url: str):
    host = urlparse(url).netloc.lower()
    if any(h in host for h in ["foxnews.com", "moxie.foxnews.com"]):
        return extract_fox
    if "nytimes.com" in host:
        return extract_nyt
    if "newsmax.com" in host:
        return extract_newsmax
    if "france24.com" in host:
        return extract_france24
    return extract

# ─────────────────────────────────────────────────────────────────────────────
# 4) fetch_scrape — RSS 여러 개 → 허브 필터 → 도메인별 스크레이퍼 병렬 크롤
# ─────────────────────────────────────────────────────────────────────────────
def fetch_scrape(feeds: List[str]) -> str:
    """
    입력: RSS feed URL 리스트
    출력: json.dumps({
       "requested": N,
       "success": len(articles),
       "failed": len(errors),
       "articles": [ {title, authors, published_date, text, url}, ... ],
       "errors": [ {"url","error"}, ... ]
    })
    """
    urls: List[str] = []
    rss_dates: Dict[str, str] = {}  # 정규화 URL -> pubDate 맵 (문자열 그대로 저장)

    # RSS에서 URL + pubDate 수집
    for feed in feeds:
        items = rss_articles(feed)
        for i in items:
            u = i.get("link")
            if u and not is_hub(u):
                urls.append(u)
                rss_pub = i.get("published") or i.get("updated") or i.get("pubDate")
                if rss_pub:
                    rss_dates[_norm_url(u)] = str(rss_pub)

    # URL 중복 제거
    seen, uniq_urls = set(), []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            uniq_urls.append(u)

    errors: List[dict] = []
    results: List[str] = []

    # 스크레이퍼 호출 시 rss_pub을 함께 전달
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {}
        for u in uniq_urls:
            scraper = pick_scraper(u)
            rss_pub = rss_dates.get(_norm_url(u))  # 문자열 그대로 전달
            fut = ex.submit(scraper, u, rss_pub)
            futures[fut] = u

        for fut in as_completed(futures):
            try:
                article = fut.result()
                results.append(article)
            except Exception as e:
                url = futures[fut]
                errors.append({"url": url, "error": str(e)})
                print(f"❌ {futures[fut]} 실패:", e)

    # JSON 파싱
    articles: List[dict] = []
    for s in results:
        try:
            articles.append(json.loads(s))
        except json.JSONDecodeError:
            articles.append({"_raw": s, "_error": "invalid json from scraper"})

    # 출처 태그만 정리 (이미 스크레이퍼 단계에서 rss_pub 반영)
    for art in articles:
        if not isinstance(art, dict):
            continue
        if art.get("published_date"):
            art["published_date_source"] = "rss"
        else:
            art["published_date_source"] = None

    return json.dumps({
        "requested": len(uniq_urls),
        "success": len(articles),
        "failed": len(errors),
        "articles": articles,
        "errors": errors
    }, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────────────────────
# 5) (선택) 저장 오케스트레이션 — persist와 결합
# ─────────────────────────────────────────────────────────────────────────────
# from services.persist import persist_outlets, persist_articles
#
# def fetch_scrape_and_persist(feeds: List[str], commit: bool = True) -> Dict[str, Any]:
#     fetched = json.loads(fetch_scrape(feeds))
#     res = {"fetched": int(fetched.get("success", 0))}
#     if commit:
#         arts = fetched.get("articles", [])
#         save = persist_articles(arts)
#         res.update(save)
#     return res

# ─────────────────────────────────────────────────────────────────────────────
# 6) 스모크 테스트
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    feeds = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.feedburner.com/dailycaller",
        "https://www.theepochtimes.com/us/us-politics/feed?_gl=1%2Ak929d7%2A_gcl_au%2AMTcyMDM2MDcyMy4xNzYwMTYwMzU1",
        "https://www.newsmax.com/rss/Newsfront/16/",
        "https://www.france24.com/en/rss",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://rss.dw.com/rdf/rss-en-all",
        "https://moxie.foxnews.com/google-publisher/latest.xml",
    ]
    out = fetch_scrape(feeds)
    obj = json.loads(out)
    print(f"✅ requested={obj['requested']} success={obj['success']} failed={obj['failed']}")
    # print(json.dumps(obj["articles"][:2], ensure_ascii=False, indent=2))
