"""
매칭 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, validator


class MatchingFilters(BaseModel):
    """매칭 필터"""
    age_range: Optional[tuple[int, int]] = Field(None, description="나이 범위")
    location: Optional[str] = Field(None, description="지역")
    interests: Optional[List[str]] = Field(default=[], description="관심사")
    personality_types: Optional[List[str]] = Field(default=[], description="선호 성격 유형")
    emotion_compatibility: Optional[str] = Field(None, description="감정 호환성 수준")
    exclude_users: Optional[List[str]] = Field(default=[], description="제외할 사용자")


class MatchingRequest(BaseModel):
    """매칭 요청 스키마"""
    limit: int = Field(default=10, ge=1, le=50, description="추천 후보 수")
    min_compatibility: float = Field(default=0.5, ge=0.0, le=1.0, description="최소 호환성 점수")
    filters: Optional[MatchingFilters] = Field(None, description="추가 필터")
    include_analysis: bool = Field(default=True, description="상세 분석 포함 여부")


class CompatibilityRequest(BaseModel):
    """호환성 계산 요청 스키마"""
    target_user_id: str = Field(..., description="상대방 사용자 ID")
    include_details: bool = Field(default=True, description="상세 분석 포함 여부")


class CompatibilityBreakdown(BaseModel):
    """호환성 세부 분석"""
    personality_compatibility: float = Field(..., ge=0.0, le=1.0, description="성격 호환성")
    emotion_compatibility: float = Field(..., ge=0.0, le=1.0, description="감정 호환성")
    lifestyle_compatibility: float = Field(..., ge=0.0, le=1.0, description="생활 패턴 호환성")
    interest_compatibility: float = Field(..., ge=0.0, le=1.0, description="관심사 호환성")
    communication_compatibility: float = Field(..., ge=0.0, le=1.0, description="소통 스타일 호환성")


class CompatibilityResponse(BaseModel):
    """호환성 계산 응답 스키마"""
    user_id_1: str = Field(..., description="사용자 1 ID")
    user_id_2: str = Field(..., description="사용자 2 ID")
    overall_compatibility: float = Field(..., ge=0.0, le=1.0, description="전체 호환성 점수")
    compatibility_level: str = Field(..., description="호환성 수준")  # excellent, good, fair, poor
    
    breakdown: Optional[CompatibilityBreakdown] = Field(None, description="세부 호환성 분석")
    
    # 강점과 주의사항
    strengths: List[str] = Field(default=[], description="관계의 강점")
    potential_challenges: List[str] = Field(default=[], description="잠재적 도전과제")
    recommendations: List[str] = Field(default=[], description="관계 개선 제안")
    
    # 메타데이터
    calculated_at: datetime = Field(..., description="계산 시간")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="분석 신뢰도")


class MatchingCandidate(BaseModel):
    """매칭 후보자 정보"""
    user_id: str = Field(..., description="사용자 ID")
    compatibility_score: float = Field(..., ge=0.0, le=1.0, description="호환성 점수")
    compatibility_level: str = Field(..., description="호환성 수준")
    
    # 기본 정보 (익명화된)
    age_range: Optional[str] = Field(None, description="나이대")
    location: Optional[str] = Field(None, description="지역 (일반화된)")
    interests: List[str] = Field(default=[], description="공통 관심사")
    
    # 성격 정보
    personality_type: Optional[str] = Field(None, description="성격 유형 (MBTI)")
    personality_traits: List[str] = Field(default=[], description="주요 성격 특성")
    
    # 매칭 이유
    match_reasons: List[str] = Field(default=[], description="매칭 근거")
    common_traits: List[str] = Field(default=[], description="공통점")
    complementary_traits: List[str] = Field(default=[], description="상호 보완적 특성")
    
    # 메타데이터
    last_active: Optional[datetime] = Field(None, description="마지막 활동 시간")
    match_rank: int = Field(..., description="매칭 순위")


class MatchingCandidatesResponse(BaseModel):
    """매칭 후보 목록 응답"""
    user_id: str = Field(..., description="요청 사용자 ID")
    candidates: List[MatchingCandidate] = Field(..., description="매칭 후보 목록")
    total_count: int = Field(..., description="총 후보자 수")
    filters_applied: Dict[str, Any] = Field(default={}, description="적용된 필터")
    
    # 추천 메타데이터
    algorithm_version: str = Field(..., description="매칭 알고리즘 버전")
    generated_at: datetime = Field(..., description="생성 시간")
    expires_at: Optional[datetime] = Field(None, description="만료 시간")


class MatchingPreferences(BaseModel):
    """매칭 선호도 설정"""
    enabled: bool = Field(default=True, description="매칭 활성화 여부")
    visibility: str = Field(default="public", description="프로필 공개 수준")  # public, limited, private
    
    # 선호 조건
    preferred_age_range: Optional[tuple[int, int]] = Field(None, description="선호 나이 범위")
    preferred_location_radius: Optional[int] = Field(None, description="선호 지역 반경(km)")
    preferred_personality_types: List[str] = Field(default=[], description="선호 성격 유형")
    
    # 가중치 설정
    personality_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="성격 가중치")
    emotion_weight: float = Field(default=0.25, ge=0.0, le=1.0, description="감정 가중치")
    lifestyle_weight: float = Field(default=0.25, ge=0.0, le=1.0, description="생활 패턴 가중치")
    interest_weight: float = Field(default=0.2, ge=0.0, le=1.0, description="관심사 가중치")
    
    # 고급 설정
    min_compatibility_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="최소 호환성 임계값")
    diversity_factor: float = Field(default=0.2, ge=0.0, le=1.0, description="다양성 팩터")
    
    @validator('personality_weight', 'emotion_weight', 'lifestyle_weight', 'interest_weight')
    def validate_weights_sum(cls, v, values):
        """가중치 합계 검증"""
        total = v
        for field in ['personality_weight', 'emotion_weight', 'lifestyle_weight']:
            if field in values:
                total += values[field]
        
        if abs(total - 1.0) > 0.1 and len(values) == 3:  # 모든 가중치가 설정된 경우만 검증
            raise ValueError('가중치의 합은 1.0에 가까워야 합니다')
        return v


class MatchingProfile(BaseModel):
    """매칭용 사용자 프로필"""
    user_id: str
    display_name: str = Field(..., description="표시 이름")
    age_range: Optional[str] = Field(None, description="나이대")
    location: Optional[str] = Field(None, description="지역")
    bio: Optional[str] = Field(None, description="자기소개")
    
    # 성격 정보
    personality_type: Optional[str] = Field(None, description="성격 유형")
    personality_summary: List[str] = Field(default=[], description="성격 요약")
    
    # 관심사 및 취미
    interests: List[str] = Field(default=[], description="관심사")
    hobbies: List[str] = Field(default=[], description="취미")
    
    # 라이프스타일
    lifestyle_tags: List[str] = Field(default=[], description="라이프스타일 태그")
    activity_level: Optional[str] = Field(None, description="활동 수준")
    
    # 매칭 관련
    looking_for: List[str] = Field(default=[], description="찾고 있는 것")
    match_preferences: Optional[MatchingPreferences] = Field(None, description="매칭 선호도")
    
    # 메타데이터
    profile_completeness: float = Field(..., ge=0.0, le=1.0, description="프로필 완성도")
    last_active: Optional[datetime] = Field(None, description="마지막 활동")
    verified: bool = Field(default=False, description="인증 여부")


class MatchingFeedback(BaseModel):
    """매칭 피드백"""
    target_user_id: str = Field(..., description="피드백 대상 사용자 ID")
    interaction_type: str = Field(..., description="상호작용 유형")  # like, pass, block, report
    feedback_reason: Optional[str] = Field(None, description="피드백 사유")
    rating: Optional[int] = Field(None, ge=1, le=5, description="평점")
    comment: Optional[str] = Field(None, description="코멘트")
    created_at: datetime = Field(..., description="피드백 시간")


class MatchingAnalytics(BaseModel):
    """매칭 분석 데이터"""
    user_id: str
    analysis_period: Dict[str, str] = Field(..., description="분석 기간")
    
    # 매칭 통계
    total_matches_found: int = Field(..., description="총 매칭 후보 수")
    avg_compatibility_score: float = Field(..., description="평균 호환성 점수")
    match_success_rate: float = Field(..., description="매칭 성공률")
    
    # 프로필 성과
    profile_views: int = Field(..., description="프로필 조회 수")
    profile_likes: int = Field(..., description="받은 좋아요 수")
    profile_completeness: float = Field(..., description="프로필 완성도")
    
    # 호환성 분석
    personality_match_rate: float = Field(..., description="성격 매칭률")
    interest_overlap_avg: float = Field(..., description="관심사 겹침 평균")
    
    # 추천사항
    profile_improvement_tips: List[str] = Field(default=[], description="프로필 개선 팁")
    matching_strategy_tips: List[str] = Field(default=[], description="매칭 전략 팁")
    
    # 트렌드
    compatibility_trends: Dict[str, List[float]] = Field(default={}, description="호환성 추이")
    popular_traits: List[str] = Field(default=[], description="인기 특성")


class MatchingHistoryItem(BaseModel):
    """매칭 이력 항목"""
    target_user_id: str
    compatibility_score: float
    interaction_type: Optional[str] = None
    matched_at: datetime
    interaction_date: Optional[datetime] = None
    status: str  # pending, accepted, declined, blocked
