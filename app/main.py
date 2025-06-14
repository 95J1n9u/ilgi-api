"""
AI Diary Analysis Backend - Main Application
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.core.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.exceptions import add_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 시작 및 종료 시 실행되는 이벤트"""
    # 시작 시
    print("🚀 AI Diary Backend 서버 시작...")
    
    # 여기서 DB 연결, Redis 연결, ML 모델 로드 등을 수행
    # await initialize_database()
    # await initialize_redis()
    # await load_ml_models()
    
    yield
    
    # 종료 시
    print("🛑 AI Diary Backend 서버 종료...")
    # 여기서 리소스 정리
    # await cleanup_resources()


def create_application() -> FastAPI:
    """FastAPI 애플리케이션 생성 및 설정"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI 일기 분석 백엔드 API 서버",
        openapi_url=f"/api/v1/openapi.json",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # 개발 환경에서는 더 관대한 CORS 설정
    if settings.DEBUG:
        allowed_origins = ["*"]  # 개발 중에는 모든 origin 허용
        # 파일 시스템에서 직접 열린 HTML을 위해 null origin도 허용
        allow_origin_regex = None
    else:
        allowed_origins = settings.ALLOWED_ORIGINS
        allow_origin_regex = None

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        # 개발 환경에서 파일 시스템에서 열린 HTML 지원
        allow_origin_regex=r".*" if settings.DEBUG else None,
    )

    # 보안 미들웨어
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # API 라우터 등록
    app.include_router(api_router, prefix="/api/v1")

    # 예외 핸들러 등록
    add_exception_handlers(app)

    # 헬스체크 엔드포인트
    @app.get("/health")
    async def health_check():
        """서버 상태 확인"""
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # 루트 엔드포인트
    @app.get("/")
    async def root():
        """루트 엔드포인트"""
        return {
            "message": "🤖 AI Diary Analysis Backend",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        }

    return app


# FastAPI 앱 인스턴스 생성
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
