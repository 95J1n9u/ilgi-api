"""
보안 관련 유틸리티
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import get_settings
from app.core.exceptions import AuthenticationException

settings = get_settings()

# Password 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 토큰 스키마
security = HTTPBearer()

# Firebase Admin SDK 초기화 (조건부)
firebase_initialized = False

if not firebase_admin._apps and settings.USE_FIREBASE and settings.FIREBASE_PROJECT_ID:
    try:
        firebase_cred = credentials.Certificate({
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": settings.FIREBASE_AUTH_URI,
            "token_uri": settings.FIREBASE_TOKEN_URI,
        })
        firebase_admin.initialize_app(firebase_cred)
        firebase_initialized = True
        print("✅ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"⚠️ Firebase initialization failed: {e}")
        firebase_initialized = False
else:
    print("ℹ️ Firebase Admin SDK skipped (disabled or missing config)")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def verify_access_token(token: str) -> Dict[str, Any]:
    """JWT 액세스 토큰 검증"""
    try:
        # 디버깅용 로깅
        print(f"🔑 JWT 토큰 검증 시작: {token[:50]}...")
        print(f"🔑 SECRET_KEY 상태: {bool(settings.SECRET_KEY)}")
        print(f"🔑 ALGORITHM: {settings.ALGORITHM}")
        
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        print(f"✅ JWT 토큰 검증 성공: {payload}")
        return payload
        
    except jwt.ExpiredSignatureError:
        print("❌ JWT 토큰 만료")
        raise AuthenticationException("Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"❌ JWT 토큰 오류: {e}")
        raise AuthenticationException(f"Invalid token: {str(e)}")
    except Exception as e:
        print(f"❌ JWT 검증 예외: {e}")
        raise AuthenticationException(f"Token verification failed: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


async def verify_firebase_token(token: str) -> Dict[str, Any]:
    """Firebase ID 토큰 검증"""
    if not firebase_initialized:
        raise AuthenticationException("Firebase authentication is not available")
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise AuthenticationException(f"Firebase token verification failed: {str(e)}")


async def get_current_user_from_firebase(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Firebase 토큰으로부터 현재 사용자 정보 추출"""
    try:
        # Bearer 토큰에서 실제 토큰 추출
        token = credentials.credentials
        
        # 개발 환경에서 Mock 토큰 허용
        if settings.DEBUG and token == "test-token-for-development":
            return {
                "uid": "test-user-123",
                "email": "test@example.com",
                "name": "Test User",
                "picture": None,
                "email_verified": True,
            }
        
        # Firebase가 비활성화된 경우 오류 메시지 개선
        if not firebase_initialized:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase authentication service is not available. Please contact administrator.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 실제 Firebase 토큰 검증
        decoded_token = await verify_firebase_token(token)
        
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "email_verified": decoded_token.get("email_verified", False),
        }
    except HTTPException:
        raise  # HTTPException은 그대로 전달
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_from_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """JWT 토큰으로부터 현재 사용자 정보 추출"""
    try:
        token = credentials.credentials
        print(f"🔍 JWT 사용자 인증 시작: {token[:30]}...")
        
        payload = await verify_access_token(token)
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationException("Invalid token payload: missing user ID")
        
        user_info = {
            "user_id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
        }
        
        print(f"✅ JWT 사용자 인증 성공: {user_info}")
        return user_info
        
    except (JWTError, AuthenticationException) as e:
        print(f"❌ JWT 사용자 인증 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate JWT token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"❌ JWT 사용자 인증 예외: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RoleChecker:
    """역할 기반 권한 체크"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: Dict[str, Any] = Depends(get_current_user_from_firebase)):
        user_role = user.get("role", "user")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user


# 권한 체크 인스턴스들
require_admin = RoleChecker(["admin"])
require_user = RoleChecker(["user", "admin"])


def sanitize_input(text: str) -> str:
    """입력 데이터 정제"""
    if not text:
        return ""
    
    # 기본적인 HTML 태그 제거
    import re
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # 특수 문자 이스케이프
    clean_text = clean_text.replace('<', '&lt;').replace('>', '&gt;')
    
    return clean_text.strip()


def validate_email(email: str) -> bool:
    """이메일 주소 검증"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def generate_api_key() -> str:
    """API 키 생성"""
    import secrets
    return secrets.token_urlsafe(32)
