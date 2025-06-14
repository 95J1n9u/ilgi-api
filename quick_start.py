"""
Firebase 없이 빠르게 실행할 수 있는 기본 서버
D:\ai-diary-backend\quick_start.py 로 저장하고 실행하세요
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# FastAPI 앱 생성
app = FastAPI(
    title="AI Diary Backend - Quick Start",
    version="1.0.0",
    description="Firebase 없이 기본 기능만 실행하는 빠른 시작 버전"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 데이터 모델
class DiaryAnalysisRequest(BaseModel):
    content: str
    analysis_type: Optional[str] = "emotion"

class DiaryAnalysisResponse(BaseModel):
    emotions: dict
    sentiment_score: float
    keywords: List[str]
    summary: str

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: str

# 메모리 기반 임시 데이터 저장소
temp_users = {}
temp_analyses = []

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🤖 AI Diary Analysis Backend - Quick Start",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "Basic diary analysis",
            "User registration (memory only)",
            "Health check",
            "API documentation"
        ]
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "app_name": "AI Diary Backend Quick Start",
        "version": "1.0.0",
        "database": "memory (temporary)",
        "ai_service": "mock (demo mode)"
    }

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register_user(user_data: UserRegisterRequest):
    """사용자 등록 (메모리 기반)"""
    user_id = f"user_{len(temp_users) + 1}"
    
    # 이메일 중복 체크
    if any(user.get("email") == user_data.email for user in temp_users.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 저장
    temp_users[user_id] = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "age": user_data.age,
        "gender": user_data.gender,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    return UserResponse(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        created_at="2024-01-01T00:00:00Z"
    )

@app.post("/api/v1/analysis/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(request: DiaryAnalysisRequest):
    """일기 분석 (Mock 버전)"""
    content = request.content
    
    # 간단한 감정 분석 Mock
    emotions = {
        "joy": 0.7 if "기쁘" in content or "좋" in content or "행복" in content else 0.2,
        "sadness": 0.6 if "슬프" in content or "우울" in content or "힘들" in content else 0.1,
        "anger": 0.5 if "화" in content or "짜증" in content or "분노" in content else 0.1,
        "fear": 0.4 if "무서" in content or "걱정" in content or "불안" in content else 0.1,
        "surprise": 0.3,
        "neutral": 0.4
    }
    
    # 감정 점수 계산 (단순화)
    sentiment_score = emotions["joy"] - emotions["sadness"] - emotions["anger"]
    
    # 키워드 추출 (단순화)
    keywords = []
    common_words = ["프로젝트", "팀원", "협업", "기대", "걱정", "최선", "노력", "시작"]
    for word in common_words:
        if word in content:
            keywords.append(word)
    
    # 요약 생성 (단순화)
    summary = f"총 {len(content)}자의 일기에서 주요 감정은 {'긍정적' if sentiment_score > 0 else '부정적' if sentiment_score < 0 else '중립적'}입니다."
    
    # 분석 결과 저장
    analysis_result = {
        "content": content,
        "emotions": emotions,
        "sentiment_score": sentiment_score,
        "keywords": keywords,
        "summary": summary,
        "analyzed_at": "2024-01-01T00:00:00Z"
    }
    temp_analyses.append(analysis_result)
    
    return DiaryAnalysisResponse(
        emotions=emotions,
        sentiment_score=sentiment_score,
        keywords=keywords,
        summary=summary
    )

@app.get("/api/v1/analysis/history")
async def get_analysis_history(limit: int = 10):
    """분석 이력 조회"""
    return {
        "total": len(temp_analyses),
        "data": temp_analyses[-limit:] if temp_analyses else [],
        "message": "Mock data - 메모리에 임시 저장된 분석 결과입니다"
    }

@app.get("/api/v1/users")
async def get_users():
    """등록된 사용자 목록 (개발용)"""
    return {
        "total": len(temp_users),
        "users": list(temp_users.values()),
        "message": "Mock data - 메모리에 임시 저장된 사용자입니다"
    }

@app.post("/api/v1/matching/find")
async def find_matching(user_id: str, limit: int = 5):
    """매칭 찾기 (Mock 버전)"""
    if user_id not in temp_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mock 매칭 결과
    mock_matches = [
        {
            "user_id": "user_match_1",
            "name": "매칭 사용자 1",
            "compatibility_score": 0.85,
            "common_interests": ["독서", "영화감상", "여행"]
        },
        {
            "user_id": "user_match_2", 
            "name": "매칭 사용자 2",
            "compatibility_score": 0.78,
            "common_interests": ["운동", "음악", "요리"]
        }
    ]
    
    return {
        "user_id": user_id,
        "matches": mock_matches[:limit],
        "message": "Mock data - 실제 매칭 알고리즘이 적용되지 않은 데모 데이터입니다"
    }

if __name__ == "__main__":
    print("🚀 AI Diary Backend Quick Start 실행 중...")
    print("📝 Firebase 없이 기본 기능만 제공합니다")
    print("🌐 브라우저에서 http://localhost:8000/docs 에서 API 테스트 가능")
    print("⚡ 모든 데이터는 메모리에 임시 저장됩니다 (재시작 시 초기화)")
    
    uvicorn.run(
        "quick_start:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
