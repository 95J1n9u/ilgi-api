"""
테스트 설정 및 픽스처
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config.database import Base, get_db
from app.config.settings import get_settings

# 테스트 데이터베이스 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 테스트용 비동기 엔진
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# 테스트용 세션 메이커
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
)


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """테스트 데이터베이스 세션"""
    # 테이블 생성
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 세션 생성
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
    
    # 테이블 삭제
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_client(test_db: AsyncSession) -> TestClient:
    """테스트 클라이언트"""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_firebase_user():
    """Mock Firebase 사용자"""
    return {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "email_verified": True
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API 응답"""
    return {
        "primary_emotion": "happiness",
        "secondary_emotions": ["joy", "contentment"],
        "emotion_scores": [
            {"emotion": "happiness", "score": 0.8, "confidence": 0.9},
            {"emotion": "joy", "score": 0.7, "confidence": 0.8}
        ],
        "sentiment_score": 0.7,
        "emotional_intensity": 0.8,
        "emotional_stability": 0.6
    }


@pytest.fixture
def sample_diary_data():
    """샘플 일기 데이터"""
    return {
        "diary_id": "diary_test_123",
        "content": "오늘은 정말 즐거운 하루였다. 친구들과 만나서 맛있는 음식도 먹고, 재미있는 영화도 봤다. 이런 날이 더 많았으면 좋겠다.",
        "metadata": {
            "date": "2024-12-12",
            "weather": "sunny",
            "mood": "happy",
            "activities": ["friends", "meal", "movie"]
        }
    }


@pytest.fixture
def sample_user_data():
    """샘플 사용자 데이터"""
    return {
        "firebase_uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "age": 25,
        "location": "Seoul"
    }


@pytest.fixture
def mock_ai_service():
    """Mock AI 서비스"""
    mock_service = MagicMock()
    
    # Mock 분석 결과
    mock_analysis_result = MagicMock()
    mock_analysis_result.diary_id = "diary_test_123"
    mock_analysis_result.analysis_id = "analysis_test_123"
    mock_analysis_result.status = "completed"
    
    mock_service.analyze_diary.return_value = mock_analysis_result
    mock_service.get_analysis_result.return_value = mock_analysis_result
    
    return mock_service


@pytest.fixture
def auth_headers(mock_firebase_user):
    """인증 헤더"""
    return {
        "Authorization": "Bearer mock_firebase_token"
    }


@pytest.fixture
def sample_emotion_analysis():
    """샘플 감정 분석 결과"""
    from app.schemas.analysis import EmotionAnalysis, EmotionScore
    
    return EmotionAnalysis(
        primary_emotion="happiness",
        secondary_emotions=["joy", "contentment"],
        emotion_scores=[
            EmotionScore(emotion="happiness", score=0.8, confidence=0.9),
            EmotionScore(emotion="joy", score=0.7, confidence=0.8)
        ],
        sentiment_score=0.7,
        emotional_intensity=0.8,
        emotional_stability=0.6
    )


@pytest.fixture
def sample_personality_analysis():
    """샘플 성격 분석 결과"""
    from app.schemas.analysis import PersonalityAnalysis, MBTIIndicators, Big5Traits
    
    return PersonalityAnalysis(
        mbti_indicators=MBTIIndicators(
            E=0.7, I=0.3, S=0.4, N=0.6,
            T=0.3, F=0.7, J=0.6, P=0.4
        ),
        big5_traits=Big5Traits(
            openness=0.75,
            conscientiousness=0.68,
            extraversion=0.82,
            agreeableness=0.79,
            neuroticism=0.23
        ),
        predicted_mbti="ENFJ",
        personality_summary=["외향적이고 사교적인 성향", "감정을 중시하는 결정"],
        confidence_level=0.8
    )


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 설정"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock 설정
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """외부 서비스 Mock"""
    
    # Firebase Admin SDK Mock
    mock_auth = MagicMock()
    mock_auth.verify_id_token.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "email_verified": True
    }
    monkeypatch.setattr("firebase_admin.auth", mock_auth)
    
    # Gemini API Mock
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"primary_emotion": "happiness", "sentiment_score": 0.7}'
    mock_model.generate_content_async.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    monkeypatch.setattr("google.generativeai.GenerativeModel", mock_genai.GenerativeModel)


# 테스트 유틸리티 함수들
def create_test_user(db_session: AsyncSession, user_data: dict = None):
    """테스트 사용자 생성"""
    from app.models.user import User
    
    if user_data is None:
        user_data = {
            "firebase_uid": "test_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    user = User(**user_data)
    db_session.add(user)
    return user


def create_test_diary_analysis(db_session: AsyncSession, user_id: str, analysis_data: dict = None):
    """테스트 일기 분석 생성"""
    from app.models.analysis import DiaryAnalysis
    
    if analysis_data is None:
        analysis_data = {
            "analysis_id": "analysis_test_123",
            "diary_id": "diary_test_123",
            "user_id": user_id,
            "content": "Test diary content",
            "primary_emotion": "happiness",
            "sentiment_score": 0.7,
            "status": "completed"
        }
    
    analysis = DiaryAnalysis(**analysis_data)
    db_session.add(analysis)
    return analysis


# 테스트 설정
pytest_plugins = ["pytest_asyncio"]

# 테스트 환경 변수 설정
import os
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
