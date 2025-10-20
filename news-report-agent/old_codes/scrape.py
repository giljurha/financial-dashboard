# ────────────────────────────────
# scrape_tool (동적 렌더링 포함 본문 텍스트 추출)
# ────────────────────────────────
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from crewai.tools import tool  # CrewAI의 @tool
from crewai_tools import SerperDevTool

# ────────────────────────────────
# 3. scrape_tool (기사 본문 수집)
# ────────────────────────────────

search_tool = SerperDevTool(
    n_results=10,
)


# @tool
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