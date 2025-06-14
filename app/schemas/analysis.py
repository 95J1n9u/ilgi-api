"""
AI 분석 결과 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, validator

from app.schemas.diary import DiaryMetadata, DiaryBase


class EmotionScore(BaseModel):
    """감정 점수"""
    emotion: str = Field(..., description="감정명")
    score: float = Field(..., ge=0.0, le=1.0, description="감정 점수 (0-1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="신뢰도")


class EmotionAnalysis(BaseModel):
    """감정 분석 결과"""
    primary_emotion: str = Field(..., description="주요 감정")
    secondary_emotions: List[str] = Field(default=[], description="보조 감정들")
    emotion_scores: List[EmotionScore] = Field(..., description="감정별 점수")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="감정 점수 (-1 ~ 1)")
    emotional_intensity: float = Field(..., ge=0.0, le=1.0, description="감정 강도")
    emotional_stability: float = Field(..., ge=0.0, le=1.0, description="감정 안정성")


class MBTIIndicators(BaseModel):
    """MBTI 지표"""
    E: float = Field(..., ge=0.0, le=1.0, description="외향성")
    I: float = Field(..., ge=0.0, le=1.0, description="내향성")
    S: float = Field(..., ge=0.0, le=1.0, description="감각형")
    N: float = Field(..., ge=0.0, le=1.0, description="직관형")
    T: float = Field(..., ge=0.0, le=1.0, description="사고형")
    F: float = Field(..., ge=0.0, le=1.0, description="감정형")
    J: float = Field(..., ge=0.0, le=1.0, description="판단형")
    P: float = Field(..., ge=0.0, le=1.0, description="인식형")
    
    @validator('*', pre=True)
    def validate_scores(cls, v):
        """점수 범위 검증"""
        if not isinstance(v, (int, float)):
            raise ValueError('점수는 숫자여야 합니다')
        return max(0.0, min(1.0, float(v)))


class Big5Traits(BaseModel):
    """Big5 성격 특성"""
    openness: float = Field(..., ge=0.0, le=1.0, description="개방성")
    conscientiousness: float = Field(..., ge=0.0, le=1.0, description="성실성")
    extraversion: float = Field(..., ge=0.0, le=1.0, description="외향성")
    agreeableness: float = Field(..., ge=0.0, le=1.0, description="친화성")
    neuroticism: float = Field(..., ge=0.0, le=1.0, description="신경성")


class PersonalityAnalysis(BaseModel):
    """성격 분석 결과"""
    mbti_indicators: MBTIIndicators = Field(..., description="MBTI 지표")
    big5_traits: Big5Traits = Field(..., description="Big5 특성")
    predicted_mbti: Optional[str] = Field(None, description="예측된 MBTI 유형")
    personality_summary: List[str] = Field(default=[], description="성격 요약")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="분석 신뢰도")


class KeywordExtraction(BaseModel):
    """키워드 추출 결과"""
    keywords: List[str] = Field(..., description="추출된 키워드")
    topics: List[str] = Field(..., description="주제 분류")
    entities: List[str] = Field(default=[], description="개체명")
    themes: List[str] = Field(default=[], description="테마")


class LifestylePattern(BaseModel):
    """생활 패턴 분석"""
    activity_patterns: Dict[str, float] = Field(default={}, description="활동 패턴")
    social_patterns: Dict[str, float] = Field(default={}, description="사회적 패턴")
    time_patterns: Dict[str, float] = Field(default={}, description="시간 패턴")
    interest_areas: List[str] = Field(default=[], description="관심 분야")
    values_orientation: Dict[str, float] = Field(default={}, description="가치관 성향")


class DiaryAnalysisRequest(DiaryBase):
    """일기 분석 요청 스키마"""
    diary_id: str = Field(..., description="일기 고유 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID (자동 설정)")
    analysis_options: Optional[Dict[str, Any]] = Field(default={}, description="분석 옵션")


class DiaryAnalysisResponse(BaseModel):
    """일기 분석 응답 스키마"""
    diary_id: str = Field(..., description="일기 ID")
    analysis_id: str = Field(..., description="분석 결과 ID")
    user_id: str = Field(..., description="사용자 ID") 
    status: str = Field(..., description="분석 상태")
    
    # 분석 결과
    emotion_analysis: EmotionAnalysis = Field(..., description="감정 분석")
    personality_analysis: PersonalityAnalysis = Field(..., description="성격 분석")
    keyword_extraction: KeywordExtraction = Field(..., description="키워드 추출")
    lifestyle_patterns: LifestylePattern = Field(..., description="생활 패턴")
    
    # 인사이트
    insights: List[str] = Field(default=[], description="분석 인사이트")
    recommendations: List[str] = Field(default=[], description="추천사항")
    
    # 메타데이터
    analysis_version: str = Field(..., description="분석 모델 버전")
    processing_time: float = Field(..., description="처리 시간(초)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="전체 신뢰도")
    processed_at: datetime = Field(..., description="분석 완료 시간")
    
    class Config:
        from_attributes = True


class BatchAnalysisRequest(BaseModel):
    """일괄 분석 요청 스키마"""
    diary_entries: List[DiaryAnalysisRequest] = Field(..., description="분석할 일기 목록")
    batch_options: Optional[Dict[str, Any]] = Field(default={}, description="일괄 처리 옵션")


class UserInsightsResponse(BaseModel):
    """사용자 종합 인사이트 응답"""
    user_id: str = Field(..., description="사용자 ID")
    analysis_period: Dict[str, str] = Field(..., description="분석 기간")
    total_entries: int = Field(..., description="분석된 일기 수")
    
    # 종합 분석 결과
    overall_emotion_pattern: EmotionAnalysis = Field(..., description="전체 감정 패턴")
    personality_profile: PersonalityAnalysis = Field(..., description="성격 프로필")
    lifestyle_summary: LifestylePattern = Field(..., description="생활 패턴 요약")
    
    # 변화 패턴
    emotion_trends: Dict[str, List[float]] = Field(default={}, description="감정 변화 추이")
    personality_evolution: Dict[str, float] = Field(default={}, description="성격 변화")
    
    # 인사이트
    key_insights: List[str] = Field(..., description="주요 인사이트")
    growth_areas: List[str] = Field(default=[], description="성장 영역")
    recommendations: List[str] = Field(default=[], description="개인화 추천")
    
    # 메타데이터
    last_updated: datetime = Field(..., description="마지막 업데이트")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="신뢰도 점수")


class AnalysisHistoryItem(BaseModel):
    """분석 이력 항목"""
    analysis_id: str
    diary_id: str
    analysis_date: datetime
    primary_emotion: str
    sentiment_score: float
    confidence_score: float
    insights_count: int


class AnalysisStatsResponse(BaseModel):
    """분석 통계 응답"""
    user_id: str
    total_analyses: int
    analysis_period_days: int
    
    # 감정 통계
    emotion_distribution: Dict[str, int] = Field(default={})
    avg_sentiment_score: float
    sentiment_trend: List[float] = Field(default=[])
    
    # 성격 통계
    personality_consistency: float
    dominant_traits: List[str] = Field(default=[])
    
    # 활동 통계
    analysis_frequency: Dict[str, int] = Field(default={})
    most_active_periods: List[str] = Field(default=[])
    
    # 인사이트 통계  
    total_insights: int
    insight_categories: Dict[str, int] = Field(default={})
