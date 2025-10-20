# tests/quick_firecrawl_test.py
from services.fetch import rss_articles, extract_firecrawl

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    # "https://feeds.feedburner.com/dailycaller",
    # "https://www.theepochtimes.com/us/us-politics/feed?_gl=1%2Ak929d7%2A_gcl_au%2AMTcyMDM2MDcyMy4xNzYwMTYwMzU1",
    "https://www.newsmax.com/rss/Newsfront/16/",
    "https://www.france24.com/en/rss",
    # "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    # "https://rss.dw.com/rdf/rss-en-all",
    # "https://moxie.foxnews.com/google-publisher/latest.xml",
]

if __name__ == "__main__":
    for url in RSS_FEEDS:
        items = rss_articles(url)
        for i, it in enumerate(items[:3], start=1):  # 상위 3개만
            url = it["link"]
            print(f"\n[{i}] {url}")
            print(extract_firecrawl(url))
        # for item in items:
        #     print(item)
