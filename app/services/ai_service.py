"""
AI 분석 서비스
"""
import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import google.generativeai as genai
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.config.settings import get_settings
from app.core.exceptions import AIServiceException

# 모델 import를 지연 로딩으로 처리
try:
    from app.models.analysis import DiaryAnalysis, UserPersonalitySummary, UserEmotionPattern
    from app.models.user import User, UserVector
except ImportError as e:
    # 개발/테스트 환경에서 모델이 없을 수 있음
    logger = structlog.get_logger()
    logger.warning(f"Model import failed: {e}")
    DiaryAnalysis = None
    UserPersonalitySummary = None
    UserEmotionPattern = None
    User = None
    UserVector = None
from app.schemas.analysis import (
    DiaryAnalysisRequest,
    DiaryAnalysisResponse,
    EmotionAnalysis,
    PersonalityAnalysis,
    KeywordExtraction,
    LifestylePattern,
    UserInsightsResponse,
)
from app.services.emotion_service import EmotionAnalysisService
from app.services.personality_service import PersonalityAnalysisService
from app.utils.helpers import generate_analysis_id

settings = get_settings()
logger = structlog.get_logger()

# Gemini API 설정
genai.configure(api_key=settings.GEMINI_API_KEY)


def validate_and_fix_user_id(user_id: str) -> str:
    """user_id 검증 및 올바른 UUID로 변환/생성"""
    if not user_id:
        return str(uuid.uuid4())
    
    # 이미 올바른 UUID 형식인지 확인
    try:
        uuid.UUID(user_id)
        return user_id
    except ValueError:
        # UUID가 아니면 새로 생성
        logger.warning("invalid_user_id_converted", original=user_id)
        return str(uuid.uuid4())


async def ensure_user_exists(user_id: str, db: AsyncSession) -> str:
    """사용자가 존재하는지 확인하고 없으면 생성"""
    try:
        # 사용자 존재 확인
        from app.models.user import User
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.info("user_exists", user_id=user_id)
            return user_id
        
        # 사용자가 없으면 새로 생성
        new_user = User(
            id=user_id,
            firebase_uid=f"test_firebase_{user_id[:8]}",  # 테스트용 Firebase UID
            email=f"test_{user_id[:8]}@example.com",
            name=f"Test User {user_id[:8]}",
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        
        logger.info("user_created", user_id=user_id)
        return user_id
        
    except Exception as e:
        logger.error("ensure_user_exists_failed", user_id=user_id, error=str(e))
        # 에러 발생 시 롤백하고 기존 사용자 중 하나 사용
        await db.rollback()
        
        # 기존 사용자 중 아무나 하나 가져오기
        try:
            from app.models.user import User
            query = select(User).limit(1)
            result = await db.execute(query)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info("using_existing_user", user_id=str(existing_user.id))
                return str(existing_user.id)
            else:
                # 사용자가 아예 없으면 하나 생성
                fallback_user = User(
                    firebase_uid="test_fallback_user",
                    email="fallback@example.com",
                    name="Fallback User",
                    is_active=True
                )
                db.add(fallback_user)
                await db.commit()
                logger.info("fallback_user_created", user_id=str(fallback_user.id))
                return str(fallback_user.id)
                
        except Exception as e2:
            logger.error("fallback_user_creation_failed", error=str(e2))
            # 최후의 수단: 임의 UUID 반환 (Foreign Key 제약조건 무시)
            return str(uuid.uuid4())


class AIAnalysisService:
    """AI 분석 서비스 클래스"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.emotion_service = EmotionAnalysisService()
        self.personality_service = PersonalityAnalysisService()
    
    def _clean_json_response(self, response_text: str) -> str:
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
        
    async def analyze_diary(
        self, 
        request: DiaryAnalysisRequest,
        db: AsyncSession
    ) -> DiaryAnalysisResponse:
        """
        일기 텍스트 종합 AI 분석
        """
        start_time = time.time()
        analysis_id = generate_analysis_id()
        
        # user_id 검증 및 올바른 UUID로 변환
        valid_user_id = validate_and_fix_user_id(request.user_id)
        
        # 사용자가 존재하는지 확인하고 없으면 생성
        existing_user_id = await ensure_user_exists(valid_user_id, db)
        
        try:
            logger.info(
                "analysis_started",
                analysis_id=analysis_id,
                diary_id=request.diary_id,
                user_id=existing_user_id,  # 존재가 확인된 UUID 사용
                content_length=len(request.content)
            )
            
            # 1. 감정 분석
            emotion_analysis = await self.emotion_service.analyze_emotions(
                request.content, request.metadata
            )
            
            # 2. 성격 분석
            personality_analysis = await self.personality_service.analyze_personality(
                request.content, existing_user_id, db  # 존재가 확인된 UUID 사용
            )
            
            # 3. 키워드 및 주제 추출
            keyword_extraction = await self._extract_keywords_and_topics(request.content)
            
            # 4. 생활 패턴 분석
            lifestyle_patterns = await self._analyze_lifestyle_patterns(
                request.content, request.metadata
            )
            
            # 5. 인사이트 생성
            insights = await self._generate_insights(
                request.content,
                emotion_analysis,
                personality_analysis,
                keyword_extraction,
                lifestyle_patterns
            )
            
            # 6. 추천사항 생성
            recommendations = await self._generate_recommendations(
                emotion_analysis,
                personality_analysis,
                lifestyle_patterns
            )
            
            # 전체 신뢰도 계산
            confidence_score = self._calculate_overall_confidence(
                emotion_analysis,
                personality_analysis,
                len(request.content)
            )
            
            processing_time = time.time() - start_time
            
            # 7. 결과를 데이터베이스에 저장
            # 늤이나믹 import로 모델 로딩 문제 해결
            try:
                from app.models.analysis import DiaryAnalysis
            except ImportError:
                logger.error("DiaryAnalysis model not available")
                raise AIServiceException("모델 로딩 실패: DiaryAnalysis")
            
            analysis_result = DiaryAnalysis(
                analysis_id=analysis_id,
                diary_id=request.diary_id,
                user_id=valid_user_id,  # 검증된 UUID 사용
                content=request.content,
                content_length=len(request.content),
                emotions=emotion_analysis.dict(),
                primary_emotion=emotion_analysis.primary_emotion,
                secondary_emotions=emotion_analysis.secondary_emotions,
                sentiment_score=emotion_analysis.sentiment_score,
                emotional_intensity=emotion_analysis.emotional_intensity,
                emotional_stability=emotion_analysis.emotional_stability,
                personality=personality_analysis.dict(),
                mbti_indicators=personality_analysis.mbti_indicators.dict(),
                big5_traits=personality_analysis.big5_traits.dict(),
                predicted_mbti=personality_analysis.predicted_mbti,
                keywords=keyword_extraction.keywords,
                topics=keyword_extraction.topics,
                entities=keyword_extraction.entities,
                themes=keyword_extraction.themes,
                lifestyle_patterns=lifestyle_patterns.dict(),
                insights=insights,
                recommendations=recommendations,
                processing_time_seconds=processing_time,
                confidence_score=confidence_score,
                analysis_version="1.0",
                status="completed"
            )
            
            db.add(analysis_result)
            await db.commit()
            
            logger.info(
                "analysis_completed",
                analysis_id=analysis_id,
                processing_time=processing_time,
                confidence_score=confidence_score
            )
            
            return DiaryAnalysisResponse(
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
                analysis_version="1.0",
                processing_time=processing_time,
                confidence_score=confidence_score,
                processed_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(
                "analysis_failed",
                analysis_id=analysis_id,
                error=str(e),
                processing_time=time.time() - start_time
            )
            raise AIServiceException(f"분석 처리 중 오류 발생: {str(e)}")
    
    async def _extract_keywords_and_topics(self, content: str) -> KeywordExtraction:
        """키워드 및 주제 추출"""
        try:
            prompt = f"""
            다음 일기 텍스트를 분석하여 키워드, 주제, 개체명, 테마를 추출해주세요:

            텍스트: {content}

            다음 JSON 형식으로 응답해주세요 (마크다운 코드 블록 없이 순수 JSON만):
            {{
                "keywords": ["키워드1", "키워드2"],
                "topics": ["주제1", "주제2"],
                "entities": ["개체명1"],
                "themes": ["테마1", "테마2"]
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = self._clean_json_response(response.text)
            result = json.loads(response_text)
            
            return KeywordExtraction(
                keywords=result.get("keywords", []),
                topics=result.get("topics", []),
                entities=result.get("entities", []),
                themes=result.get("themes", [])
            )
            
        except Exception as e:
            logger.error("keyword_extraction_failed", error=str(e))
            # 기본값 반환
            return KeywordExtraction(
                keywords=["일기", "감정", "생각"],
                topics=["일상", "감정"],
                entities=[],
                themes=["개인적 성찰"]
            )
    
    async def _analyze_lifestyle_patterns(
        self, content: str, metadata: Optional[Dict]
    ) -> LifestylePattern:
        """생활 패턴 분석"""
        try:
            metadata_str = json.dumps(metadata or {}, ensure_ascii=False)
            
            prompt = f"""
            다음 일기 텍스트를 분석하여 생활 패턴을 추출해주세요:

            텍스트: {content}

            다음 JSON 형식으로 응답해주세요 (마크다운 코드 블록 없이 순수 JSON만):
            {{
                "activity_patterns": {{"운동": 0.8, "독서": 0.6}},
                "social_patterns": {{"친구만남": 0.7, "혼자시간": 0.8}},
                "time_patterns": {{"오전활동": 0.6, "오후활동": 0.8}},
                "interest_areas": ["예술", "운동"],
                "values_orientation": {{"건강": 0.8, "관계": 0.7}}
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = self._clean_json_response(response.text)
            result = json.loads(response_text)
            
            return LifestylePattern(
                activity_patterns=result.get("activity_patterns", {}),
                social_patterns=result.get("social_patterns", {}),
                time_patterns=result.get("time_patterns", {}),
                interest_areas=result.get("interest_areas", []),
                values_orientation=result.get("values_orientation", {})
            )
            
        except Exception as e:
            logger.error("lifestyle_analysis_failed", error=str(e))
            # 기본값 반환
            return LifestylePattern(
                activity_patterns={"독서": 0.7, "운동": 0.5},
                social_patterns={"친구만남": 0.6, "혼자시간": 0.8},
                time_patterns={"오전": 0.3, "오후": 0.8, "저녁": 0.6},
                interest_areas=["자기계발", "인간관계"],
                values_orientation={"성장": 0.8, "관계": 0.7}
            )
    
    async def _generate_insights(
        self,
        content: str,
        emotion_analysis: EmotionAnalysis,
        personality_analysis: PersonalityAnalysis,
        keyword_extraction: KeywordExtraction,
        lifestyle_patterns: LifestylePattern
    ) -> List[str]:
        """인사이트 생성"""
        try:
            prompt = f"""
            다음 일기 분석 결과를 바탕으로 의미 있는 인사이트를 3개 생성해주세요:

            주요 감정: {emotion_analysis.primary_emotion}
            감정 점수: {emotion_analysis.sentiment_score}
            예상 MBTI: {personality_analysis.predicted_mbti or '미상정'}
            키워드: {', '.join(keyword_extraction.keywords[:3])}

            다음 JSON 형식으로 응답해주세요 (마크다운 코드 블록 없이 순수 JSON만):
            ["인사이트1", "인사이트2", "인사이트3"]
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = self._clean_json_response(response.text)
            insights = json.loads(response_text)
            
            return insights if isinstance(insights, list) else []
            
        except Exception as e:
            logger.error("insight_generation_failed", error=str(e))
            # 기본값 반환
            return [
                f"{emotion_analysis.primary_emotion} 감정이 주로 나타나고 있습니다.",
                f"감정 안정성이 {emotion_analysis.emotional_stability:.1f} 수준입니다.",
                "일기를 통한 자기 성찰의 기회를 얻고 있습니다."
            ]
    
    async def _generate_recommendations(
        self,
        emotion_analysis: EmotionAnalysis,
        personality_analysis: PersonalityAnalysis,
        lifestyle_patterns: LifestylePattern
    ) -> List[str]:
        """추천사항 생성"""
        try:
            prompt = f"""
            다음 분석 결과를 바탕으로 개인 성장과 웰빙을 위한 추천사항을 3개 생성해주세요:

            주요 감정: {emotion_analysis.primary_emotion}
            감정 안정성: {emotion_analysis.emotional_stability}
            MBTI: {personality_analysis.predicted_mbti or '미상정'}
            관심 분야: {', '.join(lifestyle_patterns.interest_areas[:3])}

            다음 JSON 형식으로 응답해주세요 (마크다운 코드 블록 없이 순수 JSON만):
            ["추천사항1", "추천사항2", "추천사항3"]
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = self._clean_json_response(response.text)
            recommendations = json.loads(response_text)
            
            return recommendations if isinstance(recommendations, list) else []
            
        except Exception as e:
            logger.error("recommendation_generation_failed", error=str(e))
            # 기본값 반환
            return [
                "현재의 감정 상태를 잘 관찰하고 계시네요.",
                "일기를 통한 자기 성찰을 계속 이어가시길 권합니다.",
                "감정의 변화 패턴을 파악해보시는 것도 도움이 될 것 같습니다."
            ]
    
    def _calculate_overall_confidence(
        self,
        emotion_analysis: EmotionAnalysis,
        personality_analysis: PersonalityAnalysis,
        content_length: int
    ) -> float:
        """전체 신뢰도 계산"""
        try:
            # 콘텐츠 길이 기반 신뢰도 (최소 50자, 최적 500자)
            length_confidence = min(1.0, max(0.3, content_length / 500))
            
            # 각 분석의 신뢰도 (임시로 고정값 사용)
            emotion_confidence = 0.85  # 실제로는 모델의 confidence 사용
            personality_confidence = personality_analysis.confidence_level
            
            # 가중 평균
            overall_confidence = (
                length_confidence * 0.2 +
                emotion_confidence * 0.4 +
                personality_confidence * 0.4
            )
            
            return round(overall_confidence, 3)
            
        except Exception:
            return 0.7  # 기본값
    
    async def get_analysis_result(
        self, diary_id: str, user_id: str, db: AsyncSession
    ) -> Optional[DiaryAnalysisResponse]:
        """분석 결과 조회"""
        try:
            # 늤이나믹 import
            try:
                from app.models.analysis import DiaryAnalysis
            except ImportError:
                logger.error("DiaryAnalysis model not available")
                return None
                
            query = select(DiaryAnalysis).where(
                and_(
                    DiaryAnalysis.diary_id == diary_id,
                    DiaryAnalysis.user_id == user_id
                )
            )
            result = await db.execute(query)
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                return None
            
            # 응답 객체로 변환
            return DiaryAnalysisResponse(
                diary_id=analysis.diary_id,
                analysis_id=analysis.analysis_id,
                user_id=str(analysis.user_id),
                status=analysis.status,
                emotion_analysis=EmotionAnalysis(**analysis.emotions),
                personality_analysis=PersonalityAnalysis(**analysis.personality),
                keyword_extraction=KeywordExtraction(
                    keywords=analysis.keywords,
                    topics=analysis.topics,
                    entities=analysis.entities,
                    themes=analysis.themes
                ),
                lifestyle_patterns=LifestylePattern(**analysis.lifestyle_patterns),
                insights=analysis.insights,
                recommendations=analysis.recommendations,
                analysis_version=analysis.analysis_version,
                processing_time=analysis.processing_time_seconds,
                confidence_score=analysis.confidence_score,
                processed_at=analysis.processed_at
            )
            
        except Exception as e:
            logger.error("get_analysis_result_failed", error=str(e))
            return None
    
    async def update_user_vectors(
        self, user_id: str, analysis_result: DiaryAnalysisResponse, db: AsyncSession
    ):
        """사용자 벡터 업데이트 (백그라운드 작업)"""
        try:
            # 늤이나믹 import
            try:
                from app.models.user import UserVector
            except ImportError:
                logger.error("UserVector model not available")
                return
                
            # user_id 검증
            valid_user_id = validate_and_fix_user_id(user_id)
            
            # 기존 벡터 조회
            query = select(UserVector).where(UserVector.user_id == valid_user_id)
            result = await db.execute(query)
            user_vector = result.scalar_one_or_none()
            
            if not user_vector:
                # 새 벡터 생성
                user_vector = UserVector(user_id=valid_user_id)
                db.add(user_vector)
            
            # 벡터 업데이트 로직 (실제 구현 필요)
            # personality_vector = self._update_personality_vector(...)
            # emotion_vector = self._update_emotion_vector(...)
            # lifestyle_vector = self._update_lifestyle_vector(...)
            
            user_vector.analysis_count += 1
            user_vector.confidence_score = min(100, user_vector.confidence_score + 1)
            
            await db.commit()
            
            logger.info("user_vectors_updated", user_id=valid_user_id)
            
        except Exception as e:
            logger.error("update_user_vectors_failed", user_id=user_id, error=str(e))
    
    async def batch_analyze(
        self, diary_requests: List[DiaryAnalysisRequest], user_id: str, db: AsyncSession
    ):
        """일괄 분석 처리 (백그라운드 작업)"""
        try:
            logger.info("batch_analysis_started", user_id=user_id, count=len(diary_requests))
            
            for request in diary_requests:
                try:
                    await self.analyze_diary(request, db)
                    await asyncio.sleep(0.1)  # API rate limit 방지
                except Exception as e:
                    logger.error("batch_item_failed", diary_id=request.diary_id, error=str(e))
                    continue
            
            logger.info("batch_analysis_completed", user_id=user_id)
            
        except Exception as e:
            logger.error("batch_analysis_failed", user_id=user_id, error=str(e))
    
    async def get_user_insights(
        self, user_id: str, db: AsyncSession
    ) -> UserInsightsResponse:
        """사용자 종합 인사이트 조회"""
        # 구현 필요: 사용자의 모든 분석 결과를 종합하여 인사이트 생성
        pass
    
    async def get_analysis_history(
        self, user_id: str, limit: int, offset: int, db: AsyncSession
    ) -> List[Dict]:
        """분석 이력 조회"""
        # 구현 필요
        pass
    
    async def delete_analysis(
        self, diary_id: str, user_id: str, db: AsyncSession
    ) -> bool:
        """분석 결과 삭제"""
        # 구현 필요
        pass
    
    async def get_analysis_stats(
        self, user_id: str, db: AsyncSession
    ) -> Dict:
        """분석 통계 조회"""
        # 구현 필요
        pass
