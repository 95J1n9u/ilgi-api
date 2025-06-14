"""
main.py에서 Gemini만 테스트하는 버전
데이터베이스 의존성을 제거하고 Gemini API만 연동
"""
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"✅ Gemini API 키 로드됨: {GEMINI_API_KEY[:10]}...")
else:
    print("❌ GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

# FastAPI 앱 설정 (main.py 스타일)
app = FastAPI(
    title="AI Diary Analysis Backend",
    version="1.0.0", 
    description="AI 일기 분석 백엔드 API 서버 (Gemini 연동)",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정 (main.py와 동일)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ===========================================
# 스키마 정의 (원래 프로젝트와 동일)
# ===========================================

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

# ===========================================
# Gemini AI 서비스 (원래 프로젝트 구조와 유사)
# ===========================================

class AIAnalysisService:
    """AI 분석 서비스 - main.py 스타일"""
    
    def __init__(self):
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini Pro 모델 초기화 완료")
        else:
            self.model = None
            print("❌ Gemini API 키가 없어 Mock 모드로 실행")
    
    async def analyze_diary(self, request: DiaryAnalysisRequest) -> DiaryAnalysisResponse:
        """일기 텍스트 종합 AI 분석 - main.py 스타일"""
        start_time = time.time()
        analysis_id = f"main_analysis_{int(time.time())}"
        
        try:
            print(f"🤖 Main.py에서 Gemini 분석 시작: {request.diary_id}")
            
            if self.model:
                # 실제 Gemini 분석
                emotion_analysis = await self._analyze_emotions_gemini(request.content)
                personality_analysis = await self._analyze_personality_gemini(request.content)
                keyword_extraction = await self._extract_keywords_gemini(request.content)
                lifestyle_patterns = await self._analyze_lifestyle_gemini(request.content)
                insights = await self._generate_insights_gemini(request.content, emotion_analysis)
            else:
                # Gemini 키가 없으면 Mock 사용
                emotion_analysis = self._mock_emotion_analysis()
                personality_analysis = self._mock_personality_analysis()
                keyword_extraction = self._mock_keyword_extraction(request.content)
                lifestyle_patterns = self._mock_lifestyle_analysis()
                insights = ["Gemini API 키가 설정되지 않아 Mock 분석을 사용했습니다."]
            
            recommendations = [
                "지속적인 일기 작성으로 감정 패턴을 추적해보세요.",
                "자신만의 성장 패턴을 발견해보세요.",
                "긍정적인 변화를 위한 작은 행동을 시작해보세요."
            ]
            
            processing_time = time.time() - start_time
            
            print(f"✅ Main.py Gemini 분석 완료: {processing_time:.2f}초")
            
            return DiaryAnalysisResponse(
                diary_id=request.diary_id,
                analysis_id=analysis_id,
                user_id="main-user-123",  # main.py에서는 고정
                status="completed",
                emotion_analysis=emotion_analysis,
                personality_analysis=personality_analysis,
                keyword_extraction=keyword_extraction,
                lifestyle_patterns=lifestyle_patterns,
                insights=insights,
                recommendations=recommendations,
                analysis_version="1.0.0-main-gemini",
                processing_time=processing_time,
                confidence_score=0.95 if self.model else 0.6,
                processed_at=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Main.py 분석 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Main.py에서 분석 처리 중 오류 발생: {str(e)}"
            )
    
    async def _analyze_emotions_gemini(self, content: str) -> EmotionAnalysis:
        """Gemini 감정 분석"""
        prompt = f"""
일기 텍스트의 감정을 분석해주세요: "{content}"

JSON 형식으로 응답:
{{
    "primary_emotion": "주요감정",
    "secondary_emotions": ["보조감정1", "보조감정2"],
    "emotion_scores": [{{"emotion": "감정명", "score": 0.8, "confidence": 0.9}}],
    "sentiment_score": 0.5,
    "emotional_intensity": 0.7,
    "emotional_stability": 0.8
}}
"""
        try:
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return EmotionAnalysis(
                primary_emotion=result.get("primary_emotion", "평온"),
                secondary_emotions=result.get("secondary_emotions", []),
                emotion_scores=[EmotionScore(**score) for score in result.get("emotion_scores", [])],
                sentiment_score=result.get("sentiment_score", 0.0),
                emotional_intensity=result.get("emotional_intensity", 0.5),
                emotional_stability=result.get("emotional_stability", 0.7)
            )
        except:
            return self._mock_emotion_analysis()
    
    async def _analyze_personality_gemini(self, content: str) -> PersonalityAnalysis:
        """Gemini 성격 분석"""
        prompt = f"""
일기 텍스트의 성격을 분석해주세요: "{content}"

JSON 형식으로 응답:
{{
    "mbti_indicators": {{"E": 0.6, "I": 0.4, "S": 0.5, "N": 0.5, "T": 0.3, "F": 0.7, "J": 0.6, "P": 0.4}},
    "big5_traits": {{"openness": 0.7, "conscientiousness": 0.6, "extraversion": 0.5, "agreeableness": 0.8, "neuroticism": 0.3}},
    "predicted_mbti": "ENFJ",
    "personality_summary": ["특성1", "특성2"],
    "confidence_level": 0.8
}}
"""
        try:
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return PersonalityAnalysis(
                mbti_indicators=MBTIIndicators(**result.get("mbti_indicators", {})),
                big5_traits=Big5Traits(**result.get("big5_traits", {})),
                predicted_mbti=result.get("predicted_mbti", "INFP"),
                personality_summary=result.get("personality_summary", []),
                confidence_level=result.get("confidence_level", 0.7)
            )
        except:
            return self._mock_personality_analysis()
    
    async def _extract_keywords_gemini(self, content: str) -> KeywordExtraction:
        """Gemini 키워드 추출"""
        try:
            prompt = f'일기에서 키워드를 추출하세요: "{content}"\nJSON: {{"keywords": [], "topics": [], "entities": [], "themes": []}}'
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return KeywordExtraction(**result)
        except:
            return self._mock_keyword_extraction(content)
    
    async def _analyze_lifestyle_gemini(self, content: str) -> LifestylePattern:
        """Gemini 생활 패턴 분석"""
        try:
            prompt = f'일기의 생활 패턴을 분석하세요: "{content}"\nJSON: {{"activity_patterns": {{}}, "social_patterns": {{}}, "time_patterns": {{}}, "interest_areas": [], "values_orientation": {{}}}}'
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return LifestylePattern(**result)
        except:
            return self._mock_lifestyle_analysis()
    
    async def _generate_insights_gemini(self, content: str, emotion: EmotionAnalysis) -> List[str]:
        """Gemini 인사이트 생성"""
        try:
            prompt = f'일기 "{content}"와 감정 "{emotion.primary_emotion}"를 바탕으로 인사이트 3개를 생성하세요.\nJSON: {{"insights": []}}'
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result.get("insights", ["Main.py에서 Gemini가 생성한 인사이트입니다."])
        except:
            return [f"Main.py에서 '{emotion.primary_emotion}' 감정이 주요하게 나타났습니다."]
    
    # Mock 함수들
    def _mock_emotion_analysis(self) -> EmotionAnalysis:
        return EmotionAnalysis(
            primary_emotion="평온",
            secondary_emotions=["관심"],
            emotion_scores=[EmotionScore(emotion="평온", score=0.7, confidence=0.8)],
            sentiment_score=0.1,
            emotional_intensity=0.6,
            emotional_stability=0.8
        )
    
    def _mock_personality_analysis(self) -> PersonalityAnalysis:
        return PersonalityAnalysis(
            mbti_indicators=MBTIIndicators(E=0.5, I=0.5, S=0.5, N=0.5, T=0.4, F=0.6, J=0.6, P=0.4),
            big5_traits=Big5Traits(openness=0.7, conscientiousness=0.6, extraversion=0.5, agreeableness=0.7, neuroticism=0.4),
            predicted_mbti="INFP",
            personality_summary=["내향적 성향", "공감 능력 우수"],
            confidence_level=0.6
        )
    
    def _mock_keyword_extraction(self, content: str) -> KeywordExtraction:
        words = content.split()[:5]
        return KeywordExtraction(keywords=words, topics=["일상"], entities=[], themes=["성찰"])
    
    def _mock_lifestyle_analysis(self) -> LifestylePattern:
        return LifestylePattern(
            activity_patterns={"일상활동": 0.7},
            social_patterns={"혼자시간": 0.6},
            time_patterns={"오후": 0.8},
            interest_areas=["성장"],
            values_orientation={"성찰": 0.8}
        )

# 서비스 인스턴스 생성
ai_service = AIAnalysisService()

# ===========================================
# 인증 (간소화된 버전)
# ===========================================

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """간단한 인증 - main.py 스타일"""
    if not credentials or credentials.credentials != "test-token-for-development":
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    return {"uid": "main-user-123", "email": "main@example.com"}

# ===========================================
# API 엔드포인트 (main.py 스타일 라우팅)
# ===========================================

@app.get("/")
async def root():
    """루트 엔드포인트 - main.py와 동일"""
    return {
        "message": "🤖 AI Diary Analysis Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "gemini_enabled": GEMINI_API_KEY is not None
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인 - main.py와 동일"""
    return {
        "status": "healthy",
        "app_name": "AI Diary Analysis Backend",
        "version": "1.0.0",
        "environment": "development",
        "gemini_status": "enabled" if GEMINI_API_KEY else "disabled"
    }

@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(
    request: DiaryAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """🚀 Main.py에서 Gemini를 사용한 일기 분석"""
    return await ai_service.analyze_diary(request)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Main.py 스타일 AI Diary Backend 서버 시작")
    print(f"🤖 Gemini API: {'✅ 연동됨' if GEMINI_API_KEY else '❌ 키 없음'}")
    print("🌐 http://localhost:8000")
    print("📚 http://localhost:8000/docs")
    
    uvicorn.run(
        "main_gemini_only:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
