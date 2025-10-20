# services/orchestrator.py
from typing import List, Dict, Any
import json, time
from services.fetch import fetch_scrape
from services.persist import persist_articles

def fetch_scrape_upsert(
    rss_feeds: List[str],
    batch_limit: int = 10_000,   # (지금은 fetch에서 안 쓰지만, 남겨도 무방)
    commit: bool = True,
) -> Dict[str, Any]:
    t0 = time.time()

    # fetch_scrape는 JSON 문자열을 반환하므로 파싱
    fetched_json = fetch_scrape(rss_feeds)
    fetched = json.loads(fetched_json)
    articles = fetched.get("articles", [])

    # 2차 정제: 최소 요건(제목/URL/본문 길이)만 체크
    def good(a: Dict[str, Any]) -> bool:
        if not a.get("url") or not a.get("title"):
            return False
        txt = (a.get("text") or "").strip()
        if len(txt) < 300:
            return False
        return True

    cleaned = [a for a in articles if good(a)]
    not_cleaned = [a for a in articles if not good(a)]


    if not commit:
        return {
            "fetched": len(articles),
            "cleaned": len(cleaned),
            "inserted": 0,
            "updated": 0,
            "skipped": len(articles) - len(cleaned),
            "errors": fetched.get("errors", []),
            "elapsed_sec": round(time.time() - t0, 2),
            "dry_run": True,
            # "sample": cleaned[:3],
            "sample": cleaned,
            # "sample": not_cleaned,
        }

    # DB upsert
    result = persist_articles(cleaned)
    result |= {
        "fetched": len(articles),
        "cleaned": len(cleaned),
        "errors": fetched.get("errors", []),
        "elapsed_sec": round(time.time() - t0, 2),
        "dry_run": False,
    }
    return result
