# ────────────────────────────────
# RSSFeedCollectorTool (RSS 피드 수집기)
# ────────────────────────────────
import json
import feedparser
from crewai.tools import tool

# @tool("RSSFeedCollectorTool")
def rss_articles(feed_url: str) -> str:
    """
    RSS 피드를 통해 기사 목록을 수집합니다.
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

    # return json.dumps(articles, indent=2, ensure_ascii=False)
    return articles

# 테스트
# result = fetch_rss_articles("https://feeds.bbci.co.uk/news/world/rss.xml")
# print(type(result))