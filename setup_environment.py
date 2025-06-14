"""
main.py 실행을 위한 PostgreSQL 설정 스크립트
"""
import subprocess
import sys
import os

def setup_postgresql():
    """PostgreSQL 설정"""
    print("🐘 PostgreSQL 설정 중...")
    
    # 1. PostgreSQL 설치 확인
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        print(f"✅ PostgreSQL 설치됨: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ PostgreSQL이 설치되지 않았습니다.")
        print("💡 다음 링크에서 PostgreSQL을 다운로드하여 설치하세요:")
        print("   https://www.postgresql.org/download/windows/")
        return False
    
    # 2. 데이터베이스 생성 SQL 스크립트
    sql_commands = """
-- 사용자 생성
CREATE USER ai_diary_user WITH PASSWORD '!rkdwlsrn713';

-- 데이터베이스 생성
CREATE DATABASE ai_diary_db OWNER ai_diary_user;
CREATE DATABASE ai_diary_test_db OWNER ai_diary_user;

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE ai_diary_db TO ai_diary_user;
GRANT ALL PRIVILEGES ON DATABASE ai_diary_test_db TO ai_diary_user;
"""
    
    # SQL 파일 생성
    with open('setup_db.sql', 'w', encoding='utf-8') as f:
        f.write(sql_commands)
    
    print("📝 데이터베이스 설정 SQL 파일 생성됨: setup_db.sql")
    print("💡 다음 명령어로 실행하세요:")
    print("   psql -U postgres -f setup_db.sql")
    
    return True

def run_migrations():
    """Alembic 마이그레이션 실행"""
    print("🔄 데이터베이스 마이그레이션 실행 중...")
    
    try:
        # Alembic 마이그레이션
        subprocess.run(['alembic', 'upgrade', 'head'], check=True)
        print("✅ 마이그레이션 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic이 설치되지 않았습니다.")
        print("💡 pip install alembic 명령어로 설치하세요.")
        return False

def check_redis():
    """Redis 상태 확인"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis 연결 성공")
        return True
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")
        print("💡 Redis를 설치하고 실행하세요:")
        print("   Windows: https://github.com/microsoftarchive/redis/releases")
        return False

if __name__ == "__main__":
    print("🚀 AI Diary Backend 환경 설정")
    print("=" * 50)
    
    # PostgreSQL 설정
    if not setup_postgresql():
        sys.exit(1)
    
    # Redis 확인
    check_redis()
    
    print("\n📋 다음 단계:")
    print("1. PostgreSQL에서 setup_db.sql 실행")
    print("   psql -U postgres -f setup_db.sql")
    print("2. 마이그레이션 실행")
    print("   alembic upgrade head")
    print("3. main.py 실행")
    print("   python -m app.main")
