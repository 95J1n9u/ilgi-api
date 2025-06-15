"""
Firebase Admin SDK 기반 보안 시스템
python-jose 제거하고 Firebase만 사용
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from app.config.settings import get_settings
from app.core.exceptions import AuthenticationException

settings = get_settings()
logger = logging.getLogger(__name__)

# Password 해싱 (Firebase 연동 시 필요시에만)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 토큰 스키마
security = HTTPBearer()

# Firebase Admin SDK 초기화 상태
firebase_initialized = False
firebase_app = None


def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    global firebase_initialized, firebase_app
    
    if firebase_initialized:
        logger.info("🔥 Firebase already initialized")
        return True
    
    # Firebase 환경변수 확인
    required_vars = [
        settings.FIREBASE_PROJECT_ID,
        settings.FIREBASE_PRIVATE_KEY,
        settings.FIREBASE_CLIENT_EMAIL,
    ]
    
    if not all(required_vars):
        logger.warning("⚠️ Firebase configuration incomplete - running without Firebase")
        return False
    
    if not settings.USE_FIREBASE:
        logger.info("ℹ️ Firebase disabled in settings")
        return False
    
    try:
        # Firebase 앱이 이미 있는지 확인
        if not firebase_admin._apps:
            # 서비스 계정 정보 상세 로깅
            logger.info(f"🔧 Firebase 초기화 시도...")
            logger.info(f"📊 Project ID: {settings.FIREBASE_PROJECT_ID}")
            logger.info(f"📧 Client Email: {settings.FIREBASE_CLIENT_EMAIL}")
            logger.info(f"🔑 Private Key ID: {settings.FIREBASE_PRIVATE_KEY_ID}")
            logger.info(f"🔑 Private Key Length: {len(settings.FIREBASE_PRIVATE_KEY) if settings.FIREBASE_PRIVATE_KEY else 0}")
            logger.info(f"🆔 Client ID: {settings.FIREBASE_CLIENT_ID}")
            
            firebase_cred = credentials.Certificate({
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\\\n', '\n').replace('\\n', '\n'),  # 개행 문자 처리
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}",
            })
            
            # 서비스 계정 자격 증명이 올바른지 테스트
            try:
                # 임시로 프로젝트 정보 확인
                firebase_app = firebase_admin.initialize_app(firebase_cred)
                
                # Firebase Admin SDK 버전 및 프로젝트 정보 로깅
                logger.info(f"🔥 Firebase Admin SDK 버전: {firebase_admin.__version__ if hasattr(firebase_admin, '__version__') else 'Unknown'}")
                logger.info(f"🏗️ 초기화된 프로젝트: {firebase_app.project_id}")
                
                firebase_initialized = True
                logger.info("✅ Firebase Admin SDK initialized successfully")
                
                # 간단한 토큰 검증 테스트 (선택사항)
                try:
                    # 더미 토큰으로 검증 시도해서 서비스가 정상인지 확인
                    logger.info("🧪 Firebase 서비스 상태 테스트 중...")
                    # auth.verify_id_token("dummy")  # 의도적으로 실패하게 하여 서비스 상태만 확인
                except Exception as test_error:
                    if "Could not parse" in str(test_error) or "Invalid" in str(test_error):
                        logger.info("✅ Firebase 서비스가 응답하고 있음 (예상된 오류)")
                    else:
                        logger.warning(f"⚠️ Firebase 서비스 문제 가능성: {test_error}")
                
                return True
                
            except Exception as init_error:
                logger.error(f"❌ Firebase 초기화 세부 오류: {str(init_error)}")
                logger.error(f"   오류 타입: {type(init_error).__name__}")
                
                # 일반적인 오류들에 대한 구체적인 가이드
                error_str = str(init_error).lower()
                if "private_key" in error_str:
                    logger.error("🔑 Private Key 형식 문제일 가능성이 높습니다!")
                    logger.error("   - Railway 환경변수에서 private_key 확인 필요")
                    logger.error("   - \\n이 실제 개행문자로 변환되는지 확인 필요")
                elif "project_id" in error_str:
                    logger.error("🏗️ Project ID 불일치 문제일 가능성이 높습니다!")
                elif "client_email" in error_str:
                    logger.error("📧 Service Account Email 문제일 가능성이 높습니다!")
                    logger.error("   - Firebase Console에서 서비스 계정 존재 여부 확인")
                elif "permission" in error_str or "access" in error_str:
                    logger.error("🚫 권한 문제일 가능성이 높습니다!")
                    logger.error("   - 서비스 계정에 Firebase Admin SDK 권한 부여 필요")
                else:
                    logger.error("❓ 알 수 없는 초기화 오류입니다.")
                
                firebase_initialized = False
                return False
        else:
            firebase_initialized = True
            logger.info("✅ Firebase Admin SDK already exists")
            return True
            
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        firebase_initialized = False
        return False


# 시작 시 Firebase 초기화 시도
initialize_firebase()


async def verify_firebase_token(token: str) -> Dict[str, Any]:
    """Firebase ID 토큰 검증"""
    logger.info(f"🔍 Firebase 토큰 검증 시작: {token[:30]}...")
    
    if not firebase_initialized:
        logger.error("❌ Firebase not initialized")
        raise AuthenticationException("Firebase authentication service is not available")
    
    try:
        # 토큰 정제 - 공백 제거 및 Base64 패딩 문제 해결
        clean_token = token.strip()
        
        # 토큰 기본 정보 로깅
        logger.info(f"🎫 토큰 길이: {len(clean_token)}")
        logger.info(f"🎫 토큰 부분 개수: {len(clean_token.split('.'))}")
        
        # JWT 토큰은 3개 부분으로 구성되어야 함
        token_parts = clean_token.split('.')
        if len(token_parts) != 3:
            logger.error(f"❌ 잘못된 토큰 형식: {len(token_parts)}개 부분 (정상: 3개)")
            raise AuthenticationException(f"Invalid token format: expected 3 parts, got {len(token_parts)}")
        
        # 토큰 헤더 디코딩하여 프로젝트 정보 확인
        try:
            import base64
            import json
            header_data = token_parts[0]
            # Base64 패딩 추가
            while len(header_data) % 4 != 0:
                header_data += '='
            header = json.loads(base64.b64decode(header_data))
            logger.info(f"🔍 토큰 헤더: {header}")
        except Exception as e:
            logger.warning(f"⚠️ 토큰 헤더 디코딩 실패: {e}")
        
        # 토큰 페이로드 디코딩하여 발급자(iss) 확인
        try:
            payload_data = token_parts[1]
            while len(payload_data) % 4 != 0:
                payload_data += '='
            payload = json.loads(base64.b64decode(payload_data))
            logger.info(f"🔍 토큰 발급자(iss): {payload.get('iss', 'N/A')}")
            logger.info(f"🔍 토큰 대상(aud): {payload.get('aud', 'N/A')}")
            logger.info(f"🔍 토큰 만료시간: {payload.get('exp', 'N/A')}")
            
            # 현재 백엔드 Firebase 설정 정보 로깅
            from app.config.settings import get_settings
            settings = get_settings()
            logger.info(f"🏗️ 백엔드 Firebase Project ID: {settings.FIREBASE_PROJECT_ID}")
            
            # 프로젝트 ID 일치 여부 확인
            expected_aud = f"projects/{settings.FIREBASE_PROJECT_ID}"
            if settings.FIREBASE_PROJECT_ID and payload.get('aud') != settings.FIREBASE_PROJECT_ID:
                logger.error(f"❌ 프로젝트 ID 불일치!")
                logger.error(f"   토큰 aud: {payload.get('aud')}")
                logger.error(f"   백엔드 설정: {settings.FIREBASE_PROJECT_ID}")
                
        except Exception as e:
            logger.warning(f"⚠️ 토큰 페이로드 디코딩 실패: {e}")
        
        # 각 부분의 길이 확인 및 패딩 추가 (필요한 경우)
        padded_parts = []
        for i, part in enumerate(token_parts):
            # Base64 패딩 추가 (길이가 4의 배수가 되도록)
            while len(part) % 4 != 0:
                part += '='
            padded_parts.append(part)
            logger.info(f"🔧 Part {i}: 원본 길이 {len(token_parts[i])}, 패딩 후 길이 {len(part)}")
        
        # 패딩이 추가된 토큰 재구성
        padded_token = '.'.join(padded_parts)
        
        # Firebase Admin SDK로 토큰 검증
        logger.info(f"🔥 Firebase Admin SDK 토큰 검증 시도...")
        decoded_token = auth.verify_id_token(padded_token)
        logger.info(f"✅ Firebase 토큰 검증 성공: uid={decoded_token.get('uid')}")
        return decoded_token
        
    except auth.InvalidIdTokenError as e:
        logger.error(f"❌ Invalid Firebase token: {str(e)}")
        raise AuthenticationException(f"Invalid Firebase token: {str(e)}")
    except auth.ExpiredIdTokenError as e:
        logger.error(f"❌ Expired Firebase token: {str(e)}")
        raise AuthenticationException(f"Expired Firebase token: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Firebase token verification failed: {str(e)}")
        raise AuthenticationException(f"Firebase token verification failed: {str(e)}")


async def create_custom_token(uid: str, additional_claims: Optional[Dict] = None) -> str:
    """Firebase 커스텀 토큰 생성"""
    if not firebase_initialized:
        raise AuthenticationException("Firebase authentication service is not available")
    
    try:
        custom_token = auth.create_custom_token(uid, additional_claims)
        return custom_token.decode('utf-8')
    except Exception as e:
        logger.error(f"❌ Custom token creation failed: {str(e)}")
        raise AuthenticationException(f"Custom token creation failed: {str(e)}")


def get_user_from_token(decoded_token: Dict[str, Any]) -> Dict[str, Any]:
    """Firebase 토큰에서 사용자 정보 추출"""
    return {
        "uid": decoded_token["uid"],
        "email": decoded_token.get("email"),
        "name": decoded_token.get("name"),
        "picture": decoded_token.get("picture"),
        "email_verified": decoded_token.get("email_verified", False),
        "firebase_claims": decoded_token.get("firebase", {}),
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Firebase 토큰으로부터 현재 사용자 정보 추출"""
    try:
        token = credentials.credentials
        logger.info(f"🔍 사용자 인증 시작: {token[:30]}...")
        
        # 개발 환경에서 테스트 토큰 허용
        if settings.DEBUG and token == "test-token-for-development":
            logger.info("🧪 개발 모드: 테스트 토큰 사용")
            return {
                "uid": "test-user-123",
                "email": "test@example.com",
                "name": "Test User",
                "picture": None,
                "email_verified": True,
                "firebase_claims": {},
            }
        
        # Firebase가 비활성화된 경우
        if not firebase_initialized:
            logger.error("❌ Firebase 서비스 비활성화")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase authentication service is not available. Please contact administrator.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Firebase 토큰 검증
        decoded_token = await verify_firebase_token(token)
        user_info = get_user_from_token(decoded_token)
        
        logger.info(f"✅ 사용자 인증 성공: {user_info['uid']}")
        return user_info
        
    except HTTPException:
        raise  # HTTPException은 그대로 전달
    except AuthenticationException as e:
        logger.error(f"❌ 인증 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"❌ 인증 예외: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RoleChecker:
    """역할 기반 권한 체크"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: Dict[str, Any] = Depends(get_current_user)):
        user_role = user.get("firebase_claims", {}).get("role", "user")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user


# 권한 체크 인스턴스들
require_admin = RoleChecker(["admin"])
require_user = RoleChecker(["user", "admin"])


# 유틸리티 함수들
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


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


# Firebase 서비스 상태 확인
def get_firebase_status() -> Dict[str, Any]:
    """Firebase 서비스 상태 반환"""
    return {
        "initialized": firebase_initialized,
        "use_firebase": settings.USE_FIREBASE,
        "project_id": settings.FIREBASE_PROJECT_ID[:10] + "..." if settings.FIREBASE_PROJECT_ID else None,
        "client_email": settings.FIREBASE_CLIENT_EMAIL[:20] + "..." if settings.FIREBASE_CLIENT_EMAIL else None,
    }



