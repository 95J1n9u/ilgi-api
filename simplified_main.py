"""
main.py 실행을 위한 간단한 설정
데이터베이스 없이 메모리 기반으로 실행
"""
import os
import tempfile
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 환경변수 설정 (데이터베이스 우회)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["DEBUG"] = "True"

from app.api.v1 import analysis  # 분석 API만 import
from app.config.settings import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """간소화된 생명주기"""
    print("🚀 AI Diary Backend 서버 시작...")
    yield
    print("🛑 AI Diary Backend 서버 종료...")

def create_application() -> FastAPI:
    """간소화된 FastAPI 애플리케이션"""
    
    app = FastAPI(
        title="AI Diary Analysis Backend (Simple)",
        version="1.0.0",
        description="간소화된 AI 일기 분석 백엔드",
        docs_url="/docs",
        lifespan=lifespan,
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 분석 API만 포함 (데이터베이스 의존성 제거)
    app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["AI 분석"])

    @app.get("/")
    async def root():
        return {
            "message": "🤖 AI Diary Analysis Backend (Simple Mode)",
            "version": "1.0.0",
            "docs": "/docs",
            "status": "running"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "mode": "simple"}

    return app

# FastAPI 앱 인스턴스 생성
app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "simplified_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
