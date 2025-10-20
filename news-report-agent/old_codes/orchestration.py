from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools.rss import rss_articles
from tools.serper import search
from tools.scraper import extract
from tools.scraper_fox import extract_fox
from crewai.tools import tool
import json

REJECT_PATHS = ["/tag/", "/topic/", "/hub/", "/section/", "/category/"]

# REJECT_PATHS의 문자열들이 포함되었는지 판별별
def is_hub(url: str) -> bool:
    return any(p in url.lower() for p in REJECT_PATHS)

# fox_news인지 판별
def pick_scraper(url: str):
    host = urlparse(url).netloc.lower()
    if "foxnews.com" in host or "moxie.foxnews.com" in host:
        return extract_fox
    return extract

# @tool("fetch_scrape")
def fetch_scrape(feeds):
    urls = []
    for feed in feeds:
        items = rss_articles(feed)
        for i in items:
            u = i.get("link")
            if u and not is_hub(u):
                urls.append(u)

    errors = []
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:                       # 작업반장
        futures = {ex.submit(pick_scraper(u), u): u for u in urls}      # 작업 제출: 즉시 Future(나중에 끝나면 결과를 약속하는 영수증) 반환
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

    return json.dumps({
        "requested": len(urls),
        "success": len(articles),
        "failed": len(errors),
        "articles": articles,
        "errors": errors
    }, ensure_ascii=False)

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
    articles = fetch_scrape(feeds)
    print(f"✅ 총 {len(articles)}개 기사 긁음")
    print(articles)

# 내부 서비스(비-@tool)
def persist_articles(articles: list[dict]) -> dict:
    # upsert 구현 (canonical_url/url unique, body hash 비교 등)
    return {"inserted": i, "updated": u, "skipped": s}



