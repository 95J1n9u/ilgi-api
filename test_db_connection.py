"""
데이터베이스 연결 테스트 스크립트
"""
import asyncio
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

async def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        import asyncpg
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"🔗 데이터베이스 연결 테스트: {DATABASE_URL}")
        
        # asyncpg URL 형식으로 변환
        db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        
        # 연결 테스트
        conn = await asyncpg.connect(db_url)
        
        # 간단한 쿼리 실행
        result = await conn.fetchval("SELECT version()")
        print(f"✅ PostgreSQL 연결 성공!")
        print(f"📊 버전: {result}")
        
        # 사용자 확인
        user_check = await conn.fetchval("SELECT current_user")
        print(f"👤 현재 사용자: {user_check}")
        
        await conn.close()
        return True
        
    except ImportError:
        print("❌ asyncpg가 설치되지 않았습니다.")
        print("💡 pip install asyncpg 명령어로 설치하세요.")
        return False
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print("💡 PostgreSQL 서버가 실행 중인지 확인하세요.")
        print("💡 사용자와 데이터베이스가 올바르게 생성되었는지 확인하세요.")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())
