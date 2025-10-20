# services/db_service.py
import os
import psycopg2
from psycopg2.extras import execute_batch
from typing import Iterable, List, Optional, Dict, Any
from datetime import datetime
from models import Article, Outlet, Event, Report, ArticleEmbedding

# 👇 추가
from dotenv import load_dotenv
load_dotenv()

# ────────────────────────────────
# DB 연결 설정
# ────────────────────────────────
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:1234@localhost:5432/appdb")

def get_conn():
    return psycopg2.connect(POSTGRES_URL)

# ────────────────────────────────
# 1️⃣ Outlets (언론사)
# ────────────────────────────────
def upsert_outlet(outlet: Outlet) -> int:
    """
    outlet: Outlet 모델 (name, domain, country_code)
    동일 domain 있으면 update, 없으면 insert.
    """
    sql = """
    INSERT INTO outlets (name, domain, country_code)
    VALUES (%s, %s, %s)
    ON CONFLICT (domain) DO UPDATE
    SET name = EXCLUDED.name,
        country_code = COALESCE(EXCLUDED.country_code, outlets.country_code)
    RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (outlet.name, outlet.domain, outlet.country_code))
        outlet_id = cur.fetchone()[0]
    return outlet_id

# ────────────────────────────────
# 2️⃣ Articles (기사)
# ────────────────────────────────
def upsert_articles(articles: Iterable[Article]) -> List[int]:
    """
    여러 Article 객체를 INSERT/UPDATE (url 기준)
    """
    sql = """
    INSERT INTO articles (
        outlet_id, url, title, published_at, language,
        author, body, canonical_url, hash_sha256
    )
    VALUES (
        %(outlet_id)s, %(url)s, %(title)s, %(published_at)s, %(language)s,
        %(author)s, %(body)s, %(canonical_url)s, %(hash_sha256)s
    )
    ON CONFLICT (url) DO UPDATE SET
        title = EXCLUDED.title,
        body = COALESCE(EXCLUDED.body, articles.body),
        author = COALESCE(EXCLUDED.author, articles.author),
        published_at = COALESCE(EXCLUDED.published_at, articles.published_at),
        hash_sha256 = COALESCE(EXCLUDED.hash_sha256, articles.hash_sha256),
        fetched_at = now()
    RETURNING id;
    """
    inserted_ids = []
    with get_conn() as conn, conn.cursor() as cur:
        for a in articles:
            cur.execute(sql, a.model_dump())
            inserted_ids.append(cur.fetchone()[0])
    return inserted_ids

# ────────────────────────────────
# 3️⃣ Article Embeddings (벡터)
# ────────────────────────────────
def upsert_embedding(embed: ArticleEmbedding) -> None:
    sql = """
    INSERT INTO article_embeddings (article_id, model, dim, embedding)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (article_id)
    DO UPDATE SET model = EXCLUDED.model,
                  dim = EXCLUDED.dim,
                  embedding = EXCLUDED.embedding;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (embed.article_id, embed.model, embed.dim, embed.embedding))

# ────────────────────────────────
# 4️⃣ Events (사건)
# ────────────────────────────────
def insert_event(event: Event) -> int:
    sql = """
    INSERT INTO events (
        summary, topic_tags, start_time, end_time,
        centroid_article_id, event_cred, conflicts
    )
    VALUES (
        %(summary)s, %(topic_tags)s, %(start_time)s, %(end_time)s,
        %(centroid_article_id)s, %(event_cred)s, %(conflicts)s
    )
    RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, event.model_dump())
        event_id = cur.fetchone()[0]
    return event_id


def link_event_articles(event_id: int, links: Iterable[tuple[int, float]]) -> None:
    """
    links: [(article_id, similarity), ...]
    """
    sql = """
    INSERT INTO event_articles (event_id, article_id, similarity)
    VALUES (%s, %s, %s)
    ON CONFLICT (event_id, article_id) DO NOTHING;
    """
    with get_conn() as conn, conn.cursor() as cur:
        execute_batch(cur, sql, [(event_id, aid, sim) for aid, sim in links], page_size=200)

# ────────────────────────────────
# 5️⃣ Reports (리포트)
# ────────────────────────────────
def insert_report(report: Report) -> int:
    sql = """
    INSERT INTO reports (event_id, format, version, content)
    VALUES (%(event_id)s, %(format)s, %(version)s, %(content)s)
    RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, report.model_dump())
        report_id = cur.fetchone()[0]
    return report_id

# ────────────────────────────────
# 6️⃣ 조회용 헬퍼
# ────────────────────────────────
def get_recent_articles(limit: int = 5) -> List[Dict[str, Any]]:
    sql = "SELECT id, title, url, published_at FROM articles ORDER BY published_at DESC NULLS LAST LIMIT %s;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (limit,))
        rows = cur.fetchall()
    return [{"id": r[0], "title": r[1], "url": r[2], "published_at": r[3]} for r in rows]
