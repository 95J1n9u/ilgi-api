"""
API v1 라우터 통합
"""
from fastapi import APIRouter

from app.api.v1 import analysis, auth, matching

api_router = APIRouter()

# 각 모듈의 라우터 포함
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["AI 분석"])
api_router.include_router(matching.router, prefix="/matching", tags=["매칭"])


@api_router.get("/")
async def api_root():
    """API v1 루트"""
    return {
        "message": "AI Diary Analysis API v1",
        "endpoints": {
            "auth": "/auth",
            "analysis": "/analysis", 
            "matching": "/matching"
        }
    }
