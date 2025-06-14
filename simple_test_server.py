"""
완전히 독립적인 AI 일기 분석 API 테스트 서버
모든 의존성이 제거된 순수 Mock 서버
"""
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

try:
    from fastapi import FastAPI, HTTPException, status, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field
except ImportError:
    print("❌ FastAPI가 설치되지 않았습니다. 다음 명령어로 설치하세요:")
    print("pip install fastapi uvicorn")
    exit(1)

# ===========================================
# FastAPI 앱 설정
# ===========================================

app = FastAPI(
    title="🤖 AI 일기 분석 API (Mock 서버)",
    description="완전히 독립적인 테스트용 Mock 서버",
    version="2.0.0"
)

# CORS 설정 - 모든 origin 허용 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 인증 스키마
security = HTTPBearer(auto_error=False)  # auto_error=False로 설정하여 더 유연하게

# ===========================================
# Pydantic 스키마 정의
# ===========================================

# 인증 관련 스키마
class UserRegistration(BaseModel):
    email: str = Field(..., description="사용자 이메일")
    password: str = Field(..., min_length=6, description="비밀번호")
    name: str = Field(..., description="사용자 이름")
    age: Optional[int] = Field(None, ge=1, le=120, description="나이")
    gender: Optional[str] = Field(None, description="성별")

class UserLogin(BaseModel):
    email: str = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호")

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# 일기 관련 스키마
class DiaryMetadata(BaseModel):
    date: Optional[str] = None
    weather: Optional[str] = None
    mood: Optional[str] = None
    location: Optional[str] = None
    activities: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class DiaryCreate(BaseModel):
    title: Optional[str] = Field(None, description="일기 제목")
    content: str = Field(..., min_length=1, max_length=10000, description="일기 내용")
    mood_score: Optional[int] = Field(None, ge=1, le=10, description="기분 점수 (1-10)")

class DiaryResponse(BaseModel):
    diary_id: str
    title: Optional[str]
    content: str
    mood_score: Optional[int]
    created_at: datetime

# 분석 관련 스키마
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
    E: float = Field(..., ge=0.0, le=1.0, description="외향성")
    I: float = Field(..., ge=0.0, le=1.0, description="내향성")
    S: float = Field(..., ge=0.0, le=1.0, description="감각형")
    N: float = Field(..., ge=0.0, le=1.0, description="직관형")
    T: float = Field(..., ge=0.0, le=1.0, description="사고형")
    F: float = Field(..., ge=0.0, le=1.0, description="감정형")
    J: float = Field(..., ge=0.0, le=1.0, description="판단형")
    P: float = Field(..., ge=0.0, le=1.0, description="인식형")

class Big5Traits(BaseModel):
    openness: float = Field(..., ge=0.0, le=1.0, description="개방성")
    conscientiousness: float = Field(..., ge=0.0, le=1.0, description="성실성")
    extraversion: float = Field(..., ge=0.0, le=1.0, description="외향성")
    agreeableness: float = Field(..., ge=0.0, le=1.0, description="친화성")
    neuroticism: float = Field(..., ge=0.0, le=1.0, description="신경성")

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

# 매칭 관련 스키마
class MatchingRequest(BaseModel):
    user_id: str
    limit: int = Field(default=5, ge=1, le=20)
    min_compatibility_score: float = Field(default=0.7, ge=0.0, le=1.0)

class MatchingCandidate(BaseModel):
    user_id: str
    name: str
    compatibility_score: float
    common_interests: List[str]
    personality_match: Dict[str, float]

class MatchingResponse(BaseModel):
    candidates: List[MatchingCandidate]
    total_found: int

# ===========================================
# Mock 데이터 생성 함수들
# ===========================================

def generate_mock_user_id() -> str:
    """Mock 사용자 ID 생성"""
    return f"user_{int(time.time())}_{str(uuid.uuid4())[:8]}"

def generate_mock_diary_id() -> str:
    """Mock 일기 ID 생성"""
    return f"diary_{int(time.time())}_{str(uuid.uuid4())[:8]}"

def generate_mock_analysis_id() -> str:
    """Mock 분석 ID 생성"""
    return f"analysis_{int(time.time())}_{str(uuid.uuid4())[:8]}"

# ===========================================
# 인증 관련 함수
# ===========================================

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Mock 인증 함수"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # 개발용 테스트 토큰들 허용
    valid_tokens = [
        "test-token-for-development",
        "mock-token",
        "dev-token"
    ]
    
    if token in valid_tokens:
        return {
            "uid": "test-user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 토큰입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

# ===========================================
# Mock AI 분석 함수들
# ===========================================

def analyze_emotion_mock(content: str) -> EmotionAnalysis:
    """Mock 감정 분석"""
    content_lower = content.lower()
    
    # 간단한 키워드 기반 감정 분석
    emotion_keywords = {
        "행복": ["좋", "행복", "기쁘", "즐거", "만족", "웃", "감사"],
        "슬픔": ["슬프", "우울", "힘들", "괴로", "아프", "눈물"],
        "분노": ["화", "짜증", "분노", "열받", "싫", "답답"],
        "불안": ["걱정", "불안", "두려", "무서", "떨림"],
        "평온": ["평온", "차분", "고요", "안정", "편안"]
    }
    
    emotion_scores = []
    detected_emotions = []
    
    for emotion, keywords in emotion_keywords.items():
        score = sum(1 for keyword in keywords if keyword in content_lower) / len(keywords)
        if score > 0:
            emotion_scores.append(EmotionScore(
                emotion=emotion,
                score=min(score * 2, 1.0),  # 최대 1.0
                confidence=0.7 + score * 0.2
            ))
            detected_emotions.append(emotion)
    
    # 기본값 설정
    if not emotion_scores:
        emotion_scores = [EmotionScore(emotion="평온", score=0.6, confidence=0.7)]
        detected_emotions = ["평온"]
    
    primary_emotion = max(emotion_scores, key=lambda x: x.score).emotion
    secondary_emotions = [e for e in detected_emotions if e != primary_emotion][:2]
    
    # 감정 점수 계산
    sentiment_score = 0.0
    for score in emotion_scores:
        if score.emotion in ["행복", "평온"]:
            sentiment_score += score.score
        elif score.emotion in ["슬픔", "분노", "불안"]:
            sentiment_score -= score.score
    
    sentiment_score = max(-1.0, min(1.0, sentiment_score))
    
    return EmotionAnalysis(
        primary_emotion=primary_emotion,
        secondary_emotions=secondary_emotions,
        emotion_scores=emotion_scores,
        sentiment_score=sentiment_score,
        emotional_intensity=0.6 + abs(sentiment_score) * 0.3,
        emotional_stability=0.8 - abs(sentiment_score) * 0.2
    )

def analyze_personality_mock(content: str) -> PersonalityAnalysis:
    """Mock 성격 분석"""
    content_lower = content.lower()
    
    # 간단한 패턴 기반 성격 분석
    extraversion = 0.5
    if any(word in content_lower for word in ["사람들", "친구", "만나", "파티", "모임", "대화"]):
        extraversion = 0.7
    elif any(word in content_lower for word in ["혼자", "조용", "집", "책"]):
        extraversion = 0.3
    
    openness = 0.6
    if any(word in content_lower for word in ["새로운", "창의", "예술", "상상", "꿈"]):
        openness = 0.8
    
    conscientiousness = 0.6
    if any(word in content_lower for word in ["계획", "목표", "노력", "성취", "책임"]):
        conscientiousness = 0.8
    
    agreeableness = 0.7
    if any(word in content_lower for word in ["도움", "배려", "친절", "협력"]):
        agreeableness = 0.9
    
    neuroticism = 0.4
    if any(word in content_lower for word in ["걱정", "불안", "스트레스", "힘들"]):
        neuroticism = 0.7
    
    # MBTI 지표 계산
    mbti_indicators = MBTIIndicators(
        E=extraversion,
        I=1.0 - extraversion,
        S=0.5,
        N=0.5,
        T=0.4,
        F=0.6,
        J=conscientiousness,
        P=1.0 - conscientiousness
    )
    
    # MBTI 유형 예측
    mbti = ""
    mbti += "E" if extraversion > 0.5 else "I"
    mbti += "N" if openness > 0.6 else "S"
    mbti += "F" if agreeableness > 0.6 else "T"
    mbti += "J" if conscientiousness > 0.5 else "P"
    
    return PersonalityAnalysis(
        mbti_indicators=mbti_indicators,
        big5_traits=Big5Traits(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=extraversion,
            agreeableness=agreeableness,
            neuroticism=neuroticism
        ),
        predicted_mbti=mbti,
        personality_summary=[
            f"{'외향적' if extraversion > 0.5 else '내향적'}인 성향",
            f"{'개방적' if openness > 0.6 else '실용적'}인 사고",
            f"{'체계적' if conscientiousness > 0.5 else '유연한'} 접근"
        ],
        confidence_level=0.75
    )

def extract_keywords_mock(content: str) -> KeywordExtraction:
    """Mock 키워드 추출"""
    # 간단한 키워드 추출
    words = content.replace(",", " ").replace(".", " ").split()
    keywords = [word for word in words if len(word) > 2 and word.isalnum()][:8]
    
    # 주제 분류
    topics = ["일상"]
    if any(word in content.lower() for word in ["일", "직장", "회사", "업무"]):
        topics.append("업무")
    if any(word in content.lower() for word in ["가족", "친구", "사람"]):
        topics.append("인간관계")
    if any(word in content.lower() for word in ["건강", "운동", "음식"]):
        topics.append("건강")
    
    # 개체명 추출 (간단히)
    entities = []
    if "나" in content:
        entities.append("나")
    if any(word in content for word in ["엄마", "아빠", "부모", "가족"]):
        entities.append("가족")
    
    return KeywordExtraction(
        keywords=keywords,
        topics=topics,
        entities=entities,
        themes=["성찰", "경험"]
    )

def analyze_lifestyle_mock(content: str) -> LifestylePattern:
    """Mock 생활 패턴 분석"""
    content_lower = content.lower()
    
    activity_patterns = {"일상활동": 0.7}
    if any(word in content_lower for word in ["운동", "헬스", "달리기"]):
        activity_patterns["운동"] = 0.8
    if any(word in content_lower for word in ["독서", "책"]):
        activity_patterns["독서"] = 0.7
    if any(word in content_lower for word in ["요리", "음식", "먹"]):
        activity_patterns["요리"] = 0.6
    
    social_patterns = {"혼자시간": 0.6}
    if any(word in content_lower for word in ["친구", "만나"]):
        social_patterns["친구만남"] = 0.8
    if any(word in content_lower for word in ["가족"]):
        social_patterns["가족시간"] = 0.9
    
    return LifestylePattern(
        activity_patterns=activity_patterns,
        social_patterns=social_patterns,
        time_patterns={"오전": 0.6, "오후": 0.8, "저녁": 0.7},
        interest_areas=["개인성장", "일상"],
        values_orientation={"가족": 0.9, "건강": 0.7, "성장": 0.8}
    )

# ===========================================
# API 엔드포인트들
# ===========================================

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🤖 AI 일기 분석 API - Mock 서버",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "analysis": "/api/v1/analysis", 
            "matching": "/api/v1/matching",
            "diary": "/api/v1/diary"
        }
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "Mock server is running"
    }

# 인증 API
@app.post("/api/v1/auth/register", response_model=AuthResponse)
async def register_user(user_data: UserRegistration):
    """사용자 등록 (Mock)"""
    user_id = generate_mock_user_id()
    
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
    # 간단한 Mock 인증
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
            detail="이메일 또는 비밀번호가 올바르지 않습니다"
        )

# 일기 분석 API
@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(
    request: DiaryAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """일기 분석 (Mock)"""
    try:
        start_time = time.time()
        
        # Mock AI 분석 실행
        emotion_analysis = analyze_emotion_mock(request.content)
        personality_analysis = analyze_personality_mock(request.content)
        keyword_extraction = extract_keywords_mock(request.content)
        lifestyle_patterns = analyze_lifestyle_mock(request.content)
        
        # 인사이트 생성
        insights = [
            f"일기에서 '{emotion_analysis.primary_emotion}' 감정이 주요하게 나타났습니다.",
            f"성격 유형 '{personality_analysis.predicted_mbti}'의 특성이 관찰됩니다.",
            "자기 성찰과 감정 표현 능력이 뛰어납니다."
        ]
        
        # 추천사항 생성
        recommendations = [
            "꾸준한 일기 작성으로 감정 패턴을 추적해보세요.",
            "긍정적인 경험들을 더 자세히 기록해보세요.",
            "감정의 원인과 변화 과정을 분석해보세요."
        ]
        
        processing_time = time.time() - start_time
        analysis_id = generate_mock_analysis_id()
        
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
            analysis_version="2.0.0-mock",
            processing_time=processing_time,
            confidence_score=0.82,
            processed_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/api/v1/analysis/history")
async def get_analysis_history(
    user_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """분석 이력 조회 (Mock)"""
    emotions = ["행복", "평온", "기대", "슬픔", "불안"]
    history = []
    
    for i in range(min(limit, 7)):
        days_ago = i
        analysis_date = datetime.now() - timedelta(days=days_ago)
        
        history.append({
            "analysis_id": f"analysis_{i}_{int(time.time())}",
            "diary_id": f"diary_{i}_{int(time.time())}",
            "analysis_date": analysis_date.isoformat(),
            "primary_emotion": emotions[i % len(emotions)],
            "sentiment_score": round(0.8 - (i * 0.1), 2),
            "confidence_score": round(0.85 - (i * 0.02), 2),
            "insights_count": 3,
            "processing_time": round(2.1 + (i * 0.3), 1),
            "analysis_version": "2.0.0-mock"
        })
    
    return {
        "user_id": user_id,
        "history": history,
        "total": len(history),
        "page": 1,
        "has_next": False
    }

# 일기 API
@app.post("/api/v1/diary/create", response_model=DiaryResponse)
async def create_diary(
    diary_data: DiaryCreate,
    current_user: dict = Depends(get_current_user)
):
    """일기 작성 (Mock)"""
    diary_id = generate_mock_diary_id()
    
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
    diaries = []
    titles = ["새로운 시작", "좋은 하루", "조용한 저녁", "바쁜 하루", "휴식 시간"]
    
    for i in range(min(limit, 5)):
        days_ago = i
        created_date = datetime.now() - timedelta(days=days_ago)
        
        diaries.append({
            "diary_id": f"diary_{i}_{int(time.time())}",
            "title": titles[i % len(titles)],
            "content": f"오늘의 일기 내용 {i+1}. 하루를 되돌아보며...",
            "mood_score": 7 + (i % 3),
            "created_at": created_date.isoformat(),
            "is_analyzed": True
        })
    
    return {
        "diaries": diaries,
        "total_count": len(diaries),
        "user_id": user_id
    }

# 매칭 API
@app.post("/api/v1/matching/find", response_model=MatchingResponse)
async def find_matching(
    request: MatchingRequest,
    current_user: dict = Depends(get_current_user)
):
    """매칭 후보 찾기 (Mock)"""
    candidates = []
    names = ["김하늘", "이바다", "박산들", "최강민", "정예린"]
    
    for i in range(min(request.limit, 3)):
        candidates.append(MatchingCandidate(
            user_id=f"user_{i}_{int(time.time())}",
            name=names[i % len(names)],
            compatibility_score=round(0.9 - (i * 0.05), 2),
            common_interests=["독서", "음악", "영화", "여행"][:(i+2)],
            personality_match={
                "mbti_similarity": round(0.95 - (i * 0.05), 2),
                "emotion_compatibility": round(0.88 - (i * 0.03), 2),
                "lifestyle_match": round(0.82 - (i * 0.02), 2)
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
    return {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "overall_compatibility": 0.87,
        "detailed_scores": {
            "personality_match": 0.92,
            "emotion_compatibility": 0.85,
            "lifestyle_similarity": 0.83,
            "interest_overlap": 0.79
        },
        "common_traits": [
            "유사한 MBTI 성격 유형",
            "비슷한 감정 패턴",
            "공통 관심사 다수",
            "라이프스타일 호환성"
        ],
        "compatibility_explanation": "매우 높은 호환성을 보이며, 다양한 영역에서 잘 맞을 것으로 예상됩니다.",
        "calculated_at": datetime.now().isoformat()
    }

# ===========================================
# 서버 실행
# ===========================================

if __name__ == "__main__":
    try:
        import uvicorn
        
        print("=" * 70)
        print("🚀 AI 일기 분석 Mock API 서버 v2.0 시작")
        print("=" * 70)
        print("📝 완전히 독립적인 Mock 서버입니다")
        print("🌐 서버 주소: http://localhost:8000")
        print("📚 API 문서: http://localhost:8000/docs")
        print("🧪 웹 테스트: testweb.html 파일 사용")
        print("🔑 인증 토큰: test-token-for-development")
        print("")
        print("✅ 사용 가능한 모든 API 엔드포인트:")
        print("   • POST /api/v1/auth/register      - 사용자 등록")
        print("   • POST /api/v1/auth/login         - 로그인")
        print("   • POST /api/v1/analysis/diary     - 일기 분석 ⭐")
        print("   • GET  /api/v1/analysis/history   - 분석 이력")
        print("   • POST /api/v1/matching/find      - 매칭 찾기")
        print("   • GET  /api/v1/matching/compatibility - 호환성 계산")
        print("   • POST /api/v1/diary/create       - 일기 작성")
        print("   • GET  /api/v1/diary/list         - 일기 목록")
        print("=" * 70)
        
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except ImportError:
        print("❌ uvicorn이 설치되지 않았습니다.")
        print("💡 다음 명령어로 설치하세요: pip install uvicorn")
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")
