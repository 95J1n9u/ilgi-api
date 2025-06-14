"""
데이터베이스 설정 - Docker Compose 및 Railway 지원
"""
import os
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.config.settings import get_settings

settings = get_settings()

# SQLAlchemy Base
Base = declarative_base()
metadata = MetaData()


def get_database_urls():
    """환경별 데이터베이스 URL 생성"""
    base_url = settings.DATABASE_URL
    
    if not base_url:
        raise ValueError("DATABASE_URL이 설정되지 않았습니다.")
    
    # 명시적으로 동기 URL이 설정된 경우
    if hasattr(settings, 'DATABASE_SYNC_URL') and settings.DATABASE_SYNC_URL:
        async_url = base_url
        sync_url = settings.DATABASE_SYNC_URL
    else:
        # URL 파싱하여 비동기/동기 버전 생성
        parsed = urlparse(base_url)
        
        # 비동기 URL (asyncpg)
        if "+asyncpg" not in parsed.scheme:
            async_scheme = f"{parsed.scheme}+asyncpg"
            async_url = urlunparse(parsed._replace(scheme=async_scheme))
        else:
            async_url = base_url
        
        # 동기 URL (psycopg2)
        sync_scheme = parsed.scheme.replace("+asyncpg", "")
        sync_url = urlunparse(parsed._replace(scheme=sync_scheme))
    
    return async_url, sync_url


def create_database_engines():
    """데이터베이스 엔진 생성"""
    async_url, sync_url = get_database_urls()
    
    # 비동기 엔진
    async_engine = create_async_engine(
        async_url,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    # 동기 엔진 (Alembic 마이그레이션용)
    sync_engine = create_engine(
        sync_url,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    return async_engine, sync_engine


# 엔진 생성
async_engine, sync_engine = create_database_engines()

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=True,
    autocommit=False,
)


# 의존성 주입용 함수들
async def get_async_db() -> AsyncSession:
    """비동기 데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """동기 데이터베이스 세션 의존성 (Alembic용)"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# 연결 테스트 함수
async def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            row = result.fetchone()
            return row is not None
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")
        return False


def test_sync_database_connection():
    """동기 데이터베이스 연결 테스트"""
    try:
        with SessionLocal() as session:
            result = session.execute("SELECT 1")
            row = result.fetchone()
            return row is not None
    except Exception as e:
        print(f"동기 데이터베이스 연결 실패: {e}")
        return False


# 환경 정보 출력
def print_database_info():
    """데이터베이스 설정 정보 출력"""
    async_url, sync_url = get_database_urls()
    
    # URL에서 비밀번호 마스킹
    def mask_password(url):
        parsed = urlparse(url)
        if parsed.password:
            masked = parsed._replace(netloc=f"{parsed.username}:***@{parsed.hostname}:{parsed.port}")
            return urlunparse(masked)
        return url
    
    print("🗄️ Database Configuration:")
    print(f"  Async URL: {mask_password(async_url)}")
    print(f"  Sync URL:  {mask_password(sync_url)}")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Debug: {settings.DEBUG}")


# 애플리케이션 시작시 정보 출력
if __name__ != "__main__":
    print_database_info()