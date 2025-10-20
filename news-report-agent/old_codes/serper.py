# ────────────────────────────────
# GoogleNewsSearchTool (Serper 기반 뉴스 검색)
# ────────────────────────────────
import os
import json
import requests
from dotenv import load_dotenv
from crewai.tools import tool

# @tool("GoogleNewsSearchTool")
def search(query: str) -> str:
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

    # return json.dumps(output, indent=2, ensure_ascii=False)
    return output
