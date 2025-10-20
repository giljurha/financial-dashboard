from crewai import tool
from services.orchestrator import fetch_scrape_upsert
from services.embedding_service import generate_embeddings_batch
import json

@tool
def fetch_and_store_news(rss_feeds: list[str]) -> dict:
    """
    RSS 피드에서 뉴스를 가져와서 데이터베이스에 저장합니다.
    
    Args:
        rss_feeds: RSS 피드 URL 목록
        
    Returns:
        dict: 저장 결과 통계 (fetched, inserted, updated, skipped, errors 등)
    """
    
    result = fetch_scrape_upsert(
        rss_feeds=rss_feeds,
        batch_limit=10_000,
        commit=True  # 실제 저장
    )
    
    # 읽기 쉬운 형태로 변환 (ID 정보 포함)
    summary = f"""📊 뉴스 수집 및 저장 완료:

📥 가져온 기사: {result.get('fetched', 0)}개
✅ 정제된 기사: {result.get('cleaned', 0)}개
🆕 새로 저장: {result.get('inserted', 0)}개 (ID: {result.get('inserted_ids', [])})
🔄 업데이트: {result.get('updated', 0)}개 (ID: {result.get('updated_ids', [])})
⏭️ 건너뜀: {result.get('skipped', 0)}개
❌ 오류: {len(result.get('errors', []))}개
⏱️ 소요시간: {result.get('elapsed_sec', 0)}초

🔗 임베딩 대상 ID: {result.get('all_processed_ids', [])}"""
    
    return summary


@tool
def generate_embeddings_for_articles(article_ids: list[int]) -> str:
    """
    기사 ID들을 받아서 임베딩을 생성하고 저장합니다.
    
    Args:
        article_ids: 임베딩을 생성할 기사 ID 목록
        
    Returns:
        str: 임베딩 생성 결과 요약
    """
    # embedding_service.py의 배치 함수 호출
    result = generate_embeddings_batch(article_ids)
    
    summary = f"""🔢 임베딩 생성 완료:

✅ 처리된 기사: {result['processed']}개
❌ 오류: {len(result['errors'])}개
📝 처리된 ID: {result['processed_ids']}

{'⚠️ 오류 목록:' if result['errors'] else ''}
{chr(10).join(f'  • {error}' for error in result['errors']) if result['errors'] else ''}"""
    
    return summary