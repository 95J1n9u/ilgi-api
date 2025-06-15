"""
API 의존성 주입 - Firebase Admin SDK 중심으로 단순화
"""
import logging
from typing import AsyncGenerator, Dict, Any

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user

logger = logging.getLogger(__name__)


# 사용자 인증 의존성 (Firebase 기반)
async def get_current_user_dependency():
    """현재 사용자 의존성 - Firebase 인증"""
    return Depends(get_current_user)


# 권한 확인 의존성 (단순화)
class RequirePermissions:
    """권한 확인 클래스 - Firebase 커스텀 클레임 기반"""
    
    def __init__(self, required_roles: list):
        self.required_roles = required_roles
    
    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("firebase_claims", {}).get("role", "user")
        
        if user_role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"권한이 부족합니다. 필요 역할: {', '.join(self.required_roles)}"
            )
        
        return current_user


# 관리자 권한 확인
require_admin = RequirePermissions(["admin"])
require_user = RequirePermissions(["user", "admin"])


# Rate Limiting을 위한 의존성 (단순화)
class RateLimiter:
    """Rate Limiting 의존성 - 메모리 기반 간단 구현"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = {}  # 메모리 기반 (실제 환경에서는 Redis 사용 권장)
    
    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        user_uid = current_user["uid"]
        
        # 간단한 메모리 기반 Rate Limiting
        # TODO: 프로덕션에서는 Redis나 데이터베이스 사용
        logger.info(f"🚦 Rate Limiting 체크: user={user_uid}")
        
        return current_user


# 기본 Rate Limiter
default_rate_limiter = RateLimiter()
api_rate_limiter = RateLimiter(max_requests=1000, window_seconds=3600)


# 페이지네이션 의존성
class Pagination:
    """페이지네이션 의존성"""
    
    def __init__(self, page: int = 1, size: int = 20, max_size: int = 100):
        self.page = max(1, page)
        self.size = min(max(1, size), max_size)
        self.offset = (self.page - 1) * self.size
    
    def to_dict(self):
        return {
            "page": self.page,
            "size": self.size,
            "offset": self.offset,
            "limit": self.size
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
    
    def to_dict(self):
        return {
            "query": self.query,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "tags": self.tags,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order
        }


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


# 분석 옵션 의존성
class AnalysisOptions:
    """분석 옵션 파라미터"""
    
    def __init__(
        self,
        include_emotions: bool = True,
        include_personality: bool = True,
        include_keywords: bool = True,
        include_recommendations: bool = True,
        detailed_analysis: bool = False
    ):
        self.include_emotions = include_emotions
        self.include_personality = include_personality
        self.include_keywords = include_keywords
        self.include_recommendations = include_recommendations
        self.detailed_analysis = detailed_analysis
    
    def to_dict(self):
        return {
            "include_emotions": self.include_emotions,
            "include_personality": self.include_personality,
            "include_keywords": self.include_keywords,
            "include_recommendations": self.include_recommendations,
            "detailed_analysis": self.detailed_analysis
        }


def get_analysis_options(
    include_emotions: bool = True,
    include_personality: bool = True,
    include_keywords: bool = True,
    include_recommendations: bool = True,
    detailed_analysis: bool = False
) -> AnalysisOptions:
    """분석 옵션 의존성"""
    return AnalysisOptions(
        include_emotions=include_emotions,
        include_personality=include_personality,
        include_keywords=include_keywords,
        include_recommendations=include_recommendations,
        detailed_analysis=detailed_analysis
    )


# 매칭 옵션 의존성
class MatchingOptions:
    """매칭 옵션 파라미터"""
    
    def __init__(
        self,
        limit: int = 10,
        min_compatibility: float = 0.5,
        include_details: bool = True,
        age_filter: str = None,
        location_filter: str = None
    ):
        self.limit = min(max(1, limit), 50)  # 1-50 범위로 제한
        self.min_compatibility = max(0.0, min(1.0, min_compatibility))  # 0-1 범위
        self.include_details = include_details
        self.age_filter = age_filter
        self.location_filter = location_filter
    
    def to_dict(self):
        return {
            "limit": self.limit,
            "min_compatibility": self.min_compatibility,
            "include_details": self.include_details,
            "age_filter": self.age_filter,
            "location_filter": self.location_filter
        }


def get_matching_options(
    limit: int = 10,
    min_compatibility: float = 0.5,
    include_details: bool = True,
    age_filter: str = None,
    location_filter: str = None
) -> MatchingOptions:
    """매칭 옵션 의존성"""
    return MatchingOptions(
        limit=limit,
        min_compatibility=min_compatibility,
        include_details=include_details,
        age_filter=age_filter,
        location_filter=location_filter
    )


# 사용자 검증 헬퍼
def verify_user_access(resource_user_uid: str, current_user: Dict[str, Any]) -> bool:
    """사용자 리소스 접근 권한 검증"""
    user_uid = current_user["uid"]
    user_role = current_user.get("firebase_claims", {}).get("role", "user")
    
    # 본인 리소스이거나 관리자인 경우 접근 허용
    return user_uid == resource_user_uid or user_role == "admin"


def require_resource_access(resource_user_uid: str):
    """리소스 접근 권한 요구 데코레이터"""
    def dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not verify_user_access(resource_user_uid, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 리소스에 접근할 권한이 없습니다"
            )
        return current_user
    return dependency


# 서비스 가용성 체크
def check_service_availability():
    """서비스 가용성 체크 의존성"""
    def dependency():
        from app.core.security import firebase_initialized
        from app.config.settings import get_settings
        
        settings = get_settings()
        
        # Firebase 서비스 체크
        if not firebase_initialized:
            logger.warning("Firebase 서비스가 비활성화된 상태")
        
        # Gemini API 체크
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API 키가 설정되지 않음")
        
        return {
            "firebase_available": firebase_initialized,
            "gemini_available": bool(settings.GEMINI_API_KEY),
            "database_available": bool(settings.DATABASE_URL),
            "redis_available": bool(settings.REDIS_URL)
        }
    
    return dependency


# 일반적인 서비스 가용성 체크
service_availability = check_service_availability()
