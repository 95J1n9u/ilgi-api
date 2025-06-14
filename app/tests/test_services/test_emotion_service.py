"""
감정 분석 서비스 테스트
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.emotion_service import EmotionAnalysisService
from app.schemas.analysis import EmotionAnalysis, EmotionScore


class TestEmotionAnalysisService:
    """감정 분석 서비스 테스트 클래스"""
    
    @pytest.fixture
    def emotion_service(self):
        """감정 분석 서비스 인스턴스"""
        return EmotionAnalysisService()
    
    @pytest.fixture
    def sample_content(self):
        """샘플 일기 내용"""
        return "오늘은 정말 즐거운 하루였다. 친구들과 만나서 맛있는 음식도 먹고, 재미있는 영화도 봤다."
    
    @pytest.fixture
    def sample_metadata(self):
        """샘플 메타데이터"""
        return {
            "weather": "sunny",
            "mood": "happy",
            "activities": ["friends", "meal", "movie"]
        }
    
    @pytest.fixture
    def mock_gemini_response(self):
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
            "emotional_stability": 0.6,
            "emotion_explanation": "긍정적인 감정이 주를 이룸"
        }
    
    @pytest.mark.asyncio
    async def test_analyze_emotions_success(
        self, 
        emotion_service: EmotionAnalysisService,
        sample_content: str,
        sample_metadata: dict,
        mock_gemini_response: dict
    ):
        """감정 분석 성공 테스트"""
        with patch.object(emotion_service.model, 'generate_content_async') as mock_generate:
            # Mock Gemini API 응답
            mock_response = MagicMock()
            mock_response.text = f'```json\n{mock_gemini_response}\n```'
            mock_generate.return_value = mock_response
            
            # 감정 분석 실행
            result = await emotion_service.analyze_emotions(sample_content, sample_metadata)
            
            # 결과 검증
            assert isinstance(result, EmotionAnalysis)
            assert result.primary_emotion == "happiness"
            assert "joy" in result.secondary_emotions
            assert len(result.emotion_scores) > 0
            assert -1.0 <= result.sentiment_score <= 1.0
            assert 0.0 <= result.emotional_intensity <= 1.0
            assert 0.0 <= result.emotional_stability <= 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_emotions_with_textblob_fallback(
        self,
        emotion_service: EmotionAnalysisService,
        sample_content: str
    ):
        """TextBlob 백업 감정 분석 테스트"""
        with patch.object(emotion_service.model, 'generate_content_async') as mock_generate:
            # Gemini API 실패 시뮬레이션
            mock_generate.side_effect = Exception("API Error")
            
            # 백업 분석 실행
            result = await emotion_service.analyze_emotions(sample_content)
            
            # 백업 결과 검증
            assert isinstance(result, EmotionAnalysis)
            assert result.primary_emotion in ["happiness", "sadness", "neutral"]
            assert isinstance(result.sentiment_score, float)
    
    def test_analyze_with_textblob(self, emotion_service: EmotionAnalysisService):
        """TextBlob 감정 분석 테스트"""
        positive_text = "I am very happy today!"
        negative_text = "I feel sad and disappointed."
        neutral_text = "This is a normal day."
        
        # 긍정적 텍스트
        result_positive = emotion_service._analyze_with_textblob(positive_text)
        assert result_positive["polarity"] > 0
        
        # 부정적 텍스트
        result_negative = emotion_service._analyze_with_textblob(negative_text)
        assert result_negative["polarity"] < 0
        
        # 중립적 텍스트
        result_neutral = emotion_service._analyze_with_textblob(neutral_text)
        assert abs(result_neutral["polarity"]) < 0.5
    
    def test_analyze_metadata_emotions(self, emotion_service: EmotionAnalysisService):
        """메타데이터 기반 감정 분석 테스트"""
        # 긍정적 메타데이터
        positive_metadata = {
            "weather": "sunny",
            "mood": "happy",
            "activities": ["friends", "exercise"]
        }
        
        result_positive = emotion_service._analyze_metadata_emotions(positive_metadata)
        assert "weather_boost" in result_positive
        assert result_positive["weather_boost"] > 0
        
        # 부정적 메타데이터
        negative_metadata = {
            "weather": "rainy",
            "mood": "sad",
            "activities": ["work", "stress"]
        }
        
        result_negative = emotion_service._analyze_metadata_emotions(negative_metadata)
        assert result_negative["weather_boost"] < 0
    
    def test_validate_gemini_result(self, emotion_service: EmotionAnalysisService):
        """Gemini 결과 검증 테스트"""
        # 유효한 결과
        valid_result = {
            "primary_emotion": "happiness",
            "secondary_emotions": ["joy", "contentment"],
            "emotion_scores": [
                {"emotion": "happiness", "score": 0.8, "confidence": 0.9}
            ],
            "sentiment_score": 0.7,
            "emotional_intensity": 0.8,
            "emotional_stability": 0.6
        }
        
        validated = emotion_service._validate_gemini_result(valid_result)
        
        assert validated["primary_emotion"] == "happiness"
        assert len(validated["emotion_scores"]) == 1
        assert 0.0 <= validated["sentiment_score"] <= 1.0
        
        # 잘못된 결과 (범위 초과)
        invalid_result = {
            "primary_emotion": "invalid_emotion",
            "sentiment_score": 2.0,  # 범위 초과
            "emotional_intensity": -0.5  # 범위 미달
        }
        
        validated_invalid = emotion_service._validate_gemini_result(invalid_result)
        
        assert validated_invalid["primary_emotion"] == "neutral"  # 기본값으로 변경
        assert -1.0 <= validated_invalid["sentiment_score"] <= 1.0
        assert 0.0 <= validated_invalid["emotional_intensity"] <= 1.0
    
    def test_integrate_emotion_results(
        self,
        emotion_service: EmotionAnalysisService,
        mock_gemini_response: dict
    ):
        """감정 분석 결과 통합 테스트"""
        textblob_result = {"polarity": 0.5, "subjectivity": 0.6}
        metadata_emotions = {"weather_boost": 0.1, "user_mood": 0.2}
        
        result = emotion_service._integrate_emotion_results(
            mock_gemini_response, textblob_result, metadata_emotions
        )
        
        assert isinstance(result, EmotionAnalysis)
        assert result.primary_emotion == "happiness"
        assert len(result.emotion_scores) > 0
        assert isinstance(result.emotion_scores[0], EmotionScore)
    
    def test_create_fallback_emotion_analysis(self, emotion_service: EmotionAnalysisService):
        """백업 감정 분석 결과 생성 테스트"""
        positive_content = "좋은 하루 행복한 기분"
        negative_content = "슬픔 화 우울 힘들다"
        neutral_content = "오늘은 그냥 평범한 하루"
        
        # 긍정적 내용
        result_positive = emotion_service._create_fallback_emotion_analysis(positive_content)
        assert result_positive.primary_emotion == "happiness"
        assert result_positive.sentiment_score > 0
        
        # 부정적 내용
        result_negative = emotion_service._create_fallback_emotion_analysis(negative_content)
        assert result_negative.primary_emotion == "sadness"
        assert result_negative.sentiment_score < 0
        
        # 중립적 내용
        result_neutral = emotion_service._create_fallback_emotion_analysis(neutral_content)
        assert result_neutral.primary_emotion == "neutral"
        assert result_neutral.sentiment_score == 0.0
    
    def test_classify_emotion_intensity(self, emotion_service: EmotionAnalysisService):
        """감정 강도 분류 테스트"""
        assert emotion_service.classify_emotion_intensity(0.9) == "매우 강함"
        assert emotion_service.classify_emotion_intensity(0.7) == "강함"
        assert emotion_service.classify_emotion_intensity(0.5) == "보통"
        assert emotion_service.classify_emotion_intensity(0.3) == "약함"
        assert emotion_service.classify_emotion_intensity(0.1) == "매우 약함"
    
    def test_get_emotion_recommendations(self, emotion_service: EmotionAnalysisService):
        """감정 상태 기반 추천사항 테스트"""
        # 부정적 감정 상태
        negative_emotion = EmotionAnalysis(
            primary_emotion="sadness",
            secondary_emotions=[],
            emotion_scores=[],
            sentiment_score=-0.7,
            emotional_intensity=0.8,
            emotional_stability=0.3
        )
        
        recommendations = emotion_service.get_emotion_recommendations(negative_emotion)
        
        assert len(recommendations) > 0
        assert any("부정적인 감정" in rec for rec in recommendations)
        
        # 긍정적 감정 상태
        positive_emotion = EmotionAnalysis(
            primary_emotion="happiness",
            secondary_emotions=[],
            emotion_scores=[],
            sentiment_score=0.8,
            emotional_intensity=0.6,
            emotional_stability=0.7
        )
        
        recommendations_positive = emotion_service.get_emotion_recommendations(positive_emotion)
        
        assert len(recommendations_positive) > 0
        assert any("긍정적인 감정" in rec for rec in recommendations_positive)
    
    @pytest.mark.asyncio
    async def test_get_user_emotion_patterns(self, emotion_service: EmotionAnalysisService):
        """사용자 감정 패턴 조회 테스트"""
        user_id = "test_user_123"
        
        result = await emotion_service.get_user_emotion_patterns(user_id)
        
        assert result["user_id"] == user_id
        assert "dominant_emotions" in result
        assert "emotion_trends" in result
        assert "weekly_patterns" in result
        assert "monthly_patterns" in result
    
    def test_emotion_categories_validation(self, emotion_service: EmotionAnalysisService):
        """감정 카테고리 검증 테스트"""
        # 정의된 감정 카테고리들이 모두 유효한지 확인
        for emotion in emotion_service.emotion_categories:
            assert isinstance(emotion, str)
            assert len(emotion) > 0
        
        # 중복 없는지 확인
        assert len(emotion_service.emotion_categories) == len(set(emotion_service.emotion_categories))
    
    @pytest.mark.asyncio
    async def test_analyze_emotions_empty_content(self, emotion_service: EmotionAnalysisService):
        """빈 내용 감정 분석 테스트"""
        result = await emotion_service.analyze_emotions("")
        
        # 빈 내용에 대해서도 기본 결과 반환
        assert isinstance(result, EmotionAnalysis)
        assert result.primary_emotion in ["neutral", "happiness", "sadness"]
    
    @pytest.mark.asyncio
    async def test_analyze_emotions_very_long_content(self, emotion_service: EmotionAnalysisService):
        """매우 긴 내용 감정 분석 테스트"""
        long_content = "이것은 매우 긴 텍스트입니다. " * 1000
        
        result = await emotion_service.analyze_emotions(long_content)
        
        # 긴 내용도 정상적으로 처리되어야 함
        assert isinstance(result, EmotionAnalysis)
        assert result.primary_emotion is not None
