# ────────────────────────────────
# CanonicalScraperTool (403 회피 강화판)
# ────────────────────────────────
import json
import re
import time
import random
from urllib.parse import urlparse, urlunparse
import requests
from newspaper import Article, Config
from crewai.tools import tool

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

REQ_TIMEOUT = 20

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

# @tool("CanonicalScraperTool")
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
