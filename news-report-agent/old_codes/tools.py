# ────────────────────────────────
# 🧩 표준 라이브러리
# ────────────────────────────────
import os
import json
import time
import hashlib
from datetime import datetime

# ────────────────────────────────
# 🌐 외부 라이브러리
# ────────────────────────────────
import requests
import feedparser
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI
from playwright.sync_api import sync_playwright

# CrewAI 관련
from crewai.tools import tool
from crewai_tools import SerperDevTool

# ────────────────────────────────
# 🧱 내부 모듈 (프로젝트 모듈)
# ────────────────────────────────
from services import db_services
from models import Article, ArticleEmbedding



# ────────────────────────────────
# 1️. GoogleNewsSearchTool (Serper 기반 뉴스 검색)
# ────────────────────────────────
# @tool("GoogleNewsSearchTool")
def search_news_with_serper(query: str) -> str:
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

    return json.dumps(output, indent=2, ensure_ascii=False)

# # 테스트
# result = search_news_with_serper("Donald Trump")
# print(type(result))
# print("-" * 50)

# ────────────────────────────────
# 2. RSSFeedCollectorTool (RSS 피드 수집기)
# ────────────────────────────────
# @tool("RSSFeedCollectorTool")
def fetch_rss_articles(feed_url: str) -> str:
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

    return json.dumps(articles, indent=2, ensure_ascii=False)

# 테스트
result = fetch_rss_articles("https://feeds.bbci.co.uk/news/world/rss.xml")
print(type(result))

# ────────────────────────────────
# 3. scrape_tool (기사 본문 수집)
# ────────────────────────────────

search_tool = SerperDevTool(
    n_results=10,
)


@tool
def scrape_tool(url: str):
    """
    웹사이트의 내용을 읽어야 할 때 사용하세요.
    웹사이트에 접속할 수 없는 경우 "No content"(콘텐츠 없음)을 반환합니다.
    입력값은 url 문자열이어야 합니다.
    예시: https://www.reuters.com/world/asia-pacific/cambodia-thailand-begin-talks-malaysia-amid-fragile-ceasefire-2025-08-04/
    """

    print(f"Scrapping URL: {url}")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(url)

        time.sleep(5)

        html = page.content()

        browser.close()

        soup = BeautifulSoup(html, "html.parser")

        unwanted_tags = [
            "header",
            "footer",
            "nav",
            "aside",
            "script",
            "style",
            "noscript",
            "iframe",
            "form",
            "button",
            "input",
            "select",
            "textarea",
            "img",
            "svg",
            "canvas",
            "audio",
            "video",
            "embed",
            "object",
        ]

        for tag in soup.find_all(unwanted_tags):
            tag.decompose()

        content = soup.get_text(separator=" ")

        return content if content != "" else "No content"

# ────────────────────────────────
# 3. CanonicalScraperTool (기사 본문 + 메타데이터 추출기)
# ────────────────────────────────
@tool("CanonicalScraperTool")
def extract_article_content(url: str) -> str:
    """
    기사 URL에서 본문과 메타데이터를 추출합니다.
    """
    try:
        article = Article(url)
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







# # ────────────────────────────────
# # 0️⃣ 기본 설정
# # ────────────────────────────────
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)
# 
# # ────────────────────────────────
# # 1️⃣ 웹 기사 스크래핑 도구
# # ────────────────────────────────
# @tool
# def scrape_article(url: str) -> str:
#     """
#     웹페이지의 본문 텍스트를 추출한다.
#     - 광고, 메뉴, 댓글 등을 제외하고 <p> 태그 중심으로 본문만 모은다.
#     - 실패 시 빈 문자열을 반환한다.
#     """
#     try:
#         res = requests.get(url, timeout=10)
#         res.raise_for_status()
#         soup = BeautifulSoup(res.text, "html.parser")

#         paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
#         body = "\n".join(p for p in paragraphs if len(p) > 50)  # 짧은 문장은 제외
#         return body
#     except Exception as e:
#         print(f"[scrape_article] Error fetching {url}: {e}")
#         return ""


# # ────────────────────────────────
# # 2️⃣ 임베딩 생성 도구
# # ────────────────────────────────
# @tool
# def generate_embedding(article_id: int, text: str, model: str = "text-embedding-3-small"):
#     """
#     기사 본문을 OpenAI Embedding으로 변환하고 DB에 저장한다.
#     """
#     try:
#         response = client.embeddings.create(model=model, input=text)
#         vector = response.data[0].embedding

#         emb = ArticleEmbedding(article_id=article_id, model=model, dim=len(vector), embedding=vector)
#         db_service.upsert_embedding(emb)

#         return {"article_id": article_id, "embedding_dim": len(vector), "model": model}
#     except Exception as e:
#         print(f"[generate_embedding] Error: {e}")
#         return {"error": str(e)}


# # ────────────────────────────────
# # 3️⃣ 뉴스 기사 저장 도구
# # ────────────────────────────────
# @tool
# def save_article(outlet_name: str, outlet_domain: str, country_code: str, title: str, url: str, body: str, published_at: str = None, language: str = "en"):
#     """
#     기사 정보를 DB에 저장한다.
#     - outlet이 없으면 새로 생성
#     - article은 url 중복 시 upsert
#     """
#     try:
#         outlet_id = db_service.upsert_outlet(
#             Article.Outlet(name=outlet_name, domain=outlet_domain, country_code=country_code)
#         ) if hasattr(Article, "Outlet") else db_service.upsert_outlet(
#             type("Outlet", (), {"name": outlet_name, "domain": outlet_domain, "country_code": country_code})()
#         )

#         hash_sha256 = hashlib.sha256((title + url).encode()).hexdigest()
#         article = Article(
#             outlet_id=outlet_id,
#             url=url,
#             title=title,
#             body=body,
#             language=language,
#             published_at=datetime.fromisoformat(published_at) if published_at else None,
#             hash_sha256=hash_sha256,
#         )

#         inserted_ids = db_service.upsert_articles([article])
#         return {"inserted_id": inserted_ids[0], "url": url}
#     except Exception as e:
#         print(f"[save_article] Error saving article: {e}")
#         return {"error": str(e)}


# # ────────────────────────────────
# # 4️⃣ 기사 유사도 검색 (선택)
# # ────────────────────────────────
# @tool
# def search_similar_articles(query_text: str, top_k: int = 5, model: str = "text-embedding-3-small"):
#     """
#     주어진 텍스트를 임베딩하고, DB 내 기사들과 유사도 기반 검색 수행.
#     (pgvector cosine similarity)
#     """
#     try:
#         response = client.embeddings.create(model=model, input=query_text)
#         vector = response.data[0].embedding

#         sql = """
#         SELECT a.id, a.title, a.url, 1 - (aemb.embedding <=> %s::vector) AS similarity
#         FROM article_embeddings aemb
#         JOIN articles a ON a.id = aemb.article_id
#         ORDER BY aemb.embedding <=> %s::vector
#         LIMIT %s;
#         """

#         with db_service.get_conn() as conn, conn.cursor() as cur:
#             cur.execute(sql, (vector, vector, top_k))
#             rows = cur.fetchall()

#         return [{"id": r[0], "title": r[1], "url": r[2], "similarity": float(r[3])} for r in rows]
#     except Exception as e:
#         print(f"[search_similar_articles] Error: {e}")
#         return {"error": str(e)}
