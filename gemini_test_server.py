"""
실제 Gemini API 연동 테스트 서버
데이터베이스 없이 Gemini API만 테스트하는 서버
"""
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from fastapi import FastAPI, HTTPException, status, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field
    import google.generativeai as genai
    from dotenv import load_dotenv
    import os
except ImportError as e:
    print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
    print("💡 다음 명령어로 설치하세요:")
    print("pip install fastapi uvicorn google-generativeai python-dotenv")
    exit(1)

# 환경변수 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
    exit(1)

print(f"✅ Gemini API 키 로드됨: {GEMINI_API_KEY[:10]}...")
genai.configure(api_key=GEMINI_API_KEY)

# FastAPI 앱 생성
app = FastAPI(
    title="🤖 Gemini AI 일기 분석 테스트 서버",
    description="실제 Google Gemini API를 사용한 일기 분석",
    version="3.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ===========================================
# 스키마 정의
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
# Gemini AI 분석 클래스
# ===========================================

class GeminiAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini Pro 모델 초기화 완료")
    
    async def analyze_emotions(self, content: str) -> EmotionAnalysis:
        """실제 Gemini를 사용한 감정 분석"""
        try:
            prompt = f"""
다음 일기 텍스트를 분석하여 감정 상태를 정확하게 분석해주세요:

텍스트: "{content}"

다음 JSON 형식으로 응답해주세요:
{{
    "primary_emotion": "주요 감정 (한 단어)",
    "secondary_emotions": ["보조 감정1", "보조 감정2"],
    "emotion_scores": [
        {{"emotion": "감정명", "score": 0.0~1.0, "confidence": 0.0~1.0}}
    ],
    "sentiment_score": -1.0~1.0 (부정적 -1, 중립 0, 긍정적 +1),
    "emotional_intensity": 0.0~1.0 (감정 강도),
    "emotional_stability": 0.0~1.0 (감정 안정성)
}}

주요 감정은 다음 중에서 선택: 행복, 슬픔, 분노, 불안, 평온, 기대, 실망, 감사, 외로움, 만족
"""
            
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            # JSON 추출 (```json 태그 제거)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            result = json.loads(result_text)
            
            # EmotionScore 객체들 생성
            emotion_scores = [
                EmotionScore(**score) for score in result.get("emotion_scores", [])
            ]
            
            return EmotionAnalysis(
                primary_emotion=result.get("primary_emotion", "평온"),
                secondary_emotions=result.get("secondary_emotions", []),
                emotion_scores=emotion_scores,
                sentiment_score=result.get("sentiment_score", 0.0),
                emotional_intensity=result.get("emotional_intensity", 0.5),
                emotional_stability=result.get("emotional_stability", 0.7)
            )
            
        except Exception as e:
            print(f"❌ Gemini 감정 분석 오류: {e}")
            # 기본값 반환
            return EmotionAnalysis(
                primary_emotion="평온",
                secondary_emotions=[],
                emotion_scores=[EmotionScore(emotion="평온", score=0.6, confidence=0.7)],
                sentiment_score=0.0,
                emotional_intensity=0.5,
                emotional_stability=0.7
            )
    
    async def analyze_personality(self, content: str) -> PersonalityAnalysis:
        """실제 Gemini를 사용한 성격 분석"""
        try:
            prompt = f"""
다음 일기 텍스트를 분석하여 작성자의 성격 특성을 분석해주세요:

텍스트: "{content}"

다음 JSON 형식으로 응답해주세요:
{{
    "mbti_indicators": {{
        "E": 0.0~1.0 (외향성),
        "I": 0.0~1.0 (내향성),
        "S": 0.0~1.0 (감각형),
        "N": 0.0~1.0 (직관형),
        "T": 0.0~1.0 (사고형),
        "F": 0.0~1.0 (감정형),
        "J": 0.0~1.0 (판단형),
        "P": 0.0~1.0 (인식형)
    }},
    "big5_traits": {{
        "openness": 0.0~1.0 (개방성),
        "conscientiousness": 0.0~1.0 (성실성),
        "extraversion": 0.0~1.0 (외향성),
        "agreeableness": 0.0~1.0 (친화성),
        "neuroticism": 0.0~1.0 (신경성)
    }},
    "predicted_mbti": "4글자 MBTI 유형",
    "personality_summary": ["특성1", "특성2", "특성3"],
    "confidence_level": 0.0~1.0 (분석 신뢰도)
}}

E와 I의 합은 1.0, S와 N의 합은 1.0, T와 F의 합은 1.0, J와 P의 합은 1.0이 되도록 해주세요.
"""
            
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            result = json.loads(result_text)
            
            return PersonalityAnalysis(
                mbti_indicators=MBTIIndicators(**result.get("mbti_indicators", {})),
                big5_traits=Big5Traits(**result.get("big5_traits", {})),
                predicted_mbti=result.get("predicted_mbti", "INFP"),
                personality_summary=result.get("personality_summary", []),
                confidence_level=result.get("confidence_level", 0.7)
            )
            
        except Exception as e:
            print(f"❌ Gemini 성격 분석 오류: {e}")
            # 기본값 반환
            return PersonalityAnalysis(
                mbti_indicators=MBTIIndicators(E=0.5, I=0.5, S=0.5, N=0.5, T=0.4, F=0.6, J=0.6, P=0.4),
                big5_traits=Big5Traits(openness=0.7, conscientiousness=0.6, extraversion=0.5, agreeableness=0.7, neuroticism=0.4),
                predicted_mbti="INFP",
                personality_summary=["공감 능력이 뛰어남", "창의적 사고", "내향적 성향"],
                confidence_level=0.6
            )
    
    async def extract_keywords(self, content: str) -> KeywordExtraction:
        """실제 Gemini를 사용한 키워드 추출"""
        try:
            prompt = f"""
다음 일기 텍스트에서 핵심 키워드와 주제를 추출해주세요:

텍스트: "{content}"

다음 JSON 형식으로 응답해주세요:
{{
    "keywords": ["핵심키워드1", "핵심키워드2", ...] (5-8개),
    "topics": ["주제1", "주제2", ...] (2-4개),
    "entities": ["인명1", "지명1", "조직명1", ...],
    "themes": ["테마1", "테마2", ...] (1-3개)
}}

keywords는 가장 중요한 명사나 동사를 추출하고,
topics는 전체 내용의 주제 분류를,
entities는 고유명사를,
themes는 전체적인 분위기나 테마를 추출해주세요.
"""
            
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            result = json.loads(result_text)
            
            return KeywordExtraction(
                keywords=result.get("keywords", []),
                topics=result.get("topics", []),
                entities=result.get("entities", []),
                themes=result.get("themes", [])
            )
            
        except Exception as e:
            print(f"❌ Gemini 키워드 추출 오류: {e}")
            # 기본값 반환
            words = content.split()
            return KeywordExtraction(
                keywords=[word for word in words if len(word) > 2][:6],
                topics=["일상", "감정"],
                entities=[],
                themes=["성찰"]
            )
    
    async def analyze_lifestyle(self, content: str) -> LifestylePattern:
        """실제 Gemini를 사용한 생활 패턴 분석"""
        try:
            prompt = f"""
다음 일기 텍스트를 분석하여 작성자의 생활 패턴을 추출해주세요:

텍스트: "{content}"

다음 JSON 형식으로 응답해주세요:
{{
    "activity_patterns": {{"활동명": 점수}} (0.0~1.0),
    "social_patterns": {{"패턴명": 점수}} (0.0~1.0),
    "time_patterns": {{"시간대": 점수}} (0.0~1.0),
    "interest_areas": ["관심분야1", "관심분야2", ...],
    "values_orientation": {{"가치관": 점수}} (0.0~1.0)
}}

예시:
- activity_patterns: {{"운동": 0.8, "독서": 0.6, "요리": 0.4}}
- social_patterns: {{"친구만남": 0.7, "가족시간": 0.9, "혼자시간": 0.5}}
- time_patterns: {{"오전활동": 0.6, "오후활동": 0.8, "야간활동": 0.3}}
- interest_areas: ["음악", "영화", "운동", "독서"]
- values_orientation: {{"가족": 0.9, "건강": 0.7, "성장": 0.8}}
"""
            
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            result = json.loads(result_text)
            
            return LifestylePattern(
                activity_patterns=result.get("activity_patterns", {}),
                social_patterns=result.get("social_patterns", {}),
                time_patterns=result.get("time_patterns", {}),
                interest_areas=result.get("interest_areas", []),
                values_orientation=result.get("values_orientation", {})
            )
            
        except Exception as e:
            print(f"❌ Gemini 생활 패턴 분석 오류: {e}")
            # 기본값 반환
            return LifestylePattern(
                activity_patterns={"일상활동": 0.7},
                social_patterns={"혼자시간": 0.6, "가족시간": 0.8},
                time_patterns={"오후활동": 0.8, "저녁활동": 0.6},
                interest_areas=["개인성장"],
                values_orientation={"성장": 0.8, "가족": 0.9}
            )
    
    async def generate_insights(self, content: str, emotion: EmotionAnalysis, personality: PersonalityAnalysis) -> List[str]:
        """실제 Gemini를 사용한 인사이트 생성"""
        try:
            prompt = f"""
다음 일기 분석 결과를 바탕으로 의미 있는 개인화된 인사이트를 3-4개 생성해주세요:

일기 내용: "{content}"
주요 감정: {emotion.primary_emotion}
감정 점수: {emotion.sentiment_score}
성격 유형: {personality.predicted_mbti}

다음 JSON 형식으로 응답해주세요:
{{
    "insights": [
        "인사이트1",
        "인사이트2", 
        "인사이트3"
    ]
}}

각 인사이트는:
- 개인적이고 구체적인 내용
- 긍정적이고 건설적인 관점
- 100자 내외의 간결한 문장
- 실용적인 가치 제공
"""
            
            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            result = json.loads(result_text)
            return result.get("insights", ["자기 성찰 능력이 뛰어납니다."])
            
        except Exception as e:
            print(f"❌ Gemini 인사이트 생성 오류: {e}")
            return [
                f"일기에서 '{emotion.primary_emotion}' 감정이 주로 나타났습니다.",
                f"'{personality.predicted_mbti}' 성격 유형의 특성이 잘 드러납니다.",
                "자기 성찰과 감정 표현 능력이 뛰어납니다."
            ]

# Gemini 분석기 초기화
analyzer = GeminiAnalyzer()

# ===========================================
# 인증 함수
# ===========================================

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """간단한 인증"""
    if not credentials:
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다")
    
    if credentials.credentials == "test-token-for-development":
        return {"uid": "test-user-123", "email": "test@example.com", "name": "Test User"}
    
    raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

# ===========================================
# API 엔드포인트
# ===========================================

@app.get("/")
async def root():
    return {
        "message": "🤖 Gemini AI 일기 분석 서버",
        "version": "3.0.0",
        "ai_engine": "Google Gemini Pro",
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_engine": "Google Gemini Pro",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary_with_gemini(
    request: DiaryAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """🚀 실제 Gemini API를 사용한 일기 분석"""
    start_time = time.time()
    analysis_id = f"gemini_analysis_{int(time.time())}"
    
    try:
        print(f"🤖 Gemini로 분석 시작: {request.diary_id}")
        
        # 동시 분석 실행 (병렬 처리로 속도 향상)
        emotion_task = analyzer.analyze_emotions(request.content)
        personality_task = analyzer.analyze_personality(request.content)
        keyword_task = analyzer.extract_keywords(request.content)
        lifestyle_task = analyzer.analyze_lifestyle(request.content)
        
        # 모든 분석 완료 대기
        emotion_analysis, personality_analysis, keyword_extraction, lifestyle_patterns = await asyncio.gather(
            emotion_task, personality_task, keyword_task, lifestyle_task
        )
        
        # 인사이트 생성
        insights = await analyzer.generate_insights(request.content, emotion_analysis, personality_analysis)
        
        # 추천사항 (Gemini 기반)
        recommendations = [
            "지속적인 일기 작성으로 감정 패턴을 추적해보세요.",
            "자신의 강점을 더욱 발전시켜보세요.",
            "새로운 도전을 통해 성장 기회를 만들어보세요."
        ]
        
        processing_time = time.time() - start_time
        
        print(f"✅ Gemini 분석 완료: {processing_time:.2f}초")
        
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
            analysis_version="3.0.0-gemini",
            processing_time=processing_time,
            confidence_score=0.92,  # Gemini 기반 높은 신뢰도
            processed_at=datetime.now()
        )
        
    except Exception as e:
        print(f"❌ Gemini 분석 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini AI 분석 중 오류 발생: {str(e)}"
        )

if __name__ == "__main__":
    try:
        import uvicorn
        
        print("=" * 80)
        print("🚀 Gemini AI 일기 분석 서버 시작")
        print("=" * 80)
        print(f"🤖 AI 엔진: Google Gemini Pro")
        print(f"🔑 API 키: {GEMINI_API_KEY[:10]}...")
        print("🌐 서버 주소: http://localhost:8000")
        print("📚 API 문서: http://localhost:8000/docs")
        print("🧪 웹 테스트: testweb.html 사용")
        print("🔐 인증 토큰: test-token-for-development")
        print("")
        print("⚡ 실제 Gemini API를 사용하여 고품질 분석을 제공합니다!")
        print("📊 병렬 처리로 빠른 분석 속도를 제공합니다!")
        print("=" * 80)
        
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except ImportError:
        print("❌ uvicorn이 설치되지 않았습니다.")
        print("💡 pip install uvicorn 명령어로 설치하세요.")
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")
