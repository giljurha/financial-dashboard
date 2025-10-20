# meta_test.py
import json
import time
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from services.fetch import rss_articles


# ─────────────────────────────────────────────────────────────────────────────
# Author 추출 헬퍼들
# ─────────────────────────────────────────────────────────────────────────────
def _parse_jsonld_authors(json_ld_objs) -> List[str]:
    """JSON-LD에서 author 후보만 수집 (Article/NewsArticle/BlogPosting 우선)"""
    names: List[str] = []

    def add_name(x):
        if not x:
            return
        if isinstance(x, str):
            s = x.strip()
            if s:
                names.append(s)
        elif isinstance(x, dict):
            # 가장 흔한 키 우선 사용
            n = x.get("name") or x.get("givenName") or x.get("familyName")
            if n:
                s = str(n).strip()
                if s:
                    names.append(s)
        elif isinstance(x, list):
            for y in x:
                add_name(y)

    def is_article_like(tval) -> bool:
        if not tval:
            return False
        if isinstance(tval, list):
            types = [str(v).lower() for v in tval]
        else:
            types = [str(tval).lower()]
        return any(tt in ("newsarticle", "article", "blogposting") for tt in types)

    # DFS 순회로 모든 중첩 객체에서 Article 계열을 탐색
    stack = [json_ld_objs]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if is_article_like(cur.get("@type") or cur.get("type")) and "author" in cur:
                add_name(cur["author"])
            for v in cur.values():
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            for v in cur:
                if isinstance(v, (dict, list)):
                    stack.append(v)

    # 중복/공백 제거
    uniq: List[str] = []
    seen = set()
    for n in names:
        k = n.strip()
        if k and k.lower() not in seen:
            uniq.append(k)
            seen.add(k.lower())
    return uniq


_AUTHOR_META_KEYS = {
    # 일반
    "author", "byline", "byl", "creator",
    # DC / DCTERMS
    "dc.creator", "dcterms.creator", "dc.contributor",
    # 소셜/플랫폼
    "article:author", "og:article:author", "twitter:creator",
    "parsely-author", "sailthru.author",
}


def _is_author_meta(tag) -> bool:
    """<meta>의 name/property/itemprop/http-equiv 중 author 관련만 필터"""
    def norm(s): return (s or "").strip().lower()
    keys = {
        norm(tag.get("name")),
        norm(tag.get("property")),
        norm(tag.get("itemprop")),
        norm(tag.get("http-equiv")),
    }
    return any(k in _AUTHOR_META_KEYS or k == "author" for k in keys)


def _extract_author_meta(soup: BeautifulSoup):
    out = []
    for m in soup.find_all("meta"):
        if _is_author_meta(m):
            out.append({
                "name": m.get("name"),
                "property": m.get("property"),
                "itemprop": m.get("itemprop"),
                "http_equiv": m.get("http-equiv"),
                "content": m.get("content"),
            })
    return out


def _has_byline_class(cls) -> bool:
    """
    class_ 인자가 str/list/None 다양한 형태로 들어올 수 있으므로 안전하게 검사
    """
    if not cls:
        return False
    if isinstance(cls, str):
        return "byline" in cls.lower()
    if isinstance(cls, (list, tuple, set)):
        joined = " ".join([c for c in cls if isinstance(c, str)])
        return "byline" in joined.lower()
    return False


def _extract_author_dom_texts(soup: BeautifulSoup) -> List[str]:
    """
    DOM에서 byline/author 힌트 추출
    - rel=author
    - itemprop=author (내부의 itemprop=name 포함)
    - class에 'byline' 포함
    """
    texts: List[str] = []

    # rel=author
    for a in soup.select('[rel="author"]'):
        t = a.get_text(" ", strip=True)
        if t:
            texts.append(t)

    # itemprop=author
    for el in soup.select('[itemprop="author"]'):
        # 중첩에 name이 있으면 name 우선
        name_el = el.find(attrs={"itemprop": "name"})
        t = (name_el.get_text(" ", strip=True) if name_el else el.get_text(" ", strip=True))
        if t:
            texts.append(t)

    # class에 byline 포함(대소문자 무시)
    for el in soup.find_all(class_=_has_byline_class):
        t = el.get_text(" ", strip=True)
        if t:
            texts.append(t)

    # 정제/중복 제거(길이 과도한 문장은 제외)
    cleaned, seen = [], set()
    for t in texts:
        t = t.strip()
        if not t or len(t) > 200:
            continue
        key = t.lower()
        if key not in seen:
            cleaned.append(t)
            seen.add(key)
    return cleaned


def _normalize_author_candidates(*lists: List[str]) -> List[str]:
    """여러 출처에서 모은 후보들을 합치고 흔한 접두사/접미사 정리"""
    import re
    raw: List[str] = []
    for L in lists:
        raw.extend(L or [])

    cleaned: List[str] = []
    for s in raw:
        x = s.strip()
        if not x:
            continue

        if x.startswith("@"):
            continue
        
        # 'By ', 'BY ' 제거
        x = re.sub(r'^\s*(by|BY)\s+', '', x).strip()
        # 한국어 관행 접미사 '기자' 제거
        x = re.sub(r'\s*기자$', '', x).strip()
        # 구두점 정리(양끝)
        x = re.sub(r'^[\-–—|·,:;\s]+|[\-–—|·,:;\s]+$', '', x).strip()
        if x and x not in cleaned:
            cleaned.append(x)
    return cleaned


# ─────────────────────────────────────────────────────────────────────────────
# 핵심: URL에서 '기자이름 관련 정보'만 뽑아 JSON으로 반환
# ─────────────────────────────────────────────────────────────────────────────
def extract_meta(url: str) -> str:
    """
    주어진 URL을 렌더링해 '기자이름' 관련 정보만 JSON으로 반환:
    - requested_url, final_url, title
    - authors: 추정 기자명 후보(중복 제거/정규화)
    - author_meta: <meta> 중 author 관련 상위 일부만 (디버그용)
    - hints: jsonld/dom/meta에서 각각 뽑힌 상위 일부 (디버그용)
    """
    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(1.5)  # 렌더 안정화
            final_url = page.url
            html = page.content()
    except Exception as e:
        # Playwright 단계에서의 예외
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        return f"❌ 메타 추출 실패(브라우저 단계): {str(e)}"
    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass

    try:
        soup = BeautifulSoup(html, "html.parser")

        # 제목(참고용)
        title = (soup.title.string.strip() if soup.title and soup.title.string else None)

        # (A) JSON-LD에서 author 후보
        json_ld_objs = []
        for s in soup.find_all("script", type="application/ld+json"):
            # 일부 사이트는 .string이 None일 수 있으므로 get_text 사용
            raw = (s.string or s.get_text() or "").strip()
            if not raw:
                continue
            try:
                json_ld_objs.append(json.loads(raw))
            except Exception:
                # 깨진 JSON-LD는 무시
                pass
        jsonld_authors = _parse_jsonld_authors(json_ld_objs)

        # (B) <meta>들 중 author 관련만
        author_meta = _extract_author_meta(soup)
        meta_authors = [m.get("content") for m in author_meta if m.get("content")]

        # (C) DOM(byline/rel=author/itemprop=author) 텍스트
        dom_authors = _extract_author_dom_texts(soup)

        # (D) 통합 후보 정규화
        authors = _normalize_author_candidates(jsonld_authors, meta_authors, dom_authors)

        payload = {
            "requested_url": url,
            "final_url": final_url,
            "title": title,
            "authors": authors,                # ✅ 최종 후보(중복 제거/정규화)
            "author_meta": author_meta[:6],    # ✅ 과출력 방지용 일부만
            "hints": {
                "jsonld": (jsonld_authors[:6] if jsonld_authors else []),
                "dom_byline": (dom_authors[:6] if dom_authors else []),
                "meta_contents": (meta_authors[:6] if meta_authors else []),
            },
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"❌ 메타 추출 실패(파싱 단계): {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# 실행부: RSS → 상위 N개 URL → author 메타 테스트
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 수집할 RSS 피드
    RSS_FEEDS = [
        "https://www.newsmax.com/rss/Newsfront/16/",
        "https://www.france24.com/en/rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    ]

    # 피드별로 상위 몇 개 기사만 테스트할지
    TOP_N_PER_FEED = 3

    # 1) RSS 피드 순회 → 기사 링크 수집
    urls = []
    for feed in RSS_FEEDS:
        try:
            items = rss_articles(feed)
            for it in items[:TOP_N_PER_FEED]:
                link = it.get("link")
                if link:
                    urls.append(link)
        except Exception as e:
            print(f"⚠️ RSS 파싱 실패: {feed} ({e})")

    # 2) 중복 제거(등장 순서 유지)
    seen, uniq_urls = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq_urls.append(u)

    # 3) 각 기사 URL 메타데이터(=기자이름 관련만) 추출
    for i, u in enumerate(uniq_urls, start=1):
        print(f"\n[{i}/{len(uniq_urls)}] Fetching author meta: {u}")
        out = extract_meta(u)
        print(out)
