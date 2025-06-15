"""
커스텀 예외 처리 - Firebase Admin SDK 중심
"""
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    """커스텀 HTTP 예외"""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(status_code, detail, headers)
        self.error_code = error_code


class DatabaseException(Exception):
    """데이터베이스 관련 예외"""
    pass


class AIServiceException(Exception):
    """AI 서비스 관련 예외"""
    pass


class FirebaseException(Exception):
    """Firebase 관련 예외"""
    pass


class AuthenticationException(CustomHTTPException):
    """인증 관련 예외 - Firebase 기반"""
    
    def __init__(self, detail: str = "Firebase authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="FIREBASE_AUTH_FAILED",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(CustomHTTPException):
    """권한 관련 예외"""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="INSUFFICIENT_PERMISSIONS"
        )


class FirebaseServiceUnavailableException(CustomHTTPException):
    """Firebase 서비스 비활성화 예외"""
    
    def __init__(self, detail: str = "Firebase authentication service is not available"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="FIREBASE_SERVICE_UNAVAILABLE"
        )


class InvalidFirebaseTokenException(CustomHTTPException):
    """Firebase 토큰 오류"""
    
    def __init__(self, detail: str = "Invalid Firebase token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_FIREBASE_TOKEN",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ExpiredFirebaseTokenException(CustomHTTPException):
    """Firebase 토큰 만료"""
    
    def __init__(self, detail: str = "Firebase token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="EXPIRED_FIREBASE_TOKEN",
            headers={"WWW-Authenticate": "Bearer"}
        )


class NotFoundError(CustomHTTPException):
    """리소스를 찾을 수 없음"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND"
        )


class ValidationError(CustomHTTPException):
    """데이터 검증 오류"""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class RateLimitError(CustomHTTPException):
    """Rate Limit 초과"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            headers={"Retry-After": "3600"}  # 1시간 후 재시도
        )


class AIAnalysisError(CustomHTTPException):
    """AI 분석 오류"""
    
    def __init__(self, detail: str = "AI analysis failed"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="AI_ANALYSIS_FAILED"
        )


class GeminiAPIError(CustomHTTPException):
    """Gemini API 오류"""
    
    def __init__(self, detail: str = "Gemini API service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="GEMINI_API_ERROR"
        )


class UserNotFoundError(CustomHTTPException):
    """사용자를 찾을 수 없음"""
    
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="USER_NOT_FOUND"
        )


class DiaryNotFoundError(CustomHTTPException):
    """일기를 찾을 수 없음"""
    
    def __init__(self, detail: str = "Diary entry not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="DIARY_NOT_FOUND"
        )


class AnalysisNotFoundError(CustomHTTPException):
    """분석 결과를 찾을 수 없음"""
    
    def __init__(self, detail: str = "Analysis result not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="ANALYSIS_NOT_FOUND"
        )


def add_exception_handlers(app: FastAPI) -> None:
    """예외 핸들러 등록 - Firebase 관련 예외 포함"""
    
    @app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: CustomHTTPException
    ) -> JSONResponse:
        """커스텀 HTTP 예외 핸들러"""
        logger.error(
            f"❌ Custom HTTP Exception: {exc.error_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "url": str(request.url),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code or "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": "2025-06-14T15:00:00Z"
            },
            headers=exc.headers,
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Pydantic 검증 오류 핸들러"""
        logger.error(
            f"❌ Validation Error: {str(exc)}",
            extra={
                "url": str(request.url),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": str(exc),
                "timestamp": "2025-06-14T15:00:00Z"
            },
        )
    
    @app.exception_handler(FirebaseException)
    async def firebase_exception_handler(
        request: Request, exc: FirebaseException
    ) -> JSONResponse:
        """Firebase 예외 핸들러"""
        logger.error(
            f"❌ Firebase Error: {str(exc)}",
            extra={
                "url": str(request.url),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "FIREBASE_ERROR",
                "message": "Firebase service error",
                "details": str(exc),
                "timestamp": "2025-06-14T15:00:00Z"
            },
        )
    
    @app.exception_handler(DatabaseException)
    async def database_exception_handler(
        request: Request, exc: DatabaseException
    ) -> JSONResponse:
        """데이터베이스 예외 핸들러"""
        logger.error(
            f"❌ Database Error: {str(exc)}",
            extra={
                "url": str(request.url),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "DATABASE_ERROR",
                "message": "Database operation failed",
                "timestamp": "2025-06-14T15:00:00Z"
            },
        )
    
    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(
        request: Request, exc: AIServiceException
    ) -> JSONResponse:
        """AI 서비스 예외 핸들러"""
        logger.error(
            f"❌ AI Service Error: {str(exc)}",
            extra={
                "url": str(request.url),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "AI_SERVICE_ERROR",
                "message": "AI service is temporarily unavailable",
                "details": str(exc),
                "timestamp": "2025-06-14T15:00:00Z"
            },
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """글로벌 예외 핸들러"""
        logger.error(
            f"❌ Unhandled Exception: {type(exc).__name__} - {str(exc)}",
            extra={
                "exception_type": type(exc).__name__,
                "url": str(request.url),
                "method": request.method
            }
        )
        
        # 개발 환경에서는 상세한 오류 정보 제공
        from app.config.settings import get_settings
        settings = get_settings()
        
        error_details = {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": "2025-06-14T15:00:00Z"
        }
        
        # 디버그 모드에서는 상세 오류 정보 포함
        if settings.DEBUG:
            error_details["debug_info"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc)
            }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_details,
        )
    
    # HTTP 예외 핸들러 (기본 FastAPI HTTPException)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """기본 HTTP 예외 핸들러"""
        logger.warning(
            f"⚠️ HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "url": str(request.url),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": "2025-06-14T15:00:00Z"
            },
            headers=getattr(exc, 'headers', None),
        )


# 예외 헬퍼 함수들
def raise_firebase_auth_error(detail: str):
    """Firebase 인증 오류 발생"""
    raise AuthenticationException(detail)


def raise_firebase_service_unavailable():
    """Firebase 서비스 비활성화 오류 발생"""
    raise FirebaseServiceUnavailableException()


def raise_invalid_firebase_token(detail: str):
    """Firebase 토큰 오류 발생"""
    raise InvalidFirebaseTokenException(detail)


def raise_expired_firebase_token():
    """Firebase 토큰 만료 오류 발생"""
    raise ExpiredFirebaseTokenException()


def raise_user_not_found(user_uid: str):
    """사용자를 찾을 수 없음 오류 발생"""
    raise UserNotFoundError(f"User with UID '{user_uid}' not found")


def raise_diary_not_found(diary_id: str):
    """일기를 찾을 수 없음 오류 발생"""
    raise DiaryNotFoundError(f"Diary with ID '{diary_id}' not found")


def raise_analysis_not_found(analysis_id: str):
    """분석 결과를 찾을 수 없음 오류 발생"""
    raise AnalysisNotFoundError(f"Analysis with ID '{analysis_id}' not found")


def raise_insufficient_permissions(required_role: str):
    """권한 부족 오류 발생"""
    raise AuthorizationException(f"Required role: {required_role}")


def raise_ai_service_error(service_name: str, error_detail: str):
    """AI 서비스 오류 발생"""
    raise AIServiceException(f"{service_name} error: {error_detail}")


def raise_gemini_api_error(error_detail: str):
    """Gemini API 오류 발생"""
    raise GeminiAPIError(f"Gemini API error: {error_detail}")
