# ─────────────────────────────────────────────────────────────────────────────
# DB 저장 유틸 (이 파일 안에서 자급자족)
# ─────────────────────────────────────────────────────────────────────────────
import os, hashlib, json, re
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import psycopg2
from psycopg2.extras import execute_values

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:1234@localhost:5432/appdb")

def get_conn():
    return psycopg2.connect(POSTGRES_URL)

# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼들
# ─────────────────────────────────────────────────────────────────────────────
_OFF_RE = re.compile(r"(Z|[+-]\d{2}:\d{2})$")

def _extract_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host

def _norm_authors(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, list):
        return ", ".join([str(x) for x in val if x])
    return str(val)

def _sha256(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def _format_offset_str(dt: datetime) -> Optional[str]:
    if dt.tzinfo is None:
        return None
    off = dt.utcoffset()
    if off is None:
        return None
    total = int(off.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hh, mm = divmod(total // 60, 60)
    return f"{sign}{hh:02d}:{mm:02d}"

def _parse_dt_to_utc(published_date: Optional[str],
                     outlet_tz: Optional[str]) -> Tuple[Optional[datetime], Optional[str], str]:
    """
    반환: (published_at_utc, tz_offset_str, tz_source)
      - tz_source: 'string_offset' | 'outlet_tz' | 'unknown'
    규칙:
      1) published_date에 Z/±HH:MM 있으면 → 그 오프셋 그대로 tz-aware 파싱 → UTC 변환
      2) 없고 outlet_tz 있으면 → outlet 타임존으로 localize → UTC 변환
      3) 둘 다 없으면 → None, None, 'unknown'
    """
    if not published_date:
        return None, None, "unknown"

    s = published_date.strip()

    # 1) ISO 계열(+공백 허용) 우선 시도
    try:
        s_iso = s.replace(" ", "T")
        dt = datetime.fromisoformat(s_iso)
        if dt.tzinfo is not None:
            # aware → 그대로 UTC 변환
            tz_offset = _format_offset_str(dt)
            return dt.astimezone(timezone.utc), tz_offset, "string_offset"
        # naive → 아래 분기로
    except Exception:
        pass

    # 2) RFC 계열(예: Mon, 14 Oct 2025 02:35:12 GMT)
    try:
        from email.utils import parsedate_to_datetime
        dt2 = parsedate_to_datetime(s)
        if dt2.tzinfo is not None:
            tz_offset = _format_offset_str(dt2)
            return dt2.astimezone(timezone.utc), tz_offset, "string_offset"
    except Exception:
        pass

    # 3) 문자열 끝에 오프셋 패턴이 명시돼 있으면(간이 체크)
    if _OFF_RE.search(s):
        try:
            dt3 = datetime.fromisoformat(s.replace(" ", "T"))
            if dt3.tzinfo is not None:
                tz_offset = _format_offset_str(dt3)
                return dt3.astimezone(timezone.utc), tz_offset, "string_offset"
        except Exception:
            pass

    # 4) outlet 타임존으로 해석
    if outlet_tz:
        try:
            # naive로 한 번 파싱(년-월-일 시:분:초 정도만 지원)
            # 실패하면 그냥 unknown 처리
            try:
                dt_naive = datetime.fromisoformat(s.replace(" ", "T"))
                if dt_naive.tzinfo is not None:
                    tz_offset = _format_offset_str(dt_naive)
                    return dt_naive.astimezone(timezone.utc), tz_offset, "string_offset"
            except Exception:
                # YYYY-MM-DD만 온 경우 등 간이 처리
                try:
                    dt_naive = datetime.strptime(s.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                except Exception:
                    try:
                        dt_naive = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        dt_naive = datetime.strptime(s, "%Y-%m-%d")
            # outlet tz로 localize
            dt_loc = dt_naive.replace(tzinfo=ZoneInfo(outlet_tz))
            tz_offset = _format_offset_str(dt_loc)
            return dt_loc.astimezone(timezone.utc), tz_offset, "outlet_tz"
        except Exception:
            pass

    return None, None, "unknown"

# ─────────────────────────────────────────────────────────────────────────────
# 1) persist_outlets: 기사 목록에서 도메인 뽑아 upsert → {domain: (id, timezone)} 매핑 리턴
# ─────────────────────────────────────────────────────────────────────────────
def persist_outlets(articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    입력: fetch_scrape의 articles(list[dict])
          각 dict 최소 키: { "url": str, ... }
    동작: 도메인 단위 upsert(outlets.name=도메인 기본), timezone은 DB 값 유지
    반환: { domain: {"id": int, "timezone": Optional[str]} }
    """
    # URL → 도메인 dedup
    domains = []
    seen = set()
    for a in articles:
        url = a.get("url")
        if not url:
            continue
        d = _extract_domain(url)
        if not d or d in seen:
            continue
        seen.add(d)
        domains.append(d)

    if not domains:
        return {}

    mapping: Dict[str, Dict[str, Any]] = {}

    with get_conn() as conn, conn.cursor() as cur:
        # upsert 후 id, timezone 조회
        for dom in domains:
            cur.execute(
                """
                INSERT INTO public.outlets (name, domain)
                VALUES (%s, %s)
                ON CONFLICT (domain) DO UPDATE
                  SET name = EXCLUDED.name
                RETURNING id, timezone
                """,
                (dom, dom)
            )
            row = cur.fetchone()
            mapping[dom] = {"id": row[0], "timezone": row[1]}

    return mapping

# ─────────────────────────────────────────────────────────────────────────────
# 2) persist_articles: URL dedup → 시간 파싱 → articles upsert
# ─────────────────────────────────────────────────────────────────────────────
def persist_articles(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    입력: fetch_scrape의 articles(list[dict])
          각 dict 키 스펙(네 코드 기준):
            title:str, authors:list[str], published_date:str|None, text:str|None, url:str
    동작:
      - URL 중복 제거
      - outlets 매핑 조회/생성
      - published_date 오프셋/타임존 처리 → UTC timestamptz 저장
      - ON CONFLICT(url) upsert (변동 시에만 UPDATE)
      - inserted/updated/skipped 집계
    반환: {"processed":N, "inserted":i, "updated":u, "skipped":s, "errors":[...]}
    """
    # 0) URL dedup
    dedup: List[Dict[str, Any]] = []
    seen_urls = set()
    for a in articles:
        u = a.get("url")
        if not u or u in seen_urls:
            continue
        seen_urls.add(u)
        dedup.append(a)

    processed = 0
    inserted = 0
    updated = 0
    skipped = 0
    errors: List[Dict[str, Any]] = []
    inserted_ids: List[int] = []  # 새로 삽입된 기사 ID들
    updated_ids: List[int] = []   # 업데이트된 기사 ID들

    if not dedup:
        return {
            "processed": 0, 
            "inserted": 0, 
            "updated": 0, 
            "skipped": 0, 
            "errors": [],
            "inserted_ids": [],
            "updated_ids": [],
            "all_processed_ids": []
        }

    # 1) outlets upsert & 매핑
    outlet_map = persist_outlets(dedup)  # {domain: {"id":..., "timezone":...}}

    with get_conn() as conn, conn.cursor() as cur:
        for a in dedup:
            processed += 1
            try:
                url = a.get("url")
                title = a.get("title")
                if not url or not title:
                    skipped += 1
                    continue

                domain = _extract_domain(url)
                outlet_info = outlet_map.get(domain)
                if not outlet_info:
                    # 방어: 없으면 즉시 생성
                    cur.execute(
                        """
                        INSERT INTO public.outlets (name, domain)
                        VALUES (%s, %s)
                        ON CONFLICT (domain) DO UPDATE SET name = EXCLUDED.name
                        RETURNING id, timezone
                        """,
                        (domain, domain)
                    )
                    row = cur.fetchone()
                    outlet_info = {"id": row[0], "timezone": row[1]}
                    outlet_map[domain] = outlet_info

                outlet_id = outlet_info["id"]
                outlet_tz = outlet_info["timezone"]

                # 필드 매핑
                body = a.get("text")
                author = _norm_authors(a.get("authors"))
                language = a.get("language")  # 없으면 None
                canonical_url = url
                hash_sha256 = _sha256(body)
                published_raw = a.get("published_date")

                published_at, tz_offset_str, tz_source = _parse_dt_to_utc(
                    published_raw, outlet_tz
                )

                # upsert
                cur.execute(
                    """
                    INSERT INTO public.articles (
                        outlet_id, url, title, published_at, "language",
                        author, body, canonical_url, hash_sha256,
                        published_raw, published_tz_offset, published_tz_source
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        author = COALESCE(EXCLUDED.author, public.articles.author),
                        "language" = COALESCE(EXCLUDED."language", public.articles."language"),
                        published_at = COALESCE(EXCLUDED.published_at, public.articles.published_at),
                        body = COALESCE(EXCLUDED.body, public.articles.body),
                        hash_sha256 = COALESCE(EXCLUDED.hash_sha256, public.articles.hash_sha256),
                        canonical_url = COALESCE(EXCLUDED.canonical_url, public.articles.canonical_url),
                        published_raw = COALESCE(EXCLUDED.published_raw, public.articles.published_raw),
                        published_tz_offset = COALESCE(EXCLUDED.published_tz_offset, public.articles.published_tz_offset),
                        published_tz_source = COALESCE(EXCLUDED.published_tz_source, public.articles.published_tz_source),
                        fetched_at = now()
                    WHERE
                        public.articles.hash_sha256 IS DISTINCT FROM EXCLUDED.hash_sha256
                        OR public.articles.title IS DISTINCT FROM EXCLUDED.title
                        OR public.articles.published_at IS DISTINCT FROM EXCLUDED.published_at
                    RETURNING id;
                    """,
                    (
                        outlet_id, url, title, published_at, language,
                        author, body, canonical_url, hash_sha256,
                        published_raw, tz_offset_str, tz_source
                    )
                )

                # INSERT/UPDATE 구분 및 ID 수집
                result = cur.fetchone()
                if result:
                    article_id = result[0]
                    msg = cur.statusmessage  # e.g. "INSERT 0 1" or "UPDATE 1"
                    if msg.startswith("INSERT"):
                        inserted += 1
                        inserted_ids.append(article_id)
                    elif msg.startswith("UPDATE"):
                        updated += 1
                        updated_ids.append(article_id)
                    # 드물게 "UPDATE 0" (WHERE로 인해 no-op)이면 변화 없음 처리

            except Exception as e:
                skipped += 1
                errors.append({"url": a.get("url"), "error": str(e)})

    return {
        "processed": processed,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
        "inserted_ids": inserted_ids,  # 새로 삽입된 기사 ID들
        "updated_ids": updated_ids,    # 업데이트된 기사 ID들
        "all_processed_ids": inserted_ids + updated_ids  # 임베딩 대상 ID들
    }
