"""
UUID 및 JSON 파싱 문제를 해결한 개선된 테스트 서버
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
import re

# FastAPI 앱 생성
app = FastAPI(
    title="AI Diary Backend - Improved Test Server",
    version="1.1.0",
    description="UUID와 JSON 파싱 문제를 해결한 개선된 테스트 서버"
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

# Gemini API 설정
GEMINI_API_KEY = "AIzaSyD-MDfFrllW4aK4WFWb9ExUlgE_QFDCxrg"

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
    user_id: Optional[str] = None  # None이면 자동 생성
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
    analysis_version: str = "1.1"
    processing_time: float
    confidence_score: float
    processed_at: datetime

# 메모리 저장소
temp_analyses = []
temp_users = {}

def generate_uuid() -> str:
    """UUID 생성 헬퍼 함수"""
    return str(uuid.uuid4())

def validate_and_fix_user_id(user_id: Optional[str]) -> str:
    """user_id 검증 및 올바른 UUID로 변환/생성"""
    if not user_id:
        return generate_uuid()
    
    # 이미 올바른 UUID 형식인지 확인
    try:
        uuid.UUID(user_id)
        return user_id
    except ValueError:
        # UUID가 아니면 새로 생성
        print(f"⚠️  잘못된 UUID 형식 '{user_id}', 새 UUID 생성")
        return generate_uuid()

def clean_json_response(response_text: str) -> str:
    """Gemini 응답에서 JSON 부분만 추출"""
    # 마크다운 코드 블록 제거
    if '```json' in response_text:
        start = response_text.find('```json') + 7
        end = response_text.find('```', start)
        if end != -1:
            response_text = response_text[start:end]
    elif '```' in response_text:
        start = response_text.find('```') + 3
        end = response_text.find('```', start)
        if end != -1:
            response_text = response_text[start:end]
    
    # 앞뒤 공백 제거
    response_text = response_text.strip()
    
    # JSON 객체/배열 부분만 추출
    json_start = -1
    json_end = -1
    
    for i, char in enumerate(response_text):
        if char in ['{', '[']:
            json_start = i
            break
    
    if json_start != -1:
        bracket_count = 0
        for i in range(json_start, len(response_text)):
            char = response_text[i]
            if char in ['{', '[']:
                bracket_count += 1
            elif char in ['}', ']']:
                bracket_count -= 1
                if bracket_count == 0:
                    json_end = i + 1
                    break
        
        if json_end != -1:
            response_text = response_text[json_start:json_end]
    
    return response_text

async def analyze_emotions_with_gemini(content: str) -> Dict[str, Any]:
    """Gemini API로 감정 분석"""
    prompt = f"""
    다음 한국어 일기 텍스트의 감정을 분석해주세요:

    텍스트: "{content}"

    다음 JSON 형식으로 정확히 응답해주세요 (마크다운 없이 순수 JSON만):
    {{
        "primary_emotion": "joy",
        "secondary_emotions": ["excitement", "anxiety"],
        "emotion_scores": [
            {{"emotion": "joy", "score": 0.85, "confidence": 0.9}},
            {{"emotion": "excitement", "score": 0.65, "confidence": 0.8}}
        ],
        "sentiment_score": 0.7,
        "emotional_intensity": 0.8,
        "emotional_stability": 0.6
    }}
    """
    
    response = await gemini_model.generate_content_async(prompt)
    response_text = clean_json_response(response.text)
    return json.loads(response_text)

async def analyze_personality_with_gemini(content: str) -> Dict[str, Any]:
    """Gemini API로 성격 분석"""
    prompt = f"""
    다음 일기 텍스트에서 성격 특성을 분석해주세요:

    텍스트: "{content}"

    다음 JSON 형식으로 정확히 응답해주세요 (마크다운 없이 순수 JSON만):
    {{
        "mbti_indicators": {{
            "E": 0.7, "I": 0.3, "S": 0.4, "N": 0.6,
            "T": 0.3, "F": 0.7, "J": 0.6, "P": 0.4
        }},
        "big5_traits": {{
            "openness": 0.75,
            "conscientiousness": 0.68,
            "extraversion": 0.82,
            "agreeableness": 0.79,
            "neuroticism": 0.23
        }},
        "predicted_mbti": "ENFJ",
        "personality_summary": ["외향적이고 감정적인 성향", "새로운 경험에 개방적"]
    }}
    """
    
    response = await gemini_model.generate_content_async(prompt)
    response_text = clean_json_response(response.text)
    return json.loads(response_text)

async def extract_keywords_with_gemini(content: str) -> Dict[str, Any]:
    """키워드 추출 - 간단한 프롬프트 사용"""
    prompt = f"""
    다음 텍스트에서 키워드를 추출해주세요:

    "{content}"

    JSON 형식으로 응답:
    {{
        "keywords": ["키워드1", "키워드2", "키워드3"],
        "topics": ["주제1", "주제2"],
        "entities": ["개체명1"],
        "themes": ["테마1", "테마2"]
    }}
    """
    
    try:
        response = await gemini_model.generate_content_async(prompt)
        response_text = clean_json_response(response.text)
        return json.loads(response_text)
    except Exception as e:
        print(f"키워드 추출 실패: {e}")
        # 기본값 반환
        return {
            "keywords": ["일기", "감정", "생각"],
            "topics": ["일상", "감정"],
            "entities": [],
            "themes": ["개인적 성찰"]
        }

def create_mock_analysis(content: str) -> Dict[str, Any]:
    """Mock 분석 결과 생성 (Gemini API 실패 시)"""
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
        "emotions": {
            "primary_emotion": primary_emotion,
            "secondary_emotions": secondary_emotions,
            "emotion_scores": [
                {"emotion": primary_emotion, "score": 0.7, "confidence": 0.6},
                {"emotion": secondary_emotions[0], "score": 0.5, "confidence": 0.5}
            ],
            "sentiment_score": sentiment_score,
            "emotional_intensity": 0.6,
            "emotional_stability": 0.7
        },
        "personality": {
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
            "predicted_mbti": "ISFJ",
            "personality_summary": ["균형잡힌 성격", "안정적인 성향"]
        },
        "keywords": {
            "keywords": ["일기", "감정", "생각"],
            "topics": ["일상", "감정"],
            "entities": [],
            "themes": ["개인적 성찰"]
        }
    }

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🤖 AI Diary Analysis Backend - Improved Test Server",
        "version": "1.1.0",
        "status": "running",
        "gemini_available": GEMINI_AVAILABLE,
        "model": "gemini-1.5-flash",
        "improvements": [
            "✅ UUID 형식 문제 해결",
            "✅ JSON 파싱 오류 해결",
            "✅ 에러 처리 개선",
            "✅ Gemini API 응답 정제",
            "✅ CORS 문제 해결 유지"
        ]
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "app_name": "AI Diary Backend Improved Test",
        "version": "1.1.0",
        "gemini_model": "gemini-1.5-flash",
        "gemini_available": GEMINI_AVAILABLE,
        "cors_enabled": True,
        "uuid_validation": True,
        "json_parsing_improved": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(request: DiaryAnalysisRequest):
    """일기 분석 - 개선된 버전"""
    start_time = time.time()
    analysis_id = f"analysis_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    
    # user_id 검증 및 올바른 UUID로 변환
    valid_user_id = validate_and_fix_user_id(request.user_id)
    
    print(f"📝 일기 분석 요청: diary_id={request.diary_id}, user_id={valid_user_id}, content_length={len(request.content)}")
    
    try:
        if GEMINI_AVAILABLE:
            print("🤖 Gemini API로 분석 중...")
            
            # 각 분석을 개별적으로 수행하여 오류 격리
            try:
                emotion_result = await analyze_emotions_with_gemini(request.content)
                print("✅ 감정 분석 완료")
            except Exception as e:
                print(f"⚠️  감정 분석 실패, Mock 사용: {e}")
                mock_data = create_mock_analysis(request.content)
                emotion_result = mock_data["emotions"]
            
            try:
                personality_result = await analyze_personality_with_gemini(request.content)
                print("✅ 성격 분석 완료")
            except Exception as e:
                print(f"⚠️  성격 분석 실패, Mock 사용: {e}")
                mock_data = create_mock_analysis(request.content)
                personality_result = mock_data["personality"]
            
            try:
                keyword_result = await extract_keywords_with_gemini(request.content)
                print("✅ 키워드 추출 완료")
            except Exception as e:
                print(f"⚠️  키워드 추출 실패, Mock 사용: {e}")
                mock_data = create_mock_analysis(request.content)
                keyword_result = mock_data["keywords"]
            
        else:
            print("⚠️  Gemini API 불가, Mock 분석 사용")
            mock_data = create_mock_analysis(request.content)
            emotion_result = mock_data["emotions"]
            personality_result = mock_data["personality"]
            keyword_result = mock_data["keywords"]
        
        # 응답 객체 생성
        emotion_analysis = EmotionAnalysis(
            primary_emotion=emotion_result["primary_emotion"],
            secondary_emotions=emotion_result["secondary_emotions"],
            emotion_scores=[
                EmotionScore(**score) for score in emotion_result["emotion_scores"]
            ],
            sentiment_score=emotion_result["sentiment_score"],
            emotional_intensity=emotion_result["emotional_intensity"],
            emotional_stability=emotion_result["emotional_stability"]
        )
        
        personality_analysis = PersonalityAnalysis(
            mbti_indicators=MBTIIndicators(**personality_result["mbti_indicators"]),
            big5_traits=Big5Traits(**personality_result["big5_traits"]),
            predicted_mbti=personality_result.get("predicted_mbti", "ISFJ"),
            personality_summary=personality_result.get("personality_summary", ["균형잡힌 성격"]),
            confidence_level=0.8
        )
        
        keyword_extraction = KeywordExtraction(
            keywords=keyword_result["keywords"],
            topics=keyword_result["topics"],
            entities=keyword_result.get("entities", []),
            themes=keyword_result.get("themes", [])
        )
        
        # 라이프스타일 패턴 (Mock)
        lifestyle_patterns = LifestylePattern(
            activity_patterns={"독서": 0.7, "운동": 0.5, "사교활동": 0.6},
            social_patterns={"친구만남": 0.6, "혼자시간": 0.8, "가족시간": 0.7},
            time_patterns={"오전": 0.3, "오후": 0.8, "저녁": 0.6},
            interest_areas=["자기계발", "인간관계", "건강"],
            values_orientation={"성장": 0.8, "관계": 0.7, "안정": 0.6}
        )
        
        # 인사이트 및 추천 (개선된 버전)
        insights = [
            f"{emotion_analysis.primary_emotion} 감정이 주로 나타나고 있습니다.",
            f"감정 안정성이 {emotion_analysis.emotional_stability:.1f} 수준으로 {'양호' if emotion_analysis.emotional_stability > 0.6 else '개선이 필요'}합니다.",
            f"성격적으로 {personality_analysis.predicted_mbti} 특성을 보이고 있습니다."
        ]
        
        recommendations = [
            "현재의 감정 상태를 잘 관찰하고 계시네요.",
            "일기를 통한 자기 성찰을 계속 이어가시길 권합니다.",
            "감정의 변화 패턴을 파악해보시는 것도 도움이 될 것 같습니다."
        ]
        
        processing_time = time.time() - start_time
        
        response = DiaryAnalysisResponse(
            diary_id=request.diary_id,
            analysis_id=analysis_id,
            user_id=valid_user_id,  # 검증된 UUID 사용
            status="completed",
            emotion_analysis=emotion_analysis,
            personality_analysis=personality_analysis,
            keyword_extraction=keyword_extraction,
            lifestyle_patterns=lifestyle_patterns,
            insights=insights,
            recommendations=recommendations,
            processing_time=processing_time,
            confidence_score=0.85,
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
async def get_analysis_history(user_id: str = None, limit: int = 10):
    """분석 이력 조회 - UUID 검증 포함"""
    # user_id가 제공되지 않으면 모든 분석 반환
    if not user_id:
        return {
            "total": len(temp_analyses),
            "analyses": temp_analyses[-limit:],
            "message": "모든 분석 결과를 반환합니다."
        }
    
    # UUID 형식 검증
    valid_user_id = validate_and_fix_user_id(user_id)
    
    user_analyses = [
        analysis for analysis in temp_analyses 
        if analysis.get("user_id") == valid_user_id
    ]
    
    return {
        "user_id": valid_user_id,
        "total": len(user_analyses),
        "analyses": user_analyses[-limit:],
        "message": f"사용자 {valid_user_id}의 분석 결과 {len(user_analyses)}개를 찾았습니다."
    }

@app.post("/api/v1/auth/register")
async def register_user(user_data: dict):
    """사용자 등록 - UUID 생성"""
    user_id = generate_uuid()
    user_data["user_id"] = user_id
    temp_users[user_id] = user_data
    
    return {
        "message": "사용자 등록 성공",
        "user_id": user_id,
        "email": user_data.get("email"),
        "name": user_data.get("name")
    }

@app.post("/api/v1/auth/login") 
async def login_user(login_data: dict):
    """로그인 - UUID 반환"""
    return {
        "message": "로그인 성공",
        "access_token": "mock-jwt-token-improved",
        "token_type": "bearer",
        "user_id": generate_uuid()  # 실제 UUID 반환
    }

@app.post("/api/v1/matching/find")
async def find_matching(request: dict):
    """매칭 찾기 - UUID 검증 포함"""
    user_id = validate_and_fix_user_id(request.get("user_id"))
    limit = request.get("limit", 5)
    
    mock_matches = [
        {
            "user_id": generate_uuid(),
            "name": "호환되는 사용자 1",
            "compatibility_score": 0.89,
            "common_traits": ["감정적", "외향적", "창의적"]
        },
        {
            "user_id": generate_uuid(),
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
    """호환성 점수 계산 - UUID 검증 포함"""
    valid_user1_id = validate_and_fix_user_id(user1_id)
    valid_user2_id = validate_and_fix_user_id(user2_id)
    
    return {
        "user1_id": valid_user1_id,
        "user2_id": valid_user2_id,
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
    print("🚀 AI Diary Backend Improved Test Server 시작...")
    print("🔧 개선된 사항들:")
    print("   ✅ UUID 검증 및 자동 생성")
    print("   ✅ JSON 파싱 오류 처리 개선")
    print("   ✅ Gemini API 응답 정제")
    print("   ✅ 개별 분석 오류 격리")
    print("   ✅ CORS 문제 해결 유지")
    print("")
    print("📝 브라우저에서 테스트:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - testweb.html 파일 열어서 테스트")
    print("   - Health Check: http://localhost:8000/health")
    print("")
    print("🤖 실제 Gemini API 분석 지원 (개선된 안정성)")
    print("⚡ 모든 데이터는 메모리에 임시 저장 (재시작 시 초기화)")
    
    uvicorn.run(
        "improved_test_server:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
