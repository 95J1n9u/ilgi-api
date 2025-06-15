"""
매칭 관련 Pydantic 스키마 - Firebase 중심으로 단순화
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class MatchingRequest(BaseModel):
    """매칭 요청 스키마 - 단순화"""
    limit: int = Field(default=10, ge=1, le=50, description="추천 후보 수")
    min_compatibility: float = Field(default=0.5, ge=0.0, le=1.0, description="최소 호환성 점수")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="추가 필터")


class CompatibilityRequest(BaseModel):
    """호환성 계산 요청 스키마"""
    target_user_id: str = Field(..., description="상대방 사용자 UID")


class MatchingCandidate(BaseModel):
    """매칭 후보자 정보 - 단순화"""
    user_uid: str = Field(..., description="Firebase 사용자 UID")
    name: str = Field(..., description="표시 이름")
    compatibility_score: float = Field(..., description="호환성 점수")
    common_interests: List[str] = Field(default=[], description="공통 관심사")
    personality_match: str = Field(..., description="성격 매칭 수준")
    age_range: Optional[str] = Field(None, description="나이대")
    distance: Optional[str] = Field(None, description="거리")
    last_active: Optional[str] = Field(None, description="마지막 활동")


class MatchingCandidatesResponse(BaseModel):
    """매칭 후보 목록 응답 - 단순화"""
    user_uid: str = Field(..., description="요청 사용자 UID")
    candidates: List[MatchingCandidate] = Field(..., description="매칭 후보 목록")
    total_count: int = Field(..., description="총 후보자 수")
    filters_applied: Dict[str, Any] = Field(default={}, description="적용된 필터")
    generated_at: str = Field(..., description="생성 시간")


class CompatibilityResponse(BaseModel):
    """호환성 계산 응답 - 단순화"""
    user1_uid: str = Field(..., description="사용자 1 UID")
    user2_uid: str = Field(..., description="사용자 2 UID")
    overall_score: float = Field(..., description="전체 호환성 점수")
    compatibility_breakdown: Dict[str, float] = Field(default={}, description="세부 호환성")
    shared_traits: List[str] = Field(default=[], description="공통 특성")
    complementary_traits: List[str] = Field(default=[], description="상호 보완 특성")
    potential_challenges: List[str] = Field(default=[], description="잠재적 도전과제")
    recommendations: List[str] = Field(default=[], description="관계 개선 제안")
    calculated_at: str = Field(..., description="계산 시간")


class MatchingProfile(BaseModel):
    """매칭용 사용자 프로필 - 단순화"""
    user_uid: str
    display_name: str
    email: Optional[str] = None
    age_range: Optional[str] = None
    location: Optional[str] = None
    personality_summary: Dict[str, Any] = Field(default={})
    interests: List[str] = Field(default=[])
    lifestyle: Dict[str, Any] = Field(default={})
    matching_preferences: Dict[str, Any] = Field(default={})
    recent_activity: Dict[str, Any] = Field(default={})
    privacy_settings: Dict[str, Any] = Field(default={})
    updated_at: str


class MatchingPreferences(BaseModel):
    """매칭 선호도 설정 - 단순화"""
    user_uid: str
    age_range: Dict[str, int] = Field(default={})
    distance_limit: int = Field(default=20)
    personality_preferences: List[str] = Field(default=[])
    interest_priorities: List[str] = Field(default=[])
    lifestyle_preferences: Dict[str, Any] = Field(default={})
    deal_breakers: List[str] = Field(default=[])
    importance_weights: Dict[str, float] = Field(default={})
    last_updated: str


class MatchingHistory(BaseModel):
    """매칭 이력 - 단순화"""
    user_uid: str
    total_matches: int
    successful_connections: int
    limit: int
    offset: int
    matches: List[Dict[str, Any]] = Field(default=[])


class MatchingAnalytics(BaseModel):
    """매칭 분석 데이터 - 단순화"""
    user_uid: str
    matching_stats: Dict[str, Any] = Field(default={})
    preference_insights: Dict[str, Any] = Field(default={})
    activity_patterns: Dict[str, Any] = Field(default={})
    recommendations: List[str] = Field(default=[])
    generated_at: str
