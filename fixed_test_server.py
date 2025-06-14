"""
문제 해결된 테스트 서버
- Gemini API 모델을 gemini-1.5-flash로 업데이트
- DB 의존성 없이 작동하는 Mock 서버
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import google.generativeai as genai
import json
import uuid
import time
from datetime import datetime
import uvicorn

# FastAPI 앱 생성
app = FastAPI(
    title="AI Diary Backend - Fixed Test Server",
    version="1.0.0",
    description="Gemini 모델 문제와 CORS 문제를 해결한 테스트 서버"
)

# CORS 설정 (모든 origin 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=".*",
)

# Gemini API 설정 (실제 API 키 필요)
GEMINI_API_KEY = "AIzaSyD-MDfFrllW4aK4WFWb9ExUlgE_QFDCxrg"  # .env에서 가져온 API 키

try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    GEMINI_AVAILABLE = True
    print("✅ Gemini API 설정 완료 (gemini-1.5-flash)")
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"⚠️  Gemini API 설정 실패: {e}")

# 요청/응답 모델
class DiaryAnalysisRequest(BaseModel):
    diary_id: str
    content: str
    user_id: Optional[str] = "test-user-123"
    analysis_options: Optional[Dict] = None

class EmotionScore(BaseModel):
    emotion: str
    score: float
    confidence: float

class EmotionAnalysis(BaseModel):
    primary_emotion: str
    secondary_emotions: List[str]
    emotion_scores: List[EmotionScore]
    sentiment_score: float
    emotional_intensity: float
    emotional_stability: float

class MBTIIndicators(BaseModel):
    E: float = 0.5
    I: float = 0.5
    S: float = 0.5
    N: float = 0.5
    T: float = 0.5
    F: float = 0.5
    J: float = 0.5
    P: float = 0.5

class Big5Traits(BaseModel):
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

class PersonalityAnalysis(BaseModel):
    mbti_indicators: MBTIIndicators
    big5_traits: Big5Traits
    predicted_mbti: Optional[str] = None
    personality_summary: List[str] = []
    confidence_level: float = 0.5

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
    insights: List[str]
    recommendations: List[str]
    analysis_version: str = "1.0"
    processing_time: float
    confidence_score: float
    processed_at: datetime

# 메모리 저장소
temp_analyses = []
temp_users = {}

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🤖 AI Diary Analysis Backend - Fixed Test Server",
        "version": "1.0.0",
        "status": "running",
        "gemini_available": GEMINI_AVAILABLE,
        "model": "gemini-1.5-flash",
        "fixes": [
            "✅ CORS 문제 해결",
            "✅ Gemini 모델 업데이트 (gemini-pro → gemini-1.5-flash)",
            "✅ SQLAlchemy Foreign Key 문제 해결",
            "✅ Mock API로 DB 의존성 제거"
        ]
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "app_name": "AI Diary Backend Fixed Test",
        "version": "1.0.0",
        "gemini_model": "gemini-1.5-flash",
        "gemini_available": GEMINI_AVAILABLE,
        "cors_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

async def analyze_with_gemini(content: str) -> Dict[str, Any]:
    """실제 Gemini API로 감정 분석"""
    if not GEMINI_AVAILABLE:
        raise Exception("Gemini API not available")
    
    prompt = f"""
    다음 한국어 일기 텍스트의 감정을 정확하게 분석해주세요:

    텍스트: "{content}"

    다음 JSON 형식으로 정확히 응답해주세요:
    {{
        "primary_emotion": "주요감정",
        "secondary_emotions": ["보조감정1", "보조감정2"],
        "emotion_scores": [
            {{"emotion": "happiness", "score": 0.85, "confidence": 0.9}},
            {{"emotion": "excitement", "score": 0.65, "confidence": 0.8}}
        ],
        "sentiment_score": 0.7,
        "emotional_intensity": 0.8,
        "emotional_stability": 0.6,
        "mbti_indicators": {{
            "E": 0.7, "I": 0.3,
            "S": 0.4, "N": 0.6,
            "T": 0.3, "F": 0.7,
            "J": 0.6, "P": 0.4
        }},
        "big5_traits": {{
            "openness": 0.75,
            "conscientiousness": 0.68,
            "extraversion": 0.82,
            "agreeableness": 0.79,
            "neuroticism": 0.23
        }},
        "keywords": ["키워드1", "키워드2", "키워드3"],
        "topics": ["주제1", "주제2"],
        "themes": ["테마1", "테마2"]
    }}

    감정 분석 기준:
    1. primary_emotion: 가장 강하게 나타나는 주요 감정
    2. sentiment_score: 전체적인 감정 극성 (-1.0: 매우 부정, 0: 중립, 1.0: 매우 긍정)
    3. emotional_intensity: 감정의 강도 (0.0: 약함, 1.0: 매우 강함)
    4. mbti_indicators: 각 MBTI 차원별 점수 (0.0-1.0)
    5. big5_traits: Big5 성격 특성별 점수 (0.0-1.0)
    """
    
    response = await gemini_model.generate_content_async(prompt)
    
    # JSON 응답 파싱
    response_text = response.text.strip()
    if response_text.startswith('```json'):
        response_text = response_text[7:-3]
    elif response_text.startswith('```'):
        response_text = response_text[3:-3]
    
    return json.loads(response_text)

def create_mock_analysis(content: str) -> Dict[str, Any]:
    """Mock 분석 결과 생성 (Gemini API 실패 시)"""
    # 간단한 키워드 기반 감정 추정
    positive_words = ["좋", "행복", "기쁨", "즐거", "만족", "감사", "기대", "설레"]
    negative_words = ["슬프", "우울", "화", "짜증", "힘들", "스트레스", "걱정", "불안"]
    
    positive_count = sum(1 for word in positive_words if word in content)
    negative_count = sum(1 for word in negative_words if word in content)
    
    if positive_count > negative_count:
        primary_emotion = "happiness"
        sentiment_score = 0.6
        secondary_emotions = ["contentment", "optimism"]
    elif negative_count > positive_count:
        primary_emotion = "sadness"
        sentiment_score = -0.4
        secondary_emotions = ["worry", "melancholy"]
    else:
        primary_emotion = "neutral"
        sentiment_score = 0.0
        secondary_emotions = ["calm", "contemplative"]
    
    return {
        "primary_emotion": primary_emotion,
        "secondary_emotions": secondary_emotions,
        "emotion_scores": [
            {"emotion": primary_emotion, "score": 0.7, "confidence": 0.6},
            {"emotion": secondary_emotions[0], "score": 0.5, "confidence": 0.5}
        ],
        "sentiment_score": sentiment_score,
        "emotional_intensity": 0.6,
        "emotional_stability": 0.7,
        "mbti_indicators": {
            "E": 0.6, "I": 0.4, "S": 0.5, "N": 0.5,
            "T": 0.4, "F": 0.6, "J": 0.5, "P": 0.5
        },
        "big5_traits": {
            "openness": 0.6,
            "conscientiousness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.7,
            "neuroticism": 0.4
        },
        "keywords": ["일기", "감정", "생각"],
        "topics": ["일상", "감정"],
        "themes": ["개인적 성찰"]
    }

@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(request: DiaryAnalysisRequest):
    """일기 분석 - 실제 Gemini API 사용"""
    start_time = time.time()
    analysis_id = f"analysis_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    
    print(f"📝 일기 분석 요청: diary_id={request.diary_id}, content_length={len(request.content)}")
    
    try:
        # Gemini API로 분석 시도
        if GEMINI_AVAILABLE:
            print("🤖 Gemini API로 분석 중...")
            gemini_result = await analyze_with_gemini(request.content)
            print("✅ Gemini 분석 완료")
        else:
            print("⚠️  Gemini API 불가, Mock 분석 사용")
            gemini_result = create_mock_analysis(request.content)
        
        # 응답 객체 생성
        emotion_analysis = EmotionAnalysis(
            primary_emotion=gemini_result["primary_emotion"],
            secondary_emotions=gemini_result["secondary_emotions"],
            emotion_scores=[
                EmotionScore(**score) for score in gemini_result["emotion_scores"]
            ],
            sentiment_score=gemini_result["sentiment_score"],
            emotional_intensity=gemini_result["emotional_intensity"],
            emotional_stability=gemini_result["emotional_stability"]
        )
        
        personality_analysis = PersonalityAnalysis(
            mbti_indicators=MBTIIndicators(**gemini_result["mbti_indicators"]),
            big5_traits=Big5Traits(**gemini_result["big5_traits"]),
            predicted_mbti="ENFP",  # 임시
            personality_summary=["외향적이고 감정적인 성향을 보임"],
            confidence_level=0.7
        )
        
        keyword_extraction = KeywordExtraction(
            keywords=gemini_result["keywords"],
            topics=gemini_result["topics"],
            entities=[],
            themes=gemini_result["themes"]
        )
        
        lifestyle_patterns = LifestylePattern(
            activity_patterns={"독서": 0.7, "운동": 0.5},
            social_patterns={"친구만남": 0.6, "혼자시간": 0.8},
            time_patterns={"오전": 0.3, "오후": 0.8, "저녁": 0.6},
            interest_areas=["자기계발", "인간관계"],
            values_orientation={"성장": 0.8, "관계": 0.7}
        )
        
        insights = [
            "긍정적인 감정 상태를 유지하고 계시네요!",
            "자기 성찰적인 사고를 하는 것으로 보입니다.",
            "일상에서 의미를 찾으려는 노력이 돋보입니다."
        ]
        
        recommendations = [
            "현재의 긍정적인 마음가짐을 계속 유지해보세요.",
            "일기를 통한 자기 성찰을 꾸준히 이어가시길 권합니다.",
            "감정의 변화를 관찰하며 패턴을 파악해보세요."
        ]
        
        processing_time = time.time() - start_time
        
        response = DiaryAnalysisResponse(
            diary_id=request.diary_id,
            analysis_id=analysis_id,
            user_id=request.user_id,
            status="completed",
            emotion_analysis=emotion_analysis,
            personality_analysis=personality_analysis,
            keyword_extraction=keyword_extraction,
            lifestyle_patterns=lifestyle_patterns,
            insights=insights,
            recommendations=recommendations,
            processing_time=processing_time,
            confidence_score=0.75,
            processed_at=datetime.now()
        )
        
        # 메모리에 저장
        temp_analyses.append(response.dict())
        
        print(f"✅ 분석 완료: {analysis_id}, 처리시간: {processing_time:.2f}초")
        return response
        
    except Exception as e:
        print(f"❌ 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 처리 중 오류 발생: {str(e)}")

@app.get("/api/v1/analysis/history")
async def get_analysis_history(user_id: str = "test-user-123", limit: int = 10):
    """분석 이력 조회"""
    user_analyses = [
        analysis for analysis in temp_analyses 
        if analysis.get("user_id") == user_id
    ]
    
    return {
        "user_id": user_id,
        "total": len(user_analyses),
        "analyses": user_analyses[-limit:],
        "message": f"총 {len(user_analyses)}개의 분석 결과가 있습니다."
    }

@app.post("/api/v1/auth/register")
async def register_user(user_data: dict):
    """사용자 등록 Mock"""
    user_id = f"user_{len(temp_users) + 1}"
    temp_users[user_id] = user_data
    
    return {
        "message": "사용자 등록 성공",
        "user_id": user_id,
        "email": user_data.get("email"),
        "name": user_data.get("name")
    }

@app.post("/api/v1/auth/login") 
async def login_user(login_data: dict):
    """로그인 Mock"""
    return {
        "message": "로그인 성공",
        "access_token": "mock-jwt-token-fixed",
        "token_type": "bearer",
        "user_id": "test-user-123"
    }

@app.post("/api/v1/matching/find")
async def find_matching(user_id: str, limit: int = 5):
    """매칭 찾기 Mock"""
    mock_matches = [
        {
            "user_id": "user_match_1",
            "name": "호환되는 사용자 1",
            "compatibility_score": 0.89,
            "common_traits": ["감정적", "외향적", "창의적"]
        },
        {
            "user_id": "user_match_2",
            "name": "호환되는 사용자 2", 
            "compatibility_score": 0.82,
            "common_traits": ["사려깊음", "성실함", "친화적"]
        }
    ]
    
    return {
        "user_id": user_id,
        "matches": mock_matches[:limit],
        "total_candidates": len(mock_matches),
        "message": "매칭 알고리즘이 성공적으로 작동했습니다."
    }

@app.get("/api/v1/matching/compatibility")
async def calculate_compatibility(user1_id: str, user2_id: str):
    """호환성 점수 계산 Mock"""
    return {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "compatibility_score": 0.85,
        "compatibility_breakdown": {
            "personality": 0.88,
            "emotions": 0.82,
            "lifestyle": 0.85,
            "interests": 0.87
        },
        "shared_traits": ["감정적 안정성", "개방성", "친화성"],
        "message": "매우 높은 호환성을 보입니다."
    }

if __name__ == "__main__":
    print("🚀 AI Diary Backend Fixed Test Server 시작...")
    print("🔧 해결된 문제들:")
    print("   ✅ CORS: 모든 origin 허용 (파일 시스템 포함)")
    print("   ✅ Gemini API: gemini-1.5-flash 모델 사용")
    print("   ✅ SQLAlchemy: Foreign Key 관계 문제 해결")
    print("   ✅ DB 의존성: Mock 데이터로 독립 실행")
    print("")
    print("📝 브라우저에서 테스트:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - testweb.html 파일 열어서 테스트")
    print("   - Health Check: http://localhost:8000/health")
    print("")
    print("🤖 실제 Gemini API 분석 지원")
    print("⚡ 모든 데이터는 메모리에 임시 저장 (재시작 시 초기화)")
    
    uvicorn.run(
        "fixed_test_server:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
