# tests/smoke_orchestrate.py
import json
from services.orchestrator import fetch_scrape_upsert

# ⬇️ 추가: 부분 커밋용으로 기사 원본을 직접 가져와서 1~3개만 저장
from services.fetch import fetch_scrape, extract_firecrawl
from services.persist import persist_articles

# RSS 피드 목록 — 전 세계 주요 뉴스
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

# 오케스트레이터와 동일한 최소 품질 가드(본문 길이 기준)
def good(a: dict) -> bool:
    # 제목/URL 필수, 본문은 비어있지 않은 경우에만 허용(짧아도 OK)
    if not a.get("url") or not a.get("title"):
        return False
    txt = (a.get("text") or "").strip()
    return len(txt) > 300


if __name__ == "__main__":
    # ① 드라이런 모드 (DB 저장 안 함) — 전체 파이프라인 메트릭 확인
    result_dry = fetch_scrape_upsert(
        rss_feeds=RSS_FEEDS,
        batch_limit=10_000,
        commit=False
    )
    print("🧪 [Dry Run]")
    print(json.dumps(result_dry, ensure_ascii=False, indent=2))

    # ② 부분 커밋: good 함수를 통과한 기사들만 저장
    print("\n💾 [Full Commit] 품질 필터링된 기사 저장 테스트")
    fetched_json = fetch_scrape(RSS_FEEDS)       # 기사 원본 리스트 직접 확보
    fetched = json.loads(fetched_json)
    all_articles = fetched.get("articles", [])
    
    # good 함수를 통과한 기사들만 필터링
    articles = [a for a in all_articles if good(a)]
    print(f"📊 전체 기사: {len(all_articles)}개 → 품질 필터링 후: {len(articles)}개")


    if not articles:
        print("⚠️ 커밋할 기사가 없습니다.")
    else:
        result_commit = persist_articles(articles)
        report = {
            "total_size": len(articles),
            **result_commit,   # processed/inserted/updated/skipped/errors
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))

        print("\n✅ 저장 시도한 타이틀:")
        for a in articles:
            print("   •", a.get("title"))

# if __name__ == "__main__":
#     for url in RSS_FEEDS:
#         print(extract_firecrawl(url))
#         print("-" * 100)
