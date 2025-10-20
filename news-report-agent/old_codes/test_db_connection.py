# services/db_services 모듈에서 데이터베이스 연결을 반환하는 함수 get_conn을 임포트
from services.db_services import get_conn

def main():
    # 연결 시작 로그 출력 (사용자 피드백)
    print("🔌 Connecting to Postgres...")
    # Postgres 연결 객체(Connection) 생성. 실패 시 예외가 발생함.
    conn = get_conn()
    # SQL 실행을 위한 커서(Cursor) 생성
    cur = conn.cursor()

    # 서버 버전 확인용 쿼리 실행 (PostgreSQL 버전 문자열 반환)
    cur.execute("SELECT version();")
    # 결과 집합에서 첫 행을 가져오고, 그 행의 첫 번째 컬럼을 선택
    version = cur.fetchone()[0]
    # 연결된 서버 버전 출력
    print("✅ Connected to:", version)

    # 현재 데이터베이스명과 현재 사용자명 확인
    cur.execute("SELECT current_database(), current_user;")
    # 두 컬럼을 각각 db, user 변수로 언패킹
    db, user = cur.fetchone()
    # 현재 DB와 사용자 정보 출력
    print(f"• DB: {db}, User: {user}")

    # public 스키마에 존재하는 테이블 개수 조회
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    # COUNT(*) 결과는 단일 정수값이므로 첫 행의 첫 컬럼을 가져옴
    n_tables = cur.fetchone()[0]
    # 테이블 개수 출력
    print(f"• Tables in schema: {n_tables}")

    # 커서 리소스 정리
    cur.close()
    # 커넥션 종료 (트랜잭션 정리 및 소켓 닫힘)
    conn.close()
    # 종료 로그 출력
    print("🔒 Connection closed.")

# 이 파일을 직접 실행했을 때만 main()을 호출 (모듈로 임포트될 때는 실행 안 함)
if __name__ == "__main__":
    main()
