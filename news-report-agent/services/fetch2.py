# services/fetch.py — RSS/검색/스크레이퍼/오케스트레이션 통합 모듈

from __future__ import annotations

# Standard library
import hashlib
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Third-party
from dotenv import load_dotenv
import feedparser
import requests
from newspaper import Article, Config

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re, time, json


# (선택) .env 로드 위치는 앱 엔트리에서 하는 걸 권장하지만,
# 필요하면 아래 주석 해제
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# 0) 공통 상수/유틸
# ─────────────────────────────────────────────────────────────────────────────
REJECT_PATHS = ["/tag/", "/topic/", "/hub/", "/section/", "/category/"]

def is_hub(url: str) -> bool:
    """허브/토픽 인덱스 페이지 판별"""
    return any(p in url.lower() for p in REJECT_PATHS)

def _extract_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host

# FOX 전용 스크레이퍼 선택
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

def _amp_variant(url: str) -> str | None:
    """
    가능하면 AMP URL로 변환 (폭스 등 다수 매체가 /amp 지원).
    """
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

def _requests_get_html(url: str, headers: dict | None = None, timeout: int = REQ_TIMEOUT) -> tuple[int, str | None, str]:
    """
    단순 requests GET로 HTML을 가져온다. (리다이렉트 따라감)
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
    """
    이미 확보한 HTML을 newspaper로 파싱.
    """
    cfg = Config()
    cfg.browser_user_agent = DEFAULT_HEADERS["User-Agent"]
    cfg.request_timeout = REQ_TIMEOUT
    article = Article(url=url, config=cfg)
    article.set_html(html)
    article.parse()

    result = {
        "title": article.title,
        "authors": article.authors,
        "published_date": str(article.publish_date) if article.publish_date else None,
        "text": article.text,
        "url": url
    }
    return result

def _polite_delay():
    time.sleep(0.6 + random.random() * 0.6)


def _normalize_authors(cands: list[str]) -> list[str]:
    import re
    out, seen = [], set()
    for s in cands:
        x = (s or "").strip()
        if not x:
            continue
        # 잡음 제거
        if x.startswith("@"):            # 트위터 핸들 제거
            continue
        if x.startswith("http://") or x.startswith("https://"):  # URL 값 제거(France24 페북 등)
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


# ─────────────────────────────────────────────────────────────────────────────
# 1) RSS 수집기  (여기에 tools/rss.py의 핵심 로직을 "함수 본문"만" 붙여 넣기)
#    예: def rss_articles(feed_url: str) -> List[dict]: ...
# ─────────────────────────────────────────────────────────────────────────────
def rss_articles(feed_url: str) -> List[dict]:
    """
    TODO: tools/rss.py의 구현을 이 함수 안에 그대로 옮겨오세요.
    반환: RSS 한 개의 feed에서 기사 항목(dict) 목록
    각 항목엔 최소 'link' 키가 있어야 함.
    """
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:10]:  # 상위 10개만
        articles.append({
            "title": entry.get("title"),
            "link": entry.get("link"),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", "")
        })

    return articles

# ─────────────────────────────────────────────────────────────────────────────
# 2) 검색(Serper)  (여기에 tools/serper.py의 함수 본문 옮기기)
# ─────────────────────────────────────────────────────────────────────────────
def search(query: str, *, n_results: int = 10) -> List[str]:
    """
    구글 뉴스에서 주제에 맞는 최신 뉴스 기사를 검색합니다. 
    이 도구는 뉴스기사의 title, link, source, published만 반환하고, 본문은 포함하지 않습니다.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "❌ SERPER_API_KEY 환경변수가 설정되지 않았습니다."

    # 엔드포인트와 담아 보낼 정보
    url = "https://google.serper.dev/news"
    headers = {"X-API-KEY": api_key}
    payload = {"q": query}

    # 요청보내기
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        return f"❌ 뉴스 검색 실패: {res.status_code}"

    articles = res.json().get("news", [])
    output = []

    for article in articles:
        output.append({
            "title": article.get("title"),
            "link": article.get("link"),
            "source": article.get("source"),
            "published": article.get("date")
        })

    return output
# ─────────────────────────────────────────────────────────────────────────────
# 3) 스크레이퍼들  (여기에 tools/scraper.py, tools/scraper_fox.py 모두 옮기기)
#    두 함수 모두 "같은 반환 스펙"을 유지: JSON 문자열(dict를 json.dumps 한 것)
# ─────────────────────────────────────────────────────────────────────────────
def extract(url: str) -> str:
    """
    기사 URL에서 본문과 메타데이터를 추출합니다.
    """
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
            "published_date": str(article.publish_date) if article.publish_date else None,
            "text": article.text,
            "url": url
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"❌ 기사 추출 실패: {str(e)}"


def extract_fox(url: str) -> str:
    """
    기사 URL에서 본문과 메타데이터를 추출합니다.
    1) 커스텀 UA로 직접 GET → set_html(parse)
    2) 403/406 등 거절 시 AMP 변형으로 재시도
    3) (옵션) 마지막에 newspaper.download()도 짧게 시도
    """
    try:
        # 1) 기본 시도
        status, final_url, html = _requests_get_html(url)
        _polite_delay()
        if status == 200 and html and len(html) > 300:
            try:
                data = _newspaper_from_html(final_url or url, html)
                # 본문이 너무 짧으면(광고/목차 등) AMP로 재시도
                if len(data.get("text") or "") >= 400:
                    return json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                pass  # 아래 단계로

        # 2) AMP 변형 재시도 (403/406/451/redirect 루프 등)
        if status in (401, 403, 406, 451) or (html and "Access Denied" in html) or (len(html or "") < 300):
            amp_url = _amp_variant(final_url or url)
            if amp_url:
                _polite_delay()
                status2, final_url2, html2 = _requests_get_html(amp_url)
                if status2 == 200 and html2 and len(html2) > 300:
                    try:
                        data = _newspaper_from_html(final_url2 or amp_url, html2)
                        if len(data.get("text") or "") >= 300:  # AMP는 본문이 잘 나오는 편
                            return json.dumps(data, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

        # 3) 마지막 비상: newspaper 자체 download() (간혹 성공)
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
                "published_date": str(article.publish_date) if article.publish_date else None,
                "text": article.text,
                "url": url
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


def extract_nyt(url: str) -> str:
    amp_url = _amp_variant(url)
    if amp_url:
        status, final_url, html = _requests_get_html(amp_url)
        if status == 200 and html and len(html) > 300:
            try:
                data = _newspaper_from_html(final_url or amp_url, html)
                if len(data.get("text") or "") >= 300:
                    return json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                pass
    return extract_firecrawl(url)


def extract_newsmax(url: str) -> str:
    try:
        status, final_url, html = _requests_get_html(url)
        if status == 200 and html and len(html) > 300:
            return json.dumps(_newspaper_from_html(final_url or url, html), ensure_ascii=False, indent=2)
        amp_url = _amp_variant(url)
        if amp_url:
            status2, final_url2, html2 = _requests_get_html(amp_url)
            if status2 == 200 and html2 and len(html2) > 300:
                return json.dumps(_newspaper_from_html(final_url2 or amp_url, html2), ensure_ascii=False, indent=2)
        return extract_firecrawl(url)
    except requests.RequestException as e:
        return extract_firecrawl(url)


def extract_france24(url: str) -> str:
    amp_url = _amp_variant(url)
    if amp_url:
        status, final_url, html = _requests_get_html(amp_url)
        if status == 200 and html and len(html) > 300:
            try:
                data = _newspaper_from_html(final_url or amp_url, html)
                if len(data.get("text") or "") >= 300:
                    return json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                pass
    return extract_firecrawl(url)

# def extract_firecrawl(url: str) -> str:
#     """
#     newspaper3k / AMP 모두 실패했을 때, Playwright로 렌더링된 HTML을 직접 파싱합니다.
#     """
#     try:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             page = browser.new_page()
#             page.goto(url, timeout=60000)
#             time.sleep(5)
#             html = page.content()
#             browser.close()

#         soup = BeautifulSoup(html, "html.parser")

#         # 불필요한 영역 제거
#         unwanted_tags = [
#             "header", "footer", "nav", "aside", "script", "style", "noscript",
#             "iframe", "form", "button", "input", "select", "textarea", "img",
#             "svg", "canvas", "audio", "video", "embed", "object",
#         ]
#         for tag in soup.find_all(unwanted_tags):
#             tag.decompose()

#         text = soup.get_text(separator=" ", strip=True)
#         return json.dumps({
#             "title": soup.title.string if soup.title else None,
#             "text": text[:20000],  # 혹시 너무 길면 제한
#             "url": url
#         }, ensure_ascii=False, indent=2)

#     except Exception as e:
#         return f"❌ Firecrawl 실패: {str(e)}"

def extract_firecrawl(url: str) -> str:
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

        # --- 메타데이터 추출 ---
        author_candidates = []   # ✅ 단일 author 대신 후보 리스트로 변경
        date = None

        # 1) <meta>에서 author/date 후보 수집
        for tag in soup.find_all("meta"):
            name = (tag.get("name") or "").lower()
            prop = (tag.get("property") or "").lower()
            content = (tag.get("content") or "").strip()
            if not content:
                continue

            # author 관련 메타 전부 후보로 수집
            if (name in ["author", "dc.creator"]) or ("author" in prop) or (prop in ["article:author", "og:article:author", "twitter:creator"]):
                author_candidates.append(content)

            # 날짜는 첫 값만 채택
            # if ("publish" in name) or ("publish" in prop) or ("date" in name):
            #     if not date:
            #         date = content

        # 2) <time> 태그로 날짜 보완
        # if not date:
        #     t = soup.find("time")
        #     if t and (t.get("datetime") or t.text.strip()):
        #         date = t.get("datetime") or t.text.strip()

        # 3) ✅ 여기! DOM 힌트 추가(질문 1번의 코드)
        # rel=author, itemprop=author 안의 name
        for el in soup.select('[rel="author"], [itemprop="author"] [itemprop="name"]'):
            t = el.get_text(" ", strip=True)
            if t:
                author_candidates.append(t)

        text = soup.get_text(separator=" ", strip=True)
        title = (soup.title.string.strip() if soup.title and soup.title.string else None)
        authors = _normalize_authors(author_candidates)

        return json.dumps({
            "title": title,
            "authors": authors, 
            "published_date": date,
            "text": text[:20000],
            "url": url
        }, ensure_ascii=False, indent=2)

        # return text

    except Exception as e:
        return f"❌ Firecrawl 실패: {str(e)}"




# ─────────────────────────────────────────────────────────────────────────────
# 4) fetch_scrape — RSS 여러 개 → 허브 필터 → 도메인별 스크레이퍼 병렬 크롤
#    (tools/orchestration.py 의 fetch_scrape 본문을 이쪽으로 이전)
# ─────────────────────────────────────────────────────────────────────────────
# @tool("fetch_scrape")
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
    urls = []
    rss_dates = {}  # ⬅️ 추가: 정규화 URL -> pubDate 맵

    # 메타데이터 사용
    # for feed in feeds:
    #     items = rss_articles(feed)
    #     for i in items:
    #         u = i.get("link")
    #         if u and not is_hub(u):
    #             urls.append(u)

    #             # ⬇️ RSS 발행일 우선 수집 (여러 필드 대비)
    #             rss_pub = (
    #                 i.get("published")
    #                 or i.get("updated")
    #                 or i.get("pubDate")
    #             )
    #             if rss_pub:
    #                 rss_dates[_norm_url(u)] = rss_pub

    # 메타데이터 미사용용
    for feed in feeds:
        items = rss_articles(feed)
        for i in items:
            u = i.get("link")
            if u and not is_hub(u):
                urls.append(u)
                # ⬇️ RSS의 날짜 문자열을 그대로 저장 (published/updated/pubDate 우선순위)
                rss_pub = i.get("published") or i.get("updated") or i.get("pubDate")
                if rss_pub:
                    rss_dates[_norm_url(u)] = rss_pub

    # url 중복 제거 로직
    # urls = [...] 수집 끝난 직후에 추가
    seen, uniq_urls = set(), []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            uniq_urls.append(u)

    errors = []
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:                       # 작업반장
        futures = {ex.submit(pick_scraper(u), u): u for u in uniq_urls}      # 작업 제출: 즉시 Future(나중에 끝나면 결과를 약속하는 영수증) 반환
        for fut in as_completed(futures):                               # 끝난 순서대로 Future을 뽑아줌
            try:
                article = fut.result()
                results.append(article)
            except Exception as e:
                url = futures[fut]
                errors.append({"url": url, "error": str(e)})
                print(f"❌ {futures[fut]} 실패:", e)


    # results에 든 JSON 모양의 문자열들 → 전부 파이썬 객체로 바꾼다.
    # 그걸 한 **리스트(articles)**에 담는다.
    # 그 리스트를 {"count": N, "articles": [...]} 형태로 다시 하나의 JSON 문자열로 만들어 반환한다.
    articles = []
    for s in results:
        try:
            articles.append(json.loads(s))
        except json.JSONDecodeError:
            # 혹시 스크레이퍼가 잘못된 문자열을 준 경우 방어
            articles.append({"_raw": s, "_error": "invalid json from scraper"})
    
    # ⬇️ 추가: RSS pubDate로 발행일 보정
    for art in articles:
        if not isinstance(art, dict):
            continue
        # 스크레이퍼가 url을 항상 넣으므로 이를 기준으로 매핑
        url_key = _norm_url(art.get("canonical_url") or art.get("url"))
        rss_pub = rss_dates.get(url_key)
        if rss_pub:
            art["published_date"] = rss_pub
            art["published_date_source"] = "rss"   # (옵션) 추적용
        else:
            # (옵션) 메타를 썼다면 출처 태그만 남겨두기
            if art.get("published_date"):
                art["published_date_source"] = "meta"

        # url_key = _norm_url(art.get("url"))
        # rss_pub = rss_dates.get(url_key)

        # 1) 스크레이퍼 발행일이 없거나, 이상한 값(예: URL 같은 것)이면 RSS로 대체
        bad_date = None
        pd = art.get("published_date")
        if not pd:
            bad_date = True
        else:
            # 페북/HTTP 링크 같은 비정상 값 필터
            if isinstance(pd, str) and pd.strip().lower().startswith(("http://", "https://")):
                bad_date = True

        if bad_date and rss_pub:
            art["published_date"] = rss_pub

    return json.dumps({
        "requested": len(uniq_urls),
        "success": len(articles),
        "failed": len(errors),
        "articles": articles,
        "errors": errors
    }, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────────────────────
# 5) (선택) 저장 오케스트레이션 — persist와 결합
#    services/persist.py의 함수들을 가져와 연결하고 싶다면 아래 주석 해제
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

