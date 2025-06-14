"""
사용자 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """사용자 기본 정보"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    firebase_uid: str = Field(..., description="Firebase UID")
    email: EmailStr = Field(..., description="이메일 주소")
    name: str = Field(..., description="사용자 이름")


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 스키마"""
    name: Optional[str] = None
    picture: Optional[str] = None


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    uid: str = Field(..., description="사용자 고유 ID")
    email_verified: bool = Field(default=False, description="이메일 인증 여부")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """데이터베이스 사용자 스키마"""
    id: str
    firebase_uid: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""
    access_token: str = Field(..., description="액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: Optional[int] = Field(None, description="만료 시간(초)")
    user_info: Optional[dict] = Field(None, description="사용자 정보")


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    firebase_token: str = Field(..., description="Firebase ID 토큰")


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청 스키마"""
    refresh_token: str = Field(..., description="갱신 토큰")


class UserProfile(BaseModel):
    """사용자 프로필 스키마"""
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    interests: Optional[list] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    """사용자 설정 스키마"""
    notifications_enabled: bool = Field(default=True)
    email_notifications: bool = Field(default=True)
    matching_enabled: bool = Field(default=True)
    profile_visibility: str = Field(default="public")  # public, friends, private
    language: str = Field(default="ko")
    timezone: str = Field(default="Asia/Seoul")
