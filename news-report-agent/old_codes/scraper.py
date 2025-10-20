# ────────────────────────────────
# CanonicalScraperTool (newspaper4k 기반 본문+메타 추출)
# ────────────────────────────────
import json
from newspaper import Article
from crewai.tools import tool

# @tool("CanonicalScraperTool")
def extract(url: str) -> str:
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
