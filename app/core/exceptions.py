"""
커스텀 예외 처리
"""
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import structlog

logger = structlog.get_logger()


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


class AuthenticationException(CustomHTTPException):
    """인증 관련 예외"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_FAILED"
        )


class AuthorizationException(CustomHTTPException):
    """권한 관련 예외"""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="INSUFFICIENT_PERMISSIONS"
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
            error_code="RATE_LIMIT_EXCEEDED"
        )


class AIAnalysisError(CustomHTTPException):
    """AI 분석 오류"""
    
    def __init__(self, detail: str = "AI analysis failed"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="AI_ANALYSIS_FAILED"
        )


def add_exception_handlers(app: FastAPI) -> None:
    """예외 핸들러 등록"""
    
    @app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: CustomHTTPException
    ) -> JSONResponse:
        """커스텀 HTTP 예외 핸들러"""
        logger.error(
            "custom_http_exception",
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=exc.error_code,
            url=str(request.url),
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code or "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
            },
            headers=exc.headers,
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Pydantic 검증 오류 핸들러"""
        logger.error(
            "validation_error",
            errors=exc.errors(),
            url=str(request.url),
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
            },
        )
    
    @app.exception_handler(DatabaseException)
    async def database_exception_handler(
        request: Request, exc: DatabaseException
    ) -> JSONResponse:
        """데이터베이스 예외 핸들러"""
        logger.error(
            "database_error",
            exception=str(exc),
            url=str(request.url),
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "DATABASE_ERROR",
                "message": "Database operation failed",
            },
        )
    
    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(
        request: Request, exc: AIServiceException
    ) -> JSONResponse:
        """AI 서비스 예외 핸들러"""
        logger.error(
            "ai_service_error",
            exception=str(exc),
            url=str(request.url),
        )
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "AI_SERVICE_ERROR",
                "message": "AI service is temporarily unavailable",
            },
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """글로벌 예외 핸들러"""
        logger.error(
            "unhandled_exception",
            exception=str(exc),
            exception_type=type(exc).__name__,
            url=str(request.url),
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            },
        )
