"""
Firebase Admin SDK 기반 인증 API
python-jose 제거하고 Firebase만 사용
"""
import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import (
    get_current_user,
    verify_firebase_token,
    create_custom_token,
    get_firebase_status,
    firebase_initialized,
)
from app.schemas.user import UserResponse

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


@router.post("/verify-token")
async def verify_firebase_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Firebase ID 토큰 검증 및 사용자 정보 반환
    """
    try:
        logger.info("🔍 Firebase 토큰 검증 API 호출")
        
        # Firebase 토큰 검증
        firebase_token = credentials.credentials
        decoded_token = await verify_firebase_token(firebase_token)
        
        # 사용자 정보 반환 (Firebase 토큰 자체가 인증 수단)
        user_info = {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "email_verified": decoded_token.get("email_verified", False),
            "provider": decoded_token.get("firebase", {}).get("sign_in_provider"),
        }
        
        logger.info(f"✅ Firebase 토큰 검증 성공: {user_info['uid']}")
        
        return {
            "message": "Token verified successfully",
            "user": user_info,
            "token_type": "firebase_id_token",
            "expires_at": decoded_token.get("exp"),
            "issued_at": decoded_token.get("iat"),
        }
        
    except Exception as e:
        logger.error(f"❌ Firebase 토큰 검증 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh")
async def refresh_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Firebase ID 토큰 갱신 (클라이언트에서 Firebase SDK로 처리)
    """
    try:
        logger.info("🔄 Firebase 토큰 갱신 요청")
        
        # 현재 토큰 검증
        current_user = await get_current_user(credentials)
        
        # Firebase에서는 클라이언트가 직접 토큰을 갱신해야 함
        return {
            "message": "Token refresh should be handled by Firebase SDK on client side",
            "user_uid": current_user["uid"],
            "instruction": "Call firebase.auth().currentUser.getIdToken(true) to get fresh token",
            "current_token_valid": True,
        }
        
    except Exception as e:
        logger.error(f"❌ Firebase 토큰 갱신 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/custom-token")
async def create_firebase_custom_token(
    user_data: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """
    Firebase 커스텀 토큰 생성 (관리자 전용)
    """
    try:
        logger.info("🎫 Firebase 커스텀 토큰 생성 요청")
        
        # 관리자 권한 확인 (간단한 구현)
        if current_user.get("email") not in ["admin@example.com"]:  # 실제 환경에서는 적절한 권한 체크 필요
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        uid = user_data.get("uid")
        additional_claims = user_data.get("claims", {})
        
        custom_token = await create_custom_token(uid, additional_claims)
        
        return {
            "custom_token": custom_token,
            "uid": uid,
            "claims": additional_claims,
        }
        
    except Exception as e:
        logger.error(f"❌ 커스텀 토큰 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Custom token creation failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user)
):
    """
    현재 로그인된 사용자 정보 조회
    """
    logger.info(f"👤 사용자 정보 조회: {current_user['uid']}")
    
    return UserResponse(
        uid=current_user["uid"],
        email=current_user.get("email"),
        name=current_user.get("name"),
        picture=current_user.get("picture"),
        email_verified=current_user.get("email_verified", False),
    )


@router.post("/logout")
async def logout():
    """
    로그아웃 (클라이언트에서 Firebase SDK로 처리)
    """
    return {
        "message": "Logout should be handled by Firebase SDK on client side",
        "instruction": "Call firebase.auth().signOut() to logout user",
        "server_action": "No server-side session to clear"
    }


@router.get("/validate")
async def validate_firebase_token(
    current_user: Dict = Depends(get_current_user)
):
    """
    Firebase 토큰 유효성 검증
    """
    logger.info(f"✅ 토큰 유효성 검증: {current_user['uid']}")
    
    return {
        "valid": True,
        "uid": current_user["uid"],
        "email": current_user.get("email"),
        "email_verified": current_user.get("email_verified"),
        "provider": current_user.get("firebase_claims", {}).get("sign_in_provider"),
    }


@router.get("/status")
async def get_auth_status():
    """
    Firebase 인증 서비스 상태 확인
    """
    firebase_status = get_firebase_status()
    
    return {
        "service": "Firebase Authentication",
        "status": "operational" if firebase_initialized else "unavailable",
        "firebase_config": firebase_status,
        "available_endpoints": [
            "/verify-token - Firebase ID 토큰 검증",
            "/refresh - 토큰 갱신 안내",
            "/me - 사용자 정보 조회",
            "/validate - 토큰 유효성 검증",
            "/logout - 로그아웃 안내",
            "/status - 서비스 상태 확인",
        ]
    }
