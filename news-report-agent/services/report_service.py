# services/report_service.py
# ──────────────────────────────────────────────
# 📝 사건 리포트 저장 및 포맷팅 서비스
# ──────────────────────────────────────────────

from datetime import datetime
from typing import Optional
import markdown
from models import Report
from services import db_service


def format_report_markdown(event_summary: str,
                           topic_tags: list[str],
                           articles: list[dict],
                           effects: Optional[list[dict]] = None) -> str:
    """
    사건 요약, 주요 태그, 기사 출처, 경제적 영향 등을 Markdown 형태로 렌더링.
    """
    md = []
    md.append(f"# 📰 {event_summary}\n")

    if topic_tags:
        tags_str = ", ".join([f"`{tag}`" for tag in topic_tags])
        md.append(f"**Topics:** {tags_str}\n")

    if articles:
        md.append("## 🗂️ Related Articles\n")
        for a in articles:
            title = a.get("title", "")
            url = a.get("url", "")
            outlet = a.get("outlet", "")
            md.append(f"- [{title}]({url}) ({outlet})")

    if effects:
        md.append("\n## 📈 Economic / Political Impact\n")
        for e in effects:
            asset = e.get("asset")
            direction = e.get("direction")
            magnitude = e.get("magnitude")
            conf = e.get("confidence")
            md.append(f"- **{asset}** likely to move **{direction}** "
                      f"(impact: {magnitude}, confidence: {conf})")

    md.append(f"\n\n_Last updated: {datetime.utcnow().isoformat()} UTC_")
    return "\n".join(md)


def save_report(event_id: int, content: str, format: str = "md", version: int = 1) -> int:
    """
    생성된 리포트를 DB에 저장.
    """
    report = Report(
        event_id=event_id,
        format=format,
        version=version,
        content=content,
        created_at=datetime.utcnow(),
    )
    return db_service.insert_report(report)


def convert_markdown_to_html(md_text: str) -> str:
    """
    Markdown → HTML 변환 (간단한 웹 뷰어용)
    """
    return markdown.markdown(md_text, extensions=["fenced_code", "tables", "toc"])


def get_latest_report(event_id: int) -> Optional[dict]:
    """
    DB에서 가장 최신 리포트를 가져옴.
    """
    sql = """
    SELECT id, content, format, version, created_at
    FROM reports
    WHERE event_id = %s
    ORDER BY version DESC, created_at DESC
    LIMIT 1;
    """
    with db_service.get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (event_id,))
        row = cur.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "content": row[1],
        "format": row[2],
        "version": row[3],
        "created_at": row[4],
    }
