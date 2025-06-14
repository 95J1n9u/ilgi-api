"""
감정 분석 서비스
"""
import json
import re
from typing import Dict, List, Optional, Any

import google.generativeai as genai
import structlog
from textblob import TextBlob

from app.config.settings import get_settings
from app.schemas.analysis import EmotionAnalysis, EmotionScore

settings = get_settings()
logger = structlog.get_logger()

# Gemini API 설정
genai.configure(api_key=settings.GEMINI_API_KEY)


class EmotionAnalysisService:
    """감정 분석 서비스 클래스"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 감정 카테고리 정의
        self.emotion_categories = [
            "joy", "happiness", "contentment", "excitement",
            "sadness", "melancholy", "grief", "disappointment",
            "anger", "frustration", "irritation", "rage",
            "fear", "anxiety", "worry", "nervousness",
            "surprise", "amazement", "shock", "wonder",
            "disgust", "distaste", "aversion",
            "love", "affection", "fondness", "passion",
            "hope", "optimism", "confidence", "determination",
            "guilt", "shame", "regret", "embarrassment",
            "pride", "satisfaction", "accomplishment",
            "loneliness", "isolation", "emptiness",
            "gratitude", "appreciation", "thankfulness",
            "curiosity", "interest", "fascination",
            "peace", "calm", "tranquility", "serenity"
        ]
    
    async def analyze_emotions(
        self, content: str, metadata: Optional[Dict] = None
    ) -> EmotionAnalysis:
        """
        텍스트의 감정을 종합 분석
        """
        try:
            # 1. Gemini API를 통한 상세 감정 분석
            gemini_analysis = await self._analyze_with_gemini(content)
            
            # 2. TextBlob을 통한 기본 감정 점수
            textblob_sentiment = self._analyze_with_textblob(content)
            
            # 3. 메타데이터 기반 감정 보정
            metadata_emotions = self._analyze_metadata_emotions(metadata or {})
            
            # 4. 결과 통합 및 정제
            integrated_result = self._integrate_emotion_results(
                gemini_analysis, textblob_sentiment, metadata_emotions
            )
            
            return integrated_result
            
        except Exception as e:
            logger.error("emotion_analysis_failed", error=str(e), content_length=len(content))
            # 실패 시 기본값 반환
            return self._create_fallback_emotion_analysis(content)
    
    async def _analyze_with_gemini(self, content: str) -> Dict[str, Any]:
        """Gemini API를 통한 감정 분석"""
        try:
            prompt = f"""
            다음 한국어 일기 텍스트의 감정을 정확하게 분석해주세요:

            텍스트: "{content}"

            다음 JSON 형식으로 정확히 응답해주세요:
            {{
                "primary_emotion": "주요감정",
                "secondary_emotions": ["보조감정1", "보조감정2"],
                "emotion_scores": [
                    {{"emotion": "감정명", "score": 0.85, "confidence": 0.9}},
                    {{"emotion": "감정명", "score": 0.65, "confidence": 0.8}}
                ],
                "sentiment_score": 0.7,
                "emotional_intensity": 0.8,
                "emotional_stability": 0.6,
                "emotion_explanation": "감정 분석에 대한 간단한 설명"
            }}

            감정 분석 기준:
            1. primary_emotion: 가장 강하게 나타나는 주요 감정 (한 개)
            2. secondary_emotions: 부차적으로 나타나는 감정들 (2-3개)
            3. emotion_scores: 각 감정별 강도 점수 (0.0-1.0)
            4. sentiment_score: 전체적인 감정 극성 (-1.0: 매우 부정, 0: 중립, 1.0: 매우 긍정)
            5. emotional_intensity: 감정의 강도 (0.0: 약함, 1.0: 매우 강함)
            6. emotional_stability: 감정의 안정성 (0.0: 불안정, 1.0: 매우 안정)

            감정 목록: {', '.join(self.emotion_categories[:20])}
            """
            
            response = await self.model.generate_content_async(prompt)
            
            # JSON 응답 파싱
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            result = json.loads(response_text)
            
            # 결과 검증 및 정제
            return self._validate_gemini_result(result)
            
        except Exception as e:
            logger.error("gemini_emotion_analysis_failed", error=str(e))
            raise
    
    def _analyze_with_textblob(self, content: str) -> Dict[str, float]:
        """TextBlob을 통한 기본 감정 분석"""
        try:
            blob = TextBlob(content)
            
            return {
                "polarity": blob.sentiment.polarity,  # -1 ~ 1
                "subjectivity": blob.sentiment.subjectivity  # 0 ~ 1
            }
            
        except Exception as e:
            logger.error("textblob_analysis_failed", error=str(e))
            return {"polarity": 0.0, "subjectivity": 0.5}
    
    def _analyze_metadata_emotions(self, metadata: Dict) -> Dict[str, float]:
        """메타데이터 기반 감정 추정"""
        emotion_modifiers = {}
        
        try:
            # 날씨 기반 감정 보정
            weather = metadata.get("weather", "").lower()
            if weather in ["sunny", "clear", "맑음"]:
                emotion_modifiers["weather_boost"] = 0.1
            elif weather in ["rainy", "cloudy", "비", "흐림"]:
                emotion_modifiers["weather_boost"] = -0.1
            
            # 사용자가 설정한 기분
            user_mood = metadata.get("mood", "").lower()
            mood_mapping = {
                "happy": 0.8, "sad": -0.6, "angry": -0.7,
                "excited": 0.7, "tired": -0.3, "calm": 0.3,
                "기쁨": 0.8, "슬픔": -0.6, "화남": -0.7,
                "신남": 0.7, "피곤": -0.3, "평온": 0.3
            }
            if user_mood and user_mood in mood_mapping:
                emotion_modifiers["user_mood"] = mood_mapping[user_mood]
            
            # 활동 기반 감정 추정
            activities = metadata.get("activities", [])
            positive_activities = ["friends", "exercise", "hobby", "travel"]
            negative_activities = ["work", "stress", "conflict"]
            
            activity_score = 0
            for activity in activities:
                if activity.lower() in positive_activities:
                    activity_score += 0.1
                elif activity.lower() in negative_activities:
                    activity_score -= 0.1
            
            if activity_score != 0:
                emotion_modifiers["activities"] = activity_score
            
            return emotion_modifiers
            
        except Exception as e:
            logger.error("metadata_emotion_analysis_failed", error=str(e))
            return {}
    
    def _integrate_emotion_results(
        self,
        gemini_result: Dict,
        textblob_result: Dict,
        metadata_emotions: Dict
    ) -> EmotionAnalysis:
        """감정 분석 결과 통합"""
        try:
            # 기본값 설정
            primary_emotion = gemini_result.get("primary_emotion", "neutral")
            secondary_emotions = gemini_result.get("secondary_emotions", [])
            
            # 감정 점수 통합
            emotion_scores = []
            for emotion_data in gemini_result.get("emotion_scores", []):
                emotion_scores.append(EmotionScore(
                    emotion=emotion_data["emotion"],
                    score=emotion_data["score"],
                    confidence=emotion_data["confidence"]
                ))
            
            # 감정 점수 보정 (TextBlob + 메타데이터)
            base_sentiment = gemini_result.get("sentiment_score", 0.0)
            textblob_sentiment = textblob_result.get("polarity", 0.0)
            
            # 가중 평균으로 sentiment_score 계산
            sentiment_score = (base_sentiment * 0.7 + textblob_sentiment * 0.3)
            
            # 메타데이터 기반 보정
            for modifier_type, modifier_value in metadata_emotions.items():
                sentiment_score += modifier_value * 0.1
            
            # 범위 제한
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            # 감정 강도 및 안정성
            emotional_intensity = gemini_result.get("emotional_intensity", 0.5)
            emotional_stability = gemini_result.get("emotional_stability", 0.5)
            
            return EmotionAnalysis(
                primary_emotion=primary_emotion,
                secondary_emotions=secondary_emotions,
                emotion_scores=emotion_scores,
                sentiment_score=round(sentiment_score, 3),
                emotional_intensity=round(emotional_intensity, 3),
                emotional_stability=round(emotional_stability, 3)
            )
            
        except Exception as e:
            logger.error("emotion_integration_failed", error=str(e))
            # 실패 시 기본값 반환
            return EmotionAnalysis(
                primary_emotion="neutral",
                secondary_emotions=[],
                emotion_scores=[],
                sentiment_score=0.0,
                emotional_intensity=0.5,
                emotional_stability=0.5
            )
    
    def _validate_gemini_result(self, result: Dict) -> Dict:
        """Gemini 결과 검증 및 정제"""
        validated = {}
        
        # primary_emotion 검증
        primary = result.get("primary_emotion", "neutral")
        validated["primary_emotion"] = primary if primary in self.emotion_categories else "neutral"
        
        # secondary_emotions 검증
        secondary = result.get("secondary_emotions", [])
        validated["secondary_emotions"] = [
            emotion for emotion in secondary 
            if emotion in self.emotion_categories
        ][:3]  # 최대 3개
        
        # emotion_scores 검증
        emotion_scores = result.get("emotion_scores", [])
        validated_scores = []
        for score_data in emotion_scores:
            if isinstance(score_data, dict):
                emotion = score_data.get("emotion", "")
                score = float(score_data.get("score", 0))
                confidence = float(score_data.get("confidence", 0))
                
                if emotion in self.emotion_categories:
                    validated_scores.append({
                        "emotion": emotion,
                        "score": max(0.0, min(1.0, score)),
                        "confidence": max(0.0, min(1.0, confidence))
                    })
        
        validated["emotion_scores"] = validated_scores
        
        # 수치 값들 검증
        validated["sentiment_score"] = max(-1.0, min(1.0, 
            float(result.get("sentiment_score", 0))))
        validated["emotional_intensity"] = max(0.0, min(1.0, 
            float(result.get("emotional_intensity", 0.5))))
        validated["emotional_stability"] = max(0.0, min(1.0, 
            float(result.get("emotional_stability", 0.5))))
        
        return validated
    
    def _create_fallback_emotion_analysis(self, content: str) -> EmotionAnalysis:
        """실패 시 기본 감정 분석 결과 생성"""
        try:
            # 간단한 키워드 기반 감정 추정
            positive_words = ["좋", "행복", "기쁨", "즐거", "만족", "감사"]
            negative_words = ["슬픔", "화", "짜증", "우울", "힘들", "스트레스"]
            
            positive_count = sum(1 for word in positive_words if word in content)
            negative_count = sum(1 for word in negative_words if word in content)
            
            if positive_count > negative_count:
                primary_emotion = "happiness"
                sentiment_score = 0.6
            elif negative_count > positive_count:
                primary_emotion = "sadness"
                sentiment_score = -0.4
            else:
                primary_emotion = "neutral"
                sentiment_score = 0.0
            
            return EmotionAnalysis(
                primary_emotion=primary_emotion,
                secondary_emotions=[],
                emotion_scores=[
                    EmotionScore(
                        emotion=primary_emotion,
                        score=0.7,
                        confidence=0.5
                    )
                ],
                sentiment_score=sentiment_score,
                emotional_intensity=0.5,
                emotional_stability=0.5
            )
            
        except Exception:
            # 최종 기본값
            return EmotionAnalysis(
                primary_emotion="neutral",
                secondary_emotions=[],
                emotion_scores=[],
                sentiment_score=0.0,
                emotional_intensity=0.5,
                emotional_stability=0.5
            )
    
    async def get_user_emotion_patterns(self, user_id: str) -> Dict:
        """사용자 감정 패턴 분석"""
        # TODO: 데이터베이스에서 사용자의 모든 감정 분석 결과를 조회하여
        # 감정 패턴, 변화 추이, 통계 등을 생성
        return {
            "user_id": user_id,
            "dominant_emotions": [],
            "emotion_trends": {},
            "weekly_patterns": {},
            "monthly_patterns": {}
        }
    
    def classify_emotion_intensity(self, intensity: float) -> str:
        """감정 강도 분류"""
        if intensity >= 0.8:
            return "매우 강함"
        elif intensity >= 0.6:
            return "강함"
        elif intensity >= 0.4:
            return "보통"
        elif intensity >= 0.2:
            return "약함"
        else:
            return "매우 약함"
    
    def get_emotion_recommendations(self, emotion_analysis: EmotionAnalysis) -> List[str]:
        """감정 상태 기반 추천사항"""
        recommendations = []
        
        primary_emotion = emotion_analysis.primary_emotion
        sentiment_score = emotion_analysis.sentiment_score
        intensity = emotion_analysis.emotional_intensity
        
        if sentiment_score < -0.5:
            recommendations.append("부정적인 감정을 느끼고 계시네요. 깊은 호흡이나 명상을 시도해보세요.")
            if intensity > 0.7:
                recommendations.append("감정이 매우 강하니 신뢰할 수 있는 사람과 대화해보시는 것도 좋겠어요.")
        
        elif sentiment_score > 0.5:
            recommendations.append("긍정적인 감정 상태를 유지하고 계시네요! 이 순간을 충분히 즐기세요.")
            
        if emotion_analysis.emotional_stability < 0.4:
            recommendations.append("감정 변화가 큰 것 같아요. 규칙적인 생활 패턴을 유지해보세요.")
        
        return recommendations
