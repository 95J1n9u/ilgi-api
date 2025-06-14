"""
API 의존성 주입
"""
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_async_db as get_db
from app.core.security import get_current_user_from_firebase
from app.services.ai_service import AIAnalysisService
from app.services.emotion_service import EmotionAnalysisService
from app.services.personality_service import PersonalityAnalysisService
from app.services.matching_service import MatchingService


# 데이터베이스 세션 의존성
async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 의존성"""
    async for session in get_db():
        yield session


# 사용자 인증 의존성
async def get_current_user():
    """현재 사용자 의존성"""
    return Depends(get_current_user_from_firebase)


# 서비스 의존성들
def get_ai_service() -> AIAnalysisService:
    """AI 분석 서비스 의존성"""
    return AIAnalysisService()


def get_emotion_service() -> EmotionAnalysisService:
    """감정 분석 서비스 의존성"""
    return EmotionAnalysisService()


def get_personality_service() -> PersonalityAnalysisService:
    """성격 분석 서비스 의존성"""
    return PersonalityAnalysisService()


def get_matching_service() -> MatchingService:
    """매칭 서비스 의존성"""
    return MatchingService()


# 권한 확인 의존성
class RequirePermissions:
    """권한 확인 클래스"""
    
    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions
    
    def __call__(self, current_user=Depends(get_current_user_from_firebase)):
        user_permissions = current_user.get("permissions", [])
        
        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"권한이 부족합니다: {permission}"
                )
        
        return current_user


# 관리자 권한 확인
require_admin = RequirePermissions(["admin"])


# Rate Limiting을 위한 의존성
class RateLimiter:
    """Rate Limiting 의존성"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def __call__(self, current_user=Depends(get_current_user_from_firebase)):
        # TODO: Redis를 사용한 Rate Limiting 구현
        # 현재는 단순히 사용자 정보만 반환
        return current_user


# 기본 Rate Limiter
default_rate_limiter = RateLimiter()


# 페이지네이션 의존성
class Pagination:
    """페이지네이션 의존성"""
    
    def __init__(self, page: int = 1, size: int = 20, max_size: int = 100):
        self.page = max(1, page)
        self.size = min(max(1, size), max_size)
        self.offset = (self.page - 1) * self.size
    
    def __dict__(self):
        return {
            "page": self.page,
            "size": self.size,
            "offset": self.offset
        }


def get_pagination(page: int = 1, size: int = 20) -> Pagination:
    """페이지네이션 파라미터 의존성"""
    return Pagination(page=page, size=size)


# 검색 파라미터 의존성
class SearchParams:
    """검색 파라미터"""
    
    def __init__(
        self,
        query: str = "",
        start_date: str = None,
        end_date: str = None,
        tags: list = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.query = query.strip() if query else ""
        self.start_date = start_date
        self.end_date = end_date
        self.tags = tags or []
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order in ["asc", "desc"] else "desc"


def get_search_params(
    query: str = "",
    start_date: str = None,
    end_date: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> SearchParams:
    """검색 파라미터 의존성"""
    return SearchParams(
        query=query,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )
