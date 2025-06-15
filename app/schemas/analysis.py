"""
AI 분석 결과 관련 Pydantic 스키마 - Firebase 중심으로 단순화
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class DiaryAnalysisRequest(BaseModel):
    """일기 분석 요청 스키마 - 단순화"""
    diary_id: str = Field(..., description="일기 고유 ID")
    content: str = Field(..., description="일기 내용")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="추가 메타데이터")
    user_uid: Optional[str] = Field(None, description="Firebase 사용자 UID (자동 설정)")


class EmotionAnalysis(BaseModel):
    """감정 분석 결과 - 단순화"""
    primary_emotion: str = Field(..., description="주요 감정")
    emotions: Dict[str, float] = Field(default={}, description="감정별 점수")
    sentiment_score: float = Field(..., description="감정 점수 (-1 ~ 1)")
    confidence: float = Field(..., description="신뢰도 (0 ~ 1)")


class PersonalityInsights(BaseModel):
    """성격 인사이트 - 단순화"""
    openness: float = Field(..., description="개방성")
    conscientiousness: float = Field(..., description="성실성")
    extraversion: float = Field(..., description="외향성")
    agreeableness: float = Field(..., description="친화성")
    neuroticism: float = Field(..., description="신경성")
    dominant_traits: List[str] = Field(default=[], description="주요 특성")


class DiaryAnalysisResponse(BaseModel):
    """일기 분석 응답 스키마 - 단순화"""
    analysis_id: str = Field(..., description="분석 결과 ID")
    diary_id: str = Field(..., description="일기 ID")
    user_uid: str = Field(..., description="Firebase 사용자 UID")
    content: str = Field(..., description="분석된 내용")
    
    # 분석 결과 (단순화)
    emotion_analysis: EmotionAnalysis = Field(..., description="감정 분석")
    personality_insights: PersonalityInsights = Field(..., description="성격 인사이트")
    
    # 추가 정보
    themes: List[str] = Field(default=[], description="주제")
    keywords: List[str] = Field(default=[], description="키워드")
    mood_score: float = Field(..., description="기분 점수 (0-10)")
    stress_level: float = Field(..., description="스트레스 수준 (0-10)")
    life_satisfaction: float = Field(..., description="삶의 만족도 (0-10)")
    recommendations: List[str] = Field(default=[], description="추천사항")
    
    # 메타데이터
    created_at: str = Field(..., description="분석 완료 시간")
    processed_by: str = Field(..., description="처리 모델")
    
    class Config:
        from_attributes = True


class UserInsightsResponse(BaseModel):
    """사용자 종합 인사이트 - 단순화"""
    user_uid: str = Field(..., description="Firebase 사용자 UID")
    summary: str = Field(..., description="요약")
    emotional_wellbeing: Dict[str, Any] = Field(default={}, description="감정적 웰빙")
    behavioral_patterns: List[str] = Field(default=[], description="행동 패턴")
    recommendations: List[str] = Field(default=[], description="추천사항")
    growth_opportunities: List[str] = Field(default=[], description="성장 기회")
    generated_at: str = Field(..., description="생성 시간")


class BatchAnalysisRequest(BaseModel):
    """일괄 분석 요청 - 단순화"""
    diary_entries: List[DiaryAnalysisRequest] = Field(..., description="분석할 일기 목록")
    batch_id: Optional[str] = Field(None, description="배치 ID")


class AnalysisHistoryItem(BaseModel):
    """분석 이력 항목 - 단순화"""
    analysis_id: str
    diary_id: str
    date: str
    primary_emotion: str
    mood_score: float
    themes: List[str]


class AnalysisStatsResponse(BaseModel):
    """분석 통계 - 단순화"""
    user_uid: str
    total_analyses: int
    this_month: int
    avg_mood_score: float
    most_common_emotion: str
    emotional_diversity: float
    consistency_score: float
    growth_trend: str
    streak_days: int
    last_analysis: str
