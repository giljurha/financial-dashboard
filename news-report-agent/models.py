# models.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


# ────────────────────────────────
# 1️⃣ Outlet (언론사 정보)
# ────────────────────────────────
class Outlet(BaseModel):
    id: Optional[int] = None
    name: str
    domain: str
    country_code: Optional[str] = Field(default=None, max_length=2)
    created_at: Optional[datetime] = None


# ────────────────────────────────
# 2️⃣ Article (기사)
# ────────────────────────────────
class Article(BaseModel):
    id: Optional[int] = None
    outlet_id: int
    url: HttpUrl
    title: str
    published_at: Optional[datetime] = None
    language: Optional[str] = None
    author: Optional[str] = None
    body: Optional[str] = None
    canonical_url: Optional[HttpUrl] = None
    hash_sha256: Optional[str] = None
    fetched_at: Optional[datetime] = None


class ArticleList(BaseModel):
    articles: List[Article]


# ────────────────────────────────
# 3️⃣ Event (사건)
# ────────────────────────────────
class Event(BaseModel):
    id: Optional[int] = None
    summary: Optional[str] = None
    topic_tags: Optional[List[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    centroid_article_id: Optional[int] = None
    event_cred: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    conflicts: Optional[List[str]] = None
    created_at: Optional[datetime] = None


class EventList(BaseModel):
    events: List[Event]


# ────────────────────────────────
# 4️⃣ Report (사건 요약 리포트)
# ────────────────────────────────
class Report(BaseModel):
    id: Optional[int] = None
    event_id: int
    format: str = Field(default="md", pattern="^(md|html|json)$")
    version: int = 1
    content: str
    created_at: Optional[datetime] = None


# ────────────────────────────────
# 5️⃣ Embedding (선택: DB insert용)
# ────────────────────────────────
class ArticleEmbedding(BaseModel):
    article_id: int
    model: str
    dim: int
    embedding: List[float]


# ────────────────────────────────
# ✅ 통합 출력 구조 (예: Task expected_output)
# ────────────────────────────────
class ExtractionResult(BaseModel):
    outlet: Outlet
    articles: List[Article]
