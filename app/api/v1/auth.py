"""
인증 관련 API 엔드포인트
"""
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import (
    create_access_token,
    get_current_user_from_firebase,
    get_current_user_from_jwt,
    verify_firebase_token,
)
from app.schemas.user import UserResponse, TokenResponse

router = APIRouter()
security = HTTPBearer()


@router.post("/verify-token", response_model=TokenResponse)
async def verify_firebase_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Firebase ID 토큰 검증 및 내부 JWT 토큰 발급
    """
    try:
        # Firebase 토큰 검증
        firebase_token = credentials.credentials
        decoded_token = await verify_firebase_token(firebase_token)
        
        # 내부 JWT 토큰 생성
        access_token = create_access_token(
            data={
                "sub": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_info={
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "email_verified": decoded_token.get("email_verified", False),
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    JWT 토큰 갱신 - 기존 JWT 토큰으로 새로운 JWT 토큰 발급
    """
    try:
        # JWT 토큰으로 사용자 정보 추출
        user = await get_current_user_from_jwt(credentials)
        
        # 새로운 액세스 토큰 생성
        new_access_token = create_access_token(
            data={
                "sub": user["user_id"],
                "email": user.get("email"),
                "name": user.get("name"),
            }
        )
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            user_info={
                "uid": user["user_id"],
                "email": user.get("email"),
                "name": user.get("name"),
                "email_verified": True,  # JWT 토큰에서는 이미 검증됨
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: Dict = Depends(get_current_user_from_jwt)
):
    """
    현재 로그인된 사용자 정보 조회
    """
    return UserResponse(
        uid=current_user["user_id"],
        email=current_user.get("email"),
        name=current_user.get("name"),
        picture=None,  # JWT에는 picture 정보 없음
        email_verified=True,  # JWT 토큰이면 이미 검증됨
    )


@router.post("/logout")
async def logout():
    """
    로그아웃 (클라이언트에서 토큰 제거 필요)
    """
    return {
        "message": "Successfully logged out",
        "detail": "Please remove the token from client storage"
    }


@router.get("/validate")
async def validate_token(
    current_user: Dict = Depends(get_current_user_from_jwt)
):
    """
    JWT 토큰 유효성 검증
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user.get("email")
    }
