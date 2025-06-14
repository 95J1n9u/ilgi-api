"""
일기 분석 API 테스트용 간단한 서버
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# 앱 생성
app = FastAPI(
    title="AI 일기 분석 API (테스트용)",
    description="일기 분석 API 테스트용 간단한 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 인증 스키마
security = HTTPBearer()

# 추가 스키마 정의
class UserRegistration(BaseModel):
    email: str
    password: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class DiaryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    mood_score: Optional[int] = Field(None, ge=1, le=10)

class DiaryResponse(BaseModel):
    diary_id: str
    title: Optional[str]
    content: str
    mood_score: Optional[int]
    created_at: datetime

class MatchingRequest(BaseModel):
    user_id: str
    limit: int = 5
    min_compatibility_score: float = 0.7

class MatchingCandidate(BaseModel):
    user_id: str
    name: str
    compatibility_score: float
    common_interests: List[str]
    personality_match: Dict[str, float]

class MatchingResponse(BaseModel):
    candidates: List[MatchingCandidate]
    total_found: int
class DiaryMetadata(BaseModel):
    date: Optional[str] = None
    weather: Optional[str] = None
    mood: Optional[str] = None
    location: Optional[str] = None
    activities: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class DiaryAnalysisRequest(BaseModel):
    diary_id: str = Field(..., description="일기 고유 ID")
    content: str = Field(..., min_length=10, max_length=5000, description="일기 내용")
    metadata: Optional[DiaryMetadata] = None
    analysis_options: Optional[Dict[str, Any]] = {}

class EmotionScore(BaseModel):
    emotion: str
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)

class EmotionAnalysis(BaseModel):
    primary_emotion: str
    secondary_emotions: List[str] = []
    emotion_scores: List[EmotionScore]
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    emotional_intensity: float = Field(..., ge=0.0, le=1.0)
    emotional_stability: float = Field(..., ge=0.0, le=1.0)

class MBTIIndicators(BaseModel):
    E: float = Field(..., ge=0.0, le=1.0)
    I: float = Field(..., ge=0.0, le=1.0)
    S: float = Field(..., ge=0.0, le=1.0)
    N: float = Field(..., ge=0.0, le=1.0)
    T: float = Field(..., ge=0.0, le=1.0)
    F: float = Field(..., ge=0.0, le=1.0)
    J: float = Field(..., ge=0.0, le=1.0)
    P: float = Field(..., ge=0.0, le=1.0)

class Big5Traits(BaseModel):
    openness: float = Field(..., ge=0.0, le=1.0)
    conscientiousness: float = Field(..., ge=0.0, le=1.0)
    extraversion: float = Field(..., ge=0.0, le=1.0)
    agreeableness: float = Field(..., ge=0.0, le=1.0)
    neuroticism: float = Field(..., ge=0.0, le=1.0)

class PersonalityAnalysis(BaseModel):
    mbti_indicators: MBTIIndicators
    big5_traits: Big5Traits
    predicted_mbti: Optional[str] = None
    personality_summary: List[str] = []
    confidence_level: float = Field(..., ge=0.0, le=1.0)

class KeywordExtraction(BaseModel):
    keywords: List[str] = []
    topics: List[str] = []
    entities: List[str] = []
    themes: List[str] = []

class LifestylePattern(BaseModel):
    activity_patterns: Dict[str, float] = {}
    social_patterns: Dict[str, float] = {}
    time_patterns: Dict[str, float] = {}
    interest_areas: List[str] = []
    values_orientation: Dict[str, float] = {}

class DiaryAnalysisResponse(BaseModel):
    diary_id: str
    analysis_id: str
    user_id: str
    status: str
    emotion_analysis: EmotionAnalysis
    personality_analysis: PersonalityAnalysis
    keyword_extraction: KeywordExtraction
    lifestyle_patterns: LifestylePattern
    insights: List[str] = []
    recommendations: List[str] = []
    analysis_version: str
    processing_time: float
    confidence_score: float
    processed_at: datetime

# Mock 인증 함수
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """개발용 Mock 인증"""
    token = credentials.credentials
    
    # 개발용 테스트 토큰 허용
    if token == "test-token-for-development":
        return {
            "uid": "test-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Mock 인증 함수 (옵셔널)
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """인증이 옵셔널인 경우"""
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Mock AI 분석 함수
def mock_emotion_analysis(content: str) -> EmotionAnalysis:
    """Mock 감정 분석"""
    # 간단한 키워드 기반 감정 분석
    content_lower = content.lower()
    
    if any(word in content_lower for word in ['좋', '행복', '기쁘', '즐거', '만족']):
        primary_emotion = "행복"
        sentiment_score = 0.7
    elif any(word in content_lower for word in ['슬프', '우울', '힘들', '괴로', '아프']):
        primary_emotion = "슬픔"
        sentiment_score = -0.6
    elif any(word in content_lower for word in ['화', '짜증', '분노', '열받']):
        primary_emotion = "분노"
        sentiment_score = -0.4
    elif any(word in content_lower for word in ['걱정', '불안', '두려', '무서']):
        primary_emotion = "불안"
        sentiment_score = -0.3
    else:
        primary_emotion = "평온"
        sentiment_score = 0.1
    
    return EmotionAnalysis(
        primary_emotion=primary_emotion,
        secondary_emotions=["관심", "집중"],
        emotion_scores=[
            EmotionScore(emotion=primary_emotion, score=0.8, confidence=0.85),
            EmotionScore(emotion="관심", score=0.6, confidence=0.75),
        ],
        sentiment_score=sentiment_score,
        emotional_intensity=0.7,
        emotional_stability=0.8
    )

def mock_personality_analysis(content: str) -> PersonalityAnalysis:
    """Mock 성격 분석"""
    # 간단한 패턴 기반 성격 분석
    content_lower = content.lower()
    
    # 외향성 vs 내향성
    if any(word in content_lower for word in ['사람들', '친구', '만나', '파티', '모임']):
        extraversion = 0.7
        introversion = 0.3
    else:
        extraversion = 0.4
        introversion = 0.6
    
    return PersonalityAnalysis(
        mbti_indicators=MBTIIndicators(
            E=extraversion, I=introversion,
            S=0.5, N=0.5,
            T=0.4, F=0.6,
            J=0.6, P=0.4
        ),
        big5_traits=Big5Traits(
            openness=0.7,
            conscientiousness=0.6,
            extraversion=extraversion,
            agreeableness=0.8,
            neuroticism=0.3
        ),
        predicted_mbti="ENFJ",
        personality_summary=["따뜻하고 공감 능력이 뛰어남", "타인을 배려하는 성향"],
        confidence_level=0.75
    )

def mock_keyword_extraction(content: str) -> KeywordExtraction:
    """Mock 키워드 추출"""
    # 간단한 키워드 추출
    words = content.split()
    keywords = [word for word in words if len(word) > 2][:5]
    
    return KeywordExtraction(
        keywords=keywords,
        topics=["일상", "감정", "생각"],
        entities=["나", "가족", "친구"],
        themes=["성찰", "일상"]
    )

def mock_lifestyle_analysis(content: str) -> LifestylePattern:
    """Mock 생활 패턴 분석"""
    return LifestylePattern(
        activity_patterns={"독서": 0.6, "운동": 0.4, "음악감상": 0.7},
        social_patterns={"친구만남": 0.5, "가족시간": 0.8, "혼자시간": 0.6},
        time_patterns={"오전활동": 0.7, "오후활동": 0.8, "야간활동": 0.4},
        interest_areas=["독서", "음악", "영화"],
        values_orientation={"가족": 0.9, "건강": 0.7, "성장": 0.8}
    )

# API 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "🤖 AI 일기 분석 API 테스트 서버",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# ===========================================
# 인증 API 엔드포인트
# ===========================================

@app.post("/api/v1/auth/register", response_model=AuthResponse)
async def register_user(user_data: UserRegistration):
    """사용자 등록 (Mock)"""
    # Mock 등록 처리
    user_id = f"user_{int(time.time())}"
    
    return AuthResponse(
        access_token="test-token-for-development",
        token_type="bearer",
        user={
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "age": user_data.age,
            "gender": user_data.gender,
            "created_at": datetime.now().isoformat()
        }
    )

@app.post("/api/v1/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """로그인 (Mock)"""
    # Mock 로그인 처리
    if login_data.email == "test@example.com" and login_data.password == "password123":
        return AuthResponse(
            access_token="test-token-for-development",
            token_type="bearer",
            user={
                "id": "test-user-123",
                "email": login_data.email,
                "name": "Test User",
                "last_login": datetime.now().isoformat()
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

# ===========================================
# 일기 API 엔드포인트
# ===========================================

@app.post("/api/v1/diary/create", response_model=DiaryResponse)
async def create_diary(
    diary_data: DiaryCreate,
    current_user: dict = Depends(get_current_user)
):
    """일기 작성 (Mock)"""
    diary_id = f"diary_{int(time.time())}"
    
    return DiaryResponse(
        diary_id=diary_id,
        title=diary_data.title,
        content=diary_data.content,
        mood_score=diary_data.mood_score,
        created_at=datetime.now()
    )

@app.get("/api/v1/diary/list")
async def get_diary_list(
    user_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """일기 목록 조회 (Mock)"""
    # Mock 데이터 생성
    diaries = []
    for i in range(min(limit, 5)):
        diaries.append({
            "diary_id": f"diary_{i}",
            "title": f"일기 제목 {i+1}",
            "content": f"오늘의 일기 내용 {i+1}...",
            "mood_score": 7,
            "created_at": datetime.now().isoformat(),
            "is_analyzed": True
        })
    
    return {
        "diaries": diaries,
        "total_count": len(diaries),
        "user_id": user_id
    }

# ===========================================
# 매칭 API 엔드포인트
# ===========================================

@app.post("/api/v1/matching/find", response_model=MatchingResponse)
async def find_matching(
    request: MatchingRequest,
    current_user: dict = Depends(get_current_user)
):
    """매칭 후보 찾기 (Mock)"""
    # Mock 매칭 후보 생성
    candidates = []
    for i in range(min(request.limit, 3)):
        candidates.append(MatchingCandidate(
            user_id=f"user_{i}",
            name=f"매칭 사용자 {i+1}",
            compatibility_score=0.8 - (i * 0.1),
            common_interests=["독서", "음악", "영화"],
            personality_match={
                "mbti_similarity": 0.9,
                "emotion_compatibility": 0.8,
                "lifestyle_match": 0.7
            }
        ))
    
    return MatchingResponse(
        candidates=candidates,
        total_found=len(candidates)
    )

@app.get("/api/v1/matching/compatibility")
async def calculate_compatibility(
    user1_id: str,
    user2_id: str,
    current_user: dict = Depends(get_current_user)
):
    """호환성 점수 계산 (Mock)"""
    # Mock 호환성 계산
    return {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "overall_compatibility": 0.85,
        "detailed_scores": {
            "personality_match": 0.9,
            "emotion_compatibility": 0.8,
            "lifestyle_similarity": 0.85,
            "interest_overlap": 0.75
        },
        "common_traits": [
            "비슷한 성격 유형",
            "공통 관심사",
            "비슷한 라이프스타일"
        ],
        "compatibility_explanation": "매우 높은 호환성을 보입니다."
    }

@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(
    request: DiaryAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """일기 분석 API"""
    try:
        start_time = time.time()
        
        # Mock AI 분석 실행
        emotion_analysis = mock_emotion_analysis(request.content)
        personality_analysis = mock_personality_analysis(request.content)
        keyword_extraction = mock_keyword_extraction(request.content)
        lifestyle_patterns = mock_lifestyle_analysis(request.content)
        
        # Mock 인사이트 생성
        insights = [
            f"오늘 일기에서 '{emotion_analysis.primary_emotion}' 감정이 주로 나타났습니다.",
            "긍정적인 사고 패턴이 관찰됩니다.",
            "자기 성찰 능력이 뛰어납니다."
        ]
        
        # Mock 추천사항 생성
        recommendations = [
            "규칙적인 일기 작성을 통해 감정 패턴을 관찰해보세요.",
            "긍정적인 경험들을 더 자세히 기록해보세요.",
            "감정 변화에 대한 원인을 분석해보세요."
        ]
        
        processing_time = time.time() - start_time
        analysis_id = f"analysis_{int(time.time())}"
        
        return DiaryAnalysisResponse(
            diary_id=request.diary_id,
            analysis_id=analysis_id,
            user_id=current_user["uid"],
            status="completed",
            emotion_analysis=emotion_analysis,
            personality_analysis=personality_analysis,
            keyword_extraction=keyword_extraction,
            lifestyle_patterns=lifestyle_patterns,
            insights=insights,
            recommendations=recommendations,
            analysis_version="1.0.0-test",
            processing_time=processing_time,
            confidence_score=0.8,
            processed_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 처리 중 오류 발생: {str(e)}"
        )

@app.get("/api/v1/analysis/history")
async def get_analysis_history(
    user_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """분석 이력 조회 (Mock)"""
    # Mock 데이터 반환
    history = []
    for i in range(min(limit, 5)):
        history.append({
            "analysis_id": f"analysis_{i}",
            "diary_id": f"diary_{i}",
            "analysis_date": datetime.now().isoformat(),
            "primary_emotion": ["행복", "슬픈", "평온"][i % 3],
            "sentiment_score": 0.7 - (i * 0.1),
            "confidence_score": 0.8,
            "insights_count": 3,
            "processing_time": 2.5,
            "analysis_version": "1.0.0-test"
        })
    
    return {
        "user_id": user_id,
        "history": history,
        "total": len(history),
        "page": 1,
        "has_next": False
    }

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 AI 일기 분석 테스트 서버 시작...")
    print("📝 Mock 분석을 사용합니다 (개발용)")
    print("🌐 http://localhost:8000/docs 에서 API 네이티브 테스트 가능")
    print("🌐 testweb.html 에서 웹 UI 테스트 가능")
    print("🔑 인증 토큰: test-token-for-development")
    print("")
    print("🚀 사용 가능한 API 엔드포인트:")
    print("   • POST /api/v1/auth/register - 사용자 등록")
    print("   • POST /api/v1/auth/login - 로그인")
    print("   • POST /api/v1/analysis/diary - 일기 분석")
    print("   • GET  /api/v1/analysis/history - 분석 이력")
    print("   • POST /api/v1/matching/find - 매칭 찾기")
    print("   • GET  /api/v1/matching/compatibility - 호환성 계산")
    print("   • POST /api/v1/diary/create - 일기 작성")
    print("   • GET  /api/v1/diary/list - 일기 목록")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
