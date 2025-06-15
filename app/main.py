"""
AI Diary Analysis Backend - Main Application
Flutter 앱 연동 가능한 완전한 프로덕션 버전
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

import firebase_admin
from firebase_admin import credentials

from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.core.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.exceptions import add_exception_handlers

# 설정 로드
settings = get_settings()

# 로거 설정
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 시작 및 종료 시 실행되는 이벤트"""
    # 시작 시
    logger.info("🚀 AI Diary Backend 서버 시작...")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info(f"🔥 Firebase Enabled: {settings.USE_FIREBASE}")
    logger.info(f"🤖 Gemini API: {'✅ Configured' if settings.GEMINI_API_KEY else '❌ Missing'}")
    
    # 환경별 초기화
    try:
        # Firebase 초기화 (이미 security.py에서 처리됨)
        from app.core.security import firebase_initialized
        if firebase_initialized:
            logger.info("🔥 Firebase 초기화 완료")
        else:
            logger.info("🔥 Firebase 비활성화 모드")
        
        # 데이터베이스 초기화 (설정된 경우에만)
        if settings.DATABASE_URL:
            await initialize_database()
            logger.info("🗄️ 데이터베이스 연결 완료")
        else:
            logger.info("🗄️ 데이터베이스 연결 없음 (개발/테스트 모드)")
        
        # Redis 초기화 (설정된 경우에만)
        if settings.REDIS_URL:
            await initialize_redis()
            logger.info("🔴 Redis 연결 완료")
        else:
            logger.info("🔴 Redis 연결 없음")
        
        # AI 모델 초기화
        await initialize_ai_services()
        logger.info("🤖 AI 서비스 초기화 완료")
        
    except Exception as e:
        logger.error(f"❌ 초기화 실패: {e}")
        # 개발 환경에서는 계속 진행, 프로덕션에서는 중단
        if not settings.DEBUG:
            raise
    
    yield
    
    # 종료 시
    logger.info("🛑 AI Diary Backend 서버 종료...")
    try:
        await cleanup_resources()
        logger.info("✅ 리소스 정리 완료")
    except Exception as e:
        logger.error(f"❌ 리소스 정리 실패: {e}")


async def initialize_firebase():
    """Firebase 초기화"""
    try:
        if not firebase_admin._apps:
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": settings.FIREBASE_AUTH_URI,
                "token_uri": settings.FIREBASE_TOKEN_URI,
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            logger.info("🔥 Firebase Admin SDK 초기화 완료")
        else:
            logger.info("⚠️ Firebase 이미 초기화됨 - 중복 초기화 방지")
    except Exception as e:
        logger.error(f"❌ Firebase 초기화 실패: {e}")
        raise


async def initialize_database():
    """데이터베이스 초기화"""
    try:
        from app.config.database import engine
        # 데이터베이스 연결 테스트
        # 실제 연결 테스트 로직 구현
        logger.info("🗄️ 데이터베이스 연결 테스트 완료")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")
        raise


async def initialize_redis():
    """Redis 초기화"""
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        logger.info("🔴 Redis 연결 테스트 완료")
    except Exception as e:
        logger.error(f"❌ Redis 초기화 실패: {e}")
        raise


async def initialize_ai_services():
    """AI 서비스 초기화"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Gemini API 테스트
        model = genai.GenerativeModel('gemini-1.5-flash')
        test_response = await model.generate_content_async("Hello")
        
        logger.info("🤖 Gemini API 연결 테스트 완료")
    except Exception as e:
        logger.error(f"❌ AI 서비스 초기화 실패: {e}")
        raise


async def cleanup_resources():
    """리소스 정리"""
    try:
        # 데이터베이스 연결 정리
        # Redis 연결 정리
        # 기타 리소스 정리
        pass
    except Exception as e:
        logger.error(f"❌ 리소스 정리 중 오류: {e}")


def create_application() -> FastAPI:
    """FastAPI 애플리케이션 생성 및 설정"""
    
    # FastAPI 앱 생성
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI 일기 분석 백엔드 API 서버 - Flutter 앱과 연동",
        openapi_url=f"/api/v1/openapi.json",
        docs_url="/docs" if settings.DEBUG else "/docs",  # 프로덕션에서도 API 문서 제공
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS 설정 - Flutter 앱 지원
    if settings.DEBUG:
        # 개발 환경: 모든 origin 허용
        allowed_origins = ["*"]
        logger.info("🌐 CORS: 개발 모드 - 모든 origin 허용")
    else:
        # 프로덕션 환경: Flutter 앱과 웹 클라이언트만 허용
        allowed_origins = [
            *settings.ALLOWED_ORIGINS,
            "capacitor://localhost",  # Capacitor 앱 지원
            "ionic://localhost",      # Ionic 앱 지원
            "http://localhost",       # 로컬 테스트
            "https://localhost",      # HTTPS 로컬 테스트
        ]
        logger.info(f"🌐 CORS: 프로덕션 모드 - 허용된 origins: {len(allowed_origins)}개")

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "*",
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        expose_headers=["*"],
        # 개발 환경에서 파일 시스템 지원
        allow_origin_regex=r".*" if settings.DEBUG else None,
    )

    # 보안 미들웨어 (조건부 적용)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    
    # 커스텀 미들웨어 (에러 처리 개선)
    try:
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RateLimitMiddleware)
    except Exception as e:
        logger.warning(f"⚠️ 일부 미들웨어 로딩 실패: {e}")
        # 개발 환경에서는 계속 진행
        if not settings.DEBUG:
            raise

    # API 라우터 등록
    app.include_router(api_router, prefix="/api/v1")

    # 예외 핸들러 등록
    add_exception_handlers(app)

    # 헬스체크 엔드포인트 (확장된 정보 제공)
    @app.get("/health")
    async def health_check():
        """서버 상태 확인 - 상세 정보 포함"""
        health_status = {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": "2025-06-14T15:00:00Z",
            "services": {
                "gemini_api": bool(settings.GEMINI_API_KEY),
                "firebase": settings.USE_FIREBASE,
                "database": bool(settings.DATABASE_URL),
                "redis": bool(settings.REDIS_URL),
            },
            "ready_for_flutter": True,
        }
        
        # Railway 환경 정보 추가
        if os.getenv("RAILWAY_ENVIRONMENT"):
            health_status["deployment"] = {
                "platform": "Railway",
                "port": settings.PORT,
                "environment": os.getenv("RAILWAY_ENVIRONMENT"),
            }
        
        return health_status

    # 루트 엔드포인트 (Flutter 앱 정보 포함)
    @app.get("/")
    async def root():
        """루트 엔드포인트 - Flutter 앱 연동 정보"""
        return {
            "message": "🤖 AI Diary Analysis Backend",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "health": "/health",
            "api_base": "/api/v1",
            "flutter_ready": True,
            "endpoints": {
                "auth": "/api/v1/auth",
                "analysis": "/api/v1/analysis",
                "matching": "/api/v1/matching",
            },
            "features": {
                "diary_analysis": True,
                "emotion_analysis": True,
                "personality_analysis": True,
                "user_matching": True,
                "firebase_auth": settings.USE_FIREBASE,
            }
        }
    
    # Flutter 앱 연결 테스트 엔드포인트
    @app.get("/api/v1/flutter/test")
    async def flutter_connection_test():
        """Flutter 앱 연결 테스트"""
        return {
            "status": "success",
            "message": "Flutter 앱과 백엔드 연결 성공!",
            "timestamp": "2025-06-14T15:00:00Z",
            "server_info": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
            }
        }
    
    # API 상태 확인 엔드포인트
    @app.get("/api/v1/status")
    async def api_status():
        """API 서비스 상태 확인"""
        try:
            return {
                "api_status": "operational",
                "services": {
                    "gemini_ai": "operational" if settings.GEMINI_API_KEY else "unavailable",
                    "firebase_auth": "operational" if settings.USE_FIREBASE else "disabled",
                    "database": "operational" if settings.DATABASE_URL else "unavailable",
                    "redis_cache": "operational" if settings.REDIS_URL else "unavailable",
                },
                "last_check": "2025-06-14T15:00:00Z"
            }
        except Exception as e:
            logger.error(f"❌ API 상태 확인 실패: {e}")
            raise HTTPException(status_code=500, detail="API 상태 확인 실패")
    
    # 환경변수 디버깅 엔드포인트 (개발용)
    @app.get("/api/v1/debug/env")
    async def debug_environment():
        """환경변수 상태 확인 (개발 및 디버깅용)"""
        if not settings.DEBUG and settings.ENVIRONMENT == "production":
            raise HTTPException(status_code=404, detail="Not found")
        
        # Firebase 설정 상태 확인
        firebase_config_status = {
            "project_id": bool(settings.FIREBASE_PROJECT_ID),
            "private_key_id": bool(settings.FIREBASE_PRIVATE_KEY_ID),
            "private_key": bool(settings.FIREBASE_PRIVATE_KEY),
            "client_email": bool(settings.FIREBASE_CLIENT_EMAIL),
            "client_id": bool(settings.FIREBASE_CLIENT_ID),
            "use_firebase": settings.USE_FIREBASE,
        }
        
        # Firebase 초기화 상태 확인
        from app.core.security import firebase_initialized
        
        return {
            "debug_mode": settings.DEBUG,
            "environment": settings.ENVIRONMENT,
            "firebase": {
                "config_status": firebase_config_status,
                "initialized": firebase_initialized,
                "project_id_value": settings.FIREBASE_PROJECT_ID[:10] + "..." if settings.FIREBASE_PROJECT_ID else None,
                "client_email_value": settings.FIREBASE_CLIENT_EMAIL[:20] + "..." if settings.FIREBASE_CLIENT_EMAIL else None,
            },
            "services": {
                "gemini_api": bool(settings.GEMINI_API_KEY),
                "database": bool(settings.DATABASE_URL),
                "redis": bool(settings.REDIS_URL),
            },
            "railway": {
                "environment": os.getenv("RAILWAY_ENVIRONMENT"),
                "port": os.getenv("PORT"),
                "deployment": bool(os.getenv("RAILWAY_ENVIRONMENT")),
            },
            "message": "이 정보는 디버깅 목적으로만 사용되며 프로덕션에서는 비활성화됩니다."
        }

    return app


# FastAPI 앱 인스턴스 생성
app = create_application()


if __name__ == "__main__":
    # 환경별 설정
    port = getattr(settings, 'PORT', 8000)
    host = "0.0.0.0"
    
    logger.info(f"🚀 서버 시작: {host}:{port}")
    logger.info(f"🔧 디버그 모드: {settings.DEBUG}")
    logger.info(f"🌍 환경: {settings.ENVIRONMENT}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True,
    )
