"""
데이터베이스 연결 설정
"""
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.settings import get_settings

settings = get_settings()

# SQLAlchemy Base 클래스
Base = declarative_base()

# 비동기 데이터베이스 엔진
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 비동기 세션 메이커
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
)

# 동기 엔진 (마이그레이션용)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """테이블 생성 (개발용)"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """테이블 삭제 (개발용)"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.engine = async_engine
        self.session_maker = AsyncSessionLocal
    
    async def create_session(self) -> AsyncSession:
        """새로운 세션 생성"""
        return self.session_maker()
    
    async def health_check(self) -> bool:
        """데이터베이스 연결 상태 확인"""
        try:
            async with self.session_maker() as session:
                await session.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    async def close(self):
        """데이터베이스 연결 종료"""
        await self.engine.dispose()
