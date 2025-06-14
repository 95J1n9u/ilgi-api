"""
애플리케이션 설정
"""
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 애플리케이션 기본 설정
    APP_NAME: str = Field(default="AI Diary Analysis Backend")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    
    # 데이터베이스 설정 (Railway에서는 자동 제공)
    DATABASE_URL: Optional[str] = Field(None, description="PostgreSQL 데이터베이스 URL")
    DATABASE_TEST_URL: Optional[str] = Field(None, description="테스트 데이터베이스 URL")
    
    # Redis 설정 (선택사항)
    REDIS_URL: Optional[str] = Field(None, description="Redis URL")
    
    # Railway 환경 감지
    PORT: int = Field(default=8000, description="서버 포트")
    RAILWAY_ENVIRONMENT: Optional[str] = Field(None, description="Railway 환경")
    
    # Google AI API 설정
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API 키")
    
    # Firebase 설정 (선택사항 - 환경에 따라 자동 조정)
    FIREBASE_PROJECT_ID: Optional[str] = Field(None, description="Firebase 프로젝트 ID")
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = Field(None, description="Firebase Private Key ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = Field(None, description="Firebase Private Key")
    FIREBASE_CLIENT_EMAIL: Optional[str] = Field(None, description="Firebase Client Email")
    FIREBASE_CLIENT_ID: Optional[str] = Field(None, description="Firebase Client ID")
    FIREBASE_AUTH_URI: str = Field(default="https://accounts.google.com/o/oauth2/auth")
    FIREBASE_TOKEN_URI: str = Field(default="https://oauth2.googleapis.com/token")
    
    # Firebase 사용 여부 (자동 감지)
    USE_FIREBASE: bool = Field(default=True)
    
    # JWT 설정
    SECRET_KEY: str = Field(..., description="JWT 시크릿 키")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"]
    )
    
    # 데이터베이스 설정
    DATABASE_URL: Optional[str] = Field(None, description="postgresql+asyncpg://ai_diary_user:!rkdwlsrn713@postgres/ai_diary_db")
    DATABASE_SYNC_URL: Optional[str] = Field(None, description="postgresql://ai_diary_user:!rkdwlsrn713@postgres/ai_diary_db")
    DATABASE_TEST_URL: Optional[str] = Field(None, description="DATABASE_TEST_URL=postgresql+asyncpg://ai_diary_user:!rkdwlsrn713@postgres/ai_diary_test_db")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100)
    
    # 파일 업로드 제한
    MAX_FILE_SIZE_MB: int = Field(default=10)
    
    # AI 분석 설정
    MAX_DIARY_LENGTH: int = Field(default=5000)
    ANALYSIS_CACHE_TTL: int = Field(default=86400)  # 24시간
    BATCH_SIZE: int = Field(default=10)
    
    # Sentry 모니터링 (선택사항)
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """CORS origins 설정 검증"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("FIREBASE_PRIVATE_KEY", pre=True)
    def format_firebase_private_key(cls, v):
        """Firebase Private Key 포맷 조정"""
        if isinstance(v, str):
            return v.replace("\\n", "\n")
        return v
    
    @validator("USE_FIREBASE", pre=True, always=True)
    def determine_firebase_usage(cls, v, values):
        """Firebase 사용 여부 자동 결정"""
        # Railway 환경이거나 Firebase 설정이 없으면 Firebase 비활성화
        railway_env = values.get('RAILWAY_ENVIRONMENT')
        firebase_project = values.get('FIREBASE_PROJECT_ID')
        
        if railway_env and not firebase_project:
            return False
        elif not firebase_project:
            return False
        return True
    
    @validator("PORT", pre=True)
    def get_port_from_env(cls, v):
        """환경변수에서 PORT 가져오기 (Railway 지원)"""
        import os
        return int(os.getenv("PORT", v))


@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스를 캐시하여 반환"""
    return Settings()
