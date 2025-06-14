"""
일기 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class DiaryMetadata(BaseModel):
    """일기 메타데이터"""
    date: Optional[str] = Field(None, description="일기 작성 날짜")
    weather: Optional[str] = Field(None, description="날씨")
    mood: Optional[str] = Field(None, description="기분")
    location: Optional[str] = Field(None, description="위치")
    activities: Optional[List[str]] = Field(default=[], description="활동 목록")
    tags: Optional[List[str]] = Field(default=[], description="태그 목록")


class DiaryBase(BaseModel):
    """일기 기본 스키마"""
    content: str = Field(..., min_length=10, max_length=5000, description="일기 내용")
    metadata: Optional[DiaryMetadata] = Field(None, description="메타데이터")
    
    @validator('content')
    def validate_content(cls, v):
        """일기 내용 검증"""
        if not v or not v.strip():
            raise ValueError('일기 내용은 비어있을 수 없습니다')
        return v.strip()


class DiaryCreate(DiaryBase):
    """일기 생성 스키마"""
    diary_id: str = Field(..., description="일기 고유 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID (자동 설정)")


class DiaryUpdate(BaseModel):
    """일기 업데이트 스키마"""
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    metadata: Optional[DiaryMetadata] = None


class DiaryResponse(DiaryBase):
    """일기 응답 스키마"""
    diary_id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DiaryInDB(DiaryBase):
    """데이터베이스 일기 스키마"""
    id: str
    diary_id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DiaryListResponse(BaseModel):
    """일기 목록 응답 스키마"""
    diaries: List[DiaryResponse]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class DiarySearchRequest(BaseModel):
    """일기 검색 요청 스키마"""
    query: Optional[str] = Field(None, description="검색 키워드")
    start_date: Optional[str] = Field(None, description="시작 날짜 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="종료 날짜 (YYYY-MM-DD)")
    mood: Optional[str] = Field(None, description="기분 필터")
    tags: Optional[List[str]] = Field(default=[], description="태그 필터")
    page: int = Field(default=1, ge=1, description="페이지 번호")
    per_page: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수")


class DiaryStats(BaseModel):
    """일기 통계 스키마"""
    total_entries: int = Field(..., description="총 일기 수")
    this_month_entries: int = Field(..., description="이번 달 일기 수")
    streak_days: int = Field(..., description="연속 작성 일수")
    avg_length: float = Field(..., description="평균 일기 길이")
    most_frequent_mood: Optional[str] = Field(None, description="가장 빈번한 기분")
    most_used_tags: List[str] = Field(default=[], description="가장 많이 사용한 태그")
    writing_time_pattern: Dict[str, int] = Field(default={}, description="작성 시간 패턴")
