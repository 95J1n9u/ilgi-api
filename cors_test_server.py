"""
CORS 문제 해결을 위한 테스트 서버
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Optional

# FastAPI 앱 생성
app = FastAPI(
    title="CORS Test Server",
    version="1.0.0",
    description="CORS 문제 해결을 위한 테스트 서버"
)

# 매우 관대한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
    allow_origin_regex=".*",  # 정규식으로도 모든 origin 허용
)

# 요청 모델
class DiaryAnalysisRequest(BaseModel):
    diary_id: str
    content: str
    analysis_options: Optional[dict] = None

# 응답 모델
class DiaryAnalysisResponse(BaseModel):
    diary_id: str
    emotions: dict
    personality_traits: dict
    sentiment_score: float
    keywords: list
    summary: str

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🤖 CORS Test Server",
        "status": "running",
        "cors": "enabled for all origins"
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "cors_enabled": True,
        "allow_origins": "*"
    }

@app.options("/api/v1/analysis/diary")
async def options_analysis():
    """OPTIONS 요청 핸들러"""
    return {"message": "OPTIONS request successful"}

@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(request: DiaryAnalysisRequest):
    """일기 분석 엔드포인트 - CORS 테스트용 Mock 버전"""
    print(f"📝 일기 분석 요청 받음: diary_id={request.diary_id}")
    print(f"📄 내용 길이: {len(request.content)}자")
    
    # Mock 분석 결과 생성
    content = request.content
    
    # 간단한 감정 분석
    emotions = {
        "joy": 0.8 if any(word in content for word in ["기쁘", "좋", "행복", "즐거"]) else 0.3,
        "sadness": 0.7 if any(word in content for word in ["슬프", "우울", "힘들", "아프"]) else 0.2,
        "anger": 0.6 if any(word in content for word in ["화", "짜증", "분노", "싫"]) else 0.1,
        "fear": 0.5 if any(word in content for word in ["무서", "걱정", "불안", "두려"]) else 0.1,
        "surprise": 0.4 if any(word in content for word in ["놀라", "신기", "예상", "갑자기"]) else 0.2,
        "neutral": 0.5
    }
    
    # 성격 특성 분석
    personality_traits = {
        "openness": 0.7 if any(word in content for word in ["새로운", "창의", "상상", "예술"]) else 0.5,
        "conscientiousness": 0.8 if any(word in content for word in ["계획", "목표", "성실", "노력"]) else 0.5,
        "extraversion": 0.6 if any(word in content for word in ["사람들", "친구", "모임", "대화"]) else 0.4,
        "agreeableness": 0.7 if any(word in content for word in ["도움", "협력", "배려", "친절"]) else 0.5,
        "neuroticism": 0.4 if any(word in content for word in ["스트레스", "걱정", "불안", "긴장"]) else 0.3
    }
    
    # 감정 점수 계산
    sentiment_score = emotions["joy"] - emotions["sadness"] - emotions["anger"]
    
    # 키워드 추출
    keywords = []
    potential_keywords = ["프로젝트", "팀원", "협업", "기대", "걱정", "최선", "노력", "시작", "새로운", "기분"]
    for word in potential_keywords:
        if word in content:
            keywords.append(word)
    
    # 요약 생성
    emotion_type = "긍정적" if sentiment_score > 0.2 else "부정적" if sentiment_score < -0.2 else "중립적"
    summary = f"이 일기는 {emotion_type}인 감정을 담고 있으며, 주요 키워드는 {', '.join(keywords[:3]) if keywords else '일반적인 일상'}입니다."
    
    response = DiaryAnalysisResponse(
        diary_id=request.diary_id,
        emotions=emotions,
        personality_traits=personality_traits,
        sentiment_score=sentiment_score,
        keywords=keywords,
        summary=summary
    )
    
    print(f"✅ 분석 완료: 감정점수={sentiment_score:.2f}")
    return response

@app.post("/api/v1/auth/register")
async def register_user(user_data: dict):
    """사용자 등록 Mock"""
    return {
        "message": "User registered successfully",
        "user_id": "test-user-123",
        "email": user_data.get("email"),
        "name": user_data.get("name")
    }

@app.post("/api/v1/auth/login")
async def login_user(login_data: dict):
    """로그인 Mock"""
    return {
        "message": "Login successful",
        "access_token": "mock-jwt-token",
        "token_type": "bearer",
        "user_id": "test-user-123"
    }

@app.get("/api/v1/analysis/history")
async def get_analysis_history(user_id: str = "test-user-123", limit: int = 10):
    """분석 이력 조회 Mock"""
    return {
        "user_id": user_id,
        "total": 2,
        "analyses": [
            {
                "id": "analysis_1",
                "created_at": "2024-01-01T10:00:00Z",
                "emotions": {"joy": 0.8, "sadness": 0.2},
                "sentiment_score": 0.6
            },
            {
                "id": "analysis_2", 
                "created_at": "2024-01-01T20:00:00Z",
                "emotions": {"joy": 0.5, "sadness": 0.4},
                "sentiment_score": 0.1
            }
        ]
    }

if __name__ == "__main__":
    print("🚀 CORS 테스트 서버 시작...")
    print("🌐 모든 Origin에서 접근 가능하도록 설정됨")
    print("📝 브라우저에서 http://localhost:8000/docs 에서 API 문서 확인")
    print("🧪 testweb.html 파일로 테스트 가능")
    
    uvicorn.run(
        "cors_test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
