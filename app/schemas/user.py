"""
사용자 관련 Pydantic 스키마 - Firebase 중심으로 단순화
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """사용자 기본 정보"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    """사용자 생성 스키마 (Firebase에서는 사용 안함)"""
    pass


class UserUpdate(UserBase):
    """사용자 업데이트 스키마"""
    pass


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    uid: str
    email_verified: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """토큰 응답 스키마 (Firebase 토큰용)"""
    message: str
    user: dict
    token_type: str = "firebase_id_token"
    expires_at: Optional[int] = None
    issued_at: Optional[int] = None


class FirebaseUser(BaseModel):
    """Firebase 사용자 정보 (간단한 형태)"""
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False
    provider: Optional[str] = None
    firebase_claims: dict = {}
    
    
class AuthRequest(BaseModel):
    """인증 요청 스키마"""
    token: str
    

class CustomTokenRequest(BaseModel):
    """커스텀 토큰 생성 요청"""
    uid: str
    claims: Optional[dict] = {}
