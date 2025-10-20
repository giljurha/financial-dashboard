# services/embedding_service.py
# ────────────────────────────────
# 🔢 Embedding 관리 (pgvector)
# ────────────────────────────────

from openai import OpenAI
import os
from services import db_service
from models import ArticleEmbedding

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def embed_text(article_id: int, text: str, model: str = "text-embedding-3-small"):
    """
    주어진 텍스트를 임베딩하고 DB에 저장.
    """
    try:
        response = client.embeddings.create(model=model, input=text)
        vector = response.data[0].embedding

        embedding = ArticleEmbedding(
            article_id=article_id,
            model=model,
            dim=len(vector),
            embedding=vector,
        )
        db_service.upsert_embedding(embedding)

        return {"article_id": article_id, "dim": len(vector), "model": model}
    except Exception as e:
        print(f"[embed_text] Error: {e}")
        return {"error": str(e)}


def search_similar_text(query_text: str, top_k: int = 5, model: str = "text-embedding-3-small"):
    """
    입력 텍스트와 유사한 기사 검색 (pgvector cosine similarity).
    """
    try:
        response = client.embeddings.create(model=model, input=query_text)
        vector = response.data[0].embedding

        sql = """
        SELECT a.id, a.title, a.url,
               1 - (aemb.embedding <=> %s::vector) AS similarity
        FROM article_embeddings aemb
        JOIN articles a ON a.id = aemb.article_id
        ORDER BY aemb.embedding <=> %s::vector
        LIMIT %s;
        """

        with db_service.get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (vector, vector, top_k))
            rows = cur.fetchall()

        return [{"id": r[0], "title": r[1], "url": r[2], "similarity": float(r[3])} for r in rows]
    except Exception as e:
        print(f"[search_similar_text] Error: {e}")
        return {"error": str(e)}


def generate_embeddings_batch(article_ids: list[int]) -> dict:
    """
    여러 기사 ID에 대해 배치 임베딩 생성 및 저장
    
    Args:
        article_ids: 임베딩을 생성할 기사 ID 목록
        
    Returns:
        dict: {"processed": int, "errors": list[str], "processed_ids": list[int]}
    """
    from services.db_services import get_conn
    
    processed = 0
    errors = []
    processed_ids = []
    
    with get_conn() as conn, conn.cursor() as cur:
        for article_id in article_ids:
            try:
                # DB에서 기사 조회
                cur.execute(
                    "SELECT id, title, body FROM articles WHERE id = %s",
                    (article_id,)
                )
                row = cur.fetchone()
                
                if not row:
                    errors.append(f"기사 ID {article_id}를 찾을 수 없습니다")
                    continue
                
                _, title, body = row
                if not body or len(body.strip()) < 50:
                    errors.append(f"기사 ID {article_id}: 본문이 너무 짧습니다")
                    continue
                
                # 제목 + 본문으로 임베딩 생성
                text_for_embedding = f"{title}\n\n{body}"
                result = embed_text(article_id, text_for_embedding)
                
                if "error" not in result:
                    processed += 1
                    processed_ids.append(article_id)
                else:
                    errors.append(f"기사 ID {article_id}: {result['error']}")
                    
            except Exception as e:
                errors.append(f"기사 ID {article_id}: {str(e)}")
    
    return {
        "processed": processed,
        "errors": errors,
        "processed_ids": processed_ids
    }