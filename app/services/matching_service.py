"""
매칭 서비스
"""
import math
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, not_

# 모델 import를 지연 로딩으로 처리 (동적 import)
from app.schemas.matching import (
    MatchingCandidate,
    CompatibilityResponse,
    CompatibilityBreakdown,
    MatchingProfile,
    MatchingAnalytics,
    MatchingFilters
)

logger = structlog.get_logger()


class MatchingService:
    """매칭 서비스 클래스"""
    
    def __init__(self):
        # 호환성 계산 가중치
        self.default_weights = {
            "personality": 0.35,
            "emotion": 0.25,
            "lifestyle": 0.25,
            "interest": 0.15
        }
        
        # MBTI 호환성 매트릭스 (간단화된 버전)
        self.mbti_compatibility_matrix = {
            "ENFJ": ["INFP", "ENFP", "INFJ", "INTJ"],
            "ENFP": ["INFJ", "INTJ", "ENFJ", "ENTP"],
            "ENTJ": ["INTP", "INTJ", "ENFP", "ENTP"],
            "ENTP": ["INFJ", "INTJ", "ENFP", "ENTJ"],
            "ESFJ": ["ISFP", "ESFP", "ISTJ", "ESTJ"],
            "ESFP": ["ISFJ", "ISTJ", "ESFJ", "ESTP"],
            "ESTJ": ["ISFJ", "ISTJ", "ESFJ", "ISTP"],
            "ESTP": ["ISFJ", "ISTJ", "ESFP", "ESTJ"],
            "INFJ": ["ENFP", "ENTP", "INFP", "ENFJ"],
            "INFP": ["ENFJ", "ENTJ", "INFJ", "ENFP"],
            "INTJ": ["ENFP", "ENTP", "ENTJ", "INFP"],
            "INTP": ["ENTJ", "ESTJ", "INTJ", "ENTP"],
            "ISFJ": ["ESFP", "ESTP", "ISFP", "ESFJ"],
            "ISFP": ["ENFJ", "ESFJ", "ISFJ", "ESFP"],
            "ISTJ": ["ESFP", "ESTP", "ESTJ", "ISFJ"],
            "ISTP": ["ESFJ", "ESTJ", "ESTP", "ISFP"]
        }
    
    async def find_matching_candidates(
        self,
        user_id: str,
        db: AsyncSession,
        limit: int = 10,
        min_compatibility: float = 0.5,
        filters: Optional[MatchingFilters] = None,
    ) -> List[MatchingCandidate]:
        """
        매칭 후보 검색
        """
        try:
            logger.info("finding_matching_candidates", user_id=user_id, limit=limit)
            
            # 1. 사용자 정보 및 벡터 조회
            user_data = await self._get_user_matching_data(user_id, db)
            if not user_data:
                logger.warning("user_data_not_found", user_id=user_id)
                return []
            
            # 2. 후보자 목록 조회 (필터링 적용)
            candidates = await self._get_candidate_users(user_id, filters, db)
            
            # 3. 각 후보자와의 호환성 계산
            compatibility_scores = []
            for candidate in candidates:
                candidate_data = await self._get_user_matching_data(candidate.id, db)
                if not candidate_data:
                    continue
                
                compatibility = await self._calculate_compatibility_score(
                    user_data, candidate_data
                )
                
                if compatibility >= min_compatibility:
                    compatibility_scores.append({
                        "user": candidate,
                        "user_data": candidate_data,
                        "compatibility": compatibility
                    })
            
            # 4. 호환성 점수로 정렬
            compatibility_scores.sort(key=lambda x: x["compatibility"], reverse=True)
            
            # 5. 매칭 후보 객체 생성
            matching_candidates = []
            for i, item in enumerate(compatibility_scores[:limit]):
                candidate = await self._create_matching_candidate(
                    item["user"], 
                    item["user_data"], 
                    item["compatibility"],
                    i + 1,
                    user_data
                )
                matching_candidates.append(candidate)
            
            logger.info(
                "matching_candidates_found",
                user_id=user_id,
                count=len(matching_candidates)
            )
            
            return matching_candidates
            
        except Exception as e:
            logger.error("find_matching_candidates_failed", user_id=user_id, error=str(e))
            return []
    
    async def calculate_compatibility(
        self, user_id_1: str, user_id_2: str, db: AsyncSession
    ) -> CompatibilityResponse:
        """
        두 사용자 간 호환성 점수 계산
        """
        try:
            # 1. 두 사용자 데이터 조회
            user1_data = await self._get_user_matching_data(user_id_1, db)
            user2_data = await self._get_user_matching_data(user_id_2, db)
            
            if not user1_data or not user2_data:
                raise ValueError("사용자 데이터를 찾을 수 없습니다")
            
            # 2. 호환성 점수 계산
            overall_compatibility = await self._calculate_compatibility_score(
                user1_data, user2_data
            )
            
            # 3. 세부 호환성 분석
            breakdown = await self._calculate_compatibility_breakdown(
                user1_data, user2_data
            )
            
            # 4. 호환성 수준 결정
            compatibility_level = self._determine_compatibility_level(overall_compatibility)
            
            # 5. 관계 강점 및 주의사항 분석
            strengths, challenges = await self._analyze_relationship_dynamics(
                user1_data, user2_data, breakdown
            )
            
            # 6. 추천사항 생성
            recommendations = await self._generate_relationship_recommendations(
                breakdown, strengths, challenges
            )
            
            # 7. 신뢰도 계산
            confidence_level = self._calculate_compatibility_confidence(
                user1_data, user2_data
            )
            
            return CompatibilityResponse(
                user_id_1=user_id_1,
                user_id_2=user_id_2,
                overall_compatibility=round(overall_compatibility, 3),
                compatibility_level=compatibility_level,
                breakdown=breakdown,
                strengths=strengths,
                potential_challenges=challenges,
                recommendations=recommendations,
                calculated_at=datetime.utcnow(),
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error("calculate_compatibility_failed", error=str(e))
            raise
    
    async def _get_user_matching_data(self, user_id: str, db: AsyncSession) -> Optional[Dict]:
        """사용자 매칭 데이터 조회"""
        try:
            # 늤이나믹 import
            try:
                from app.models.user import User, UserVector, MatchingPreference
                from app.models.analysis import UserPersonalitySummary, UserEmotionPattern
            except ImportError as e:
                logger.error(f"Model import failed: {e}")
                return None
                
            # 기본 사용자 정보
            user_query = select(User).where(User.id == user_id)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                return None
            
            # 사용자 벡터
            vector_query = select(UserVector).where(UserVector.user_id == user_id)
            vector_result = await db.execute(vector_query)
            user_vector = vector_result.scalar_one_or_none()
            
            # 성격 요약
            personality_query = select(UserPersonalitySummary).where(
                UserPersonalitySummary.user_id == user_id
            )
            personality_result = await db.execute(personality_query)
            personality_summary = personality_result.scalar_one_or_none()
            
            # 감정 패턴
            emotion_query = select(UserEmotionPattern).where(
                UserEmotionPattern.user_id == user_id
            )
            emotion_result = await db.execute(emotion_query)
            emotion_pattern = emotion_result.scalar_one_or_none()
            
            # 매칭 선호도
            preference_query = select(MatchingPreference).where(
                MatchingPreference.user_id == user_id
            )
            preference_result = await db.execute(preference_query)
            matching_preference = preference_result.scalar_one_or_none()
            
            return {
                "user": user,
                "vector": user_vector,
                "personality": personality_summary,
                "emotion": emotion_pattern,
                "preference": matching_preference
            }
            
        except Exception as e:
            logger.error("get_user_matching_data_failed", user_id=user_id, error=str(e))
            return None
    
    async def _get_candidate_users(
        self, user_id: str, filters: Optional[MatchingFilters], db: AsyncSession
    ) -> List:
        """후보자 목록 조회"""
        try:
            # 늤이나믹 import
            try:
                from app.models.user import User
            except ImportError:
                logger.error("User model not available")
                return []
                
            query = select(User).where(
                and_(
                    User.id != user_id,  # 본인 제외
                    User.is_active == True,
                    User.matching_enabled == True
                )
            )
            
            # 필터 적용
            if filters:
                if filters.age_range:
                    min_age, max_age = filters.age_range
                    query = query.where(
                        and_(
                            User.age >= min_age,
                            User.age <= max_age
                        )
                    )
                
                if filters.location:
                    query = query.where(User.location.ilike(f"%{filters.location}%"))
                
                if filters.exclude_users:
                    query = query.where(not_(User.id.in_(filters.exclude_users)))
            
            # 최근 활동 우선
            query = query.order_by(User.last_active.desc()).limit(100)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("get_candidate_users_failed", error=str(e))
            return []
    
    async def _calculate_compatibility_score(
        self, user1_data: Dict, user2_data: Dict
    ) -> float:
        """전체 호환성 점수 계산"""
        try:
            # 가중치 설정 (사용자 선호도가 있으면 적용)
            weights = self.default_weights.copy()
            if user1_data["preference"]:
                pref = user1_data["preference"]
                weights = {
                    "personality": pref.personality_weight / 100,
                    "emotion": pref.emotion_weight / 100,
                    "lifestyle": pref.lifestyle_weight / 100,
                    "interest": pref.interest_weight / 100
                }
            
            # 각 영역별 호환성 계산
            personality_compatibility = self._calculate_personality_compatibility(
                user1_data, user2_data
            )
            
            emotion_compatibility = self._calculate_emotion_compatibility(
                user1_data, user2_data
            )
            
            lifestyle_compatibility = self._calculate_lifestyle_compatibility(
                user1_data, user2_data
            )
            
            interest_compatibility = self._calculate_interest_compatibility(
                user1_data, user2_data
            )
            
            # 가중 평균 계산
            overall_compatibility = (
                personality_compatibility * weights["personality"] +
                emotion_compatibility * weights["emotion"] +
                lifestyle_compatibility * weights["lifestyle"] +
                interest_compatibility * weights["interest"]
            )
            
            return max(0.0, min(1.0, overall_compatibility))
            
        except Exception as e:
            logger.error("calculate_compatibility_score_failed", error=str(e))
            return 0.5
    
    def _calculate_personality_compatibility(
        self, user1_data: Dict, user2_data: Dict
    ) -> float:
        """성격 호환성 계산"""
        try:
            personality1 = user1_data["personality"]
            personality2 = user2_data["personality"]
            
            if not personality1 or not personality2:
                return 0.5
            
            # MBTI 호환성
            mbti_compatibility = 0.5
            if personality1.overall_mbti and personality2.overall_mbti:
                mbti1 = personality1.overall_mbti
                mbti2 = personality2.overall_mbti
                
                # 호환성 매트릭스 확인
                if mbti1 in self.mbti_compatibility_matrix:
                    compatible_types = self.mbti_compatibility_matrix[mbti1]
                    if mbti2 in compatible_types:
                        mbti_compatibility = 0.9 - (compatible_types.index(mbti2) * 0.1)
                    else:
                        # 각 차원별 유사성 계산
                        similarity = sum(
                            1 for i in range(4) 
                            if mbti1[i] == mbti2[i]
                        ) / 4
                        mbti_compatibility = 0.3 + similarity * 0.4
            
            # Big5 호환성 (유사성 기반)
            big5_compatibility = 0.5
            if personality1.overall_big5 and personality2.overall_big5:
                big5_1 = personality1.overall_big5
                big5_2 = personality2.overall_big5
                
                similarities = []
                for trait in ["openness", "conscientiousness", "extraversion", 
                             "agreeableness", "neuroticism"]:
                    if trait in big5_1 and trait in big5_2:
                        diff = abs(big5_1[trait] - big5_2[trait])
                        similarity = 1 - diff
                        similarities.append(similarity)
                
                if similarities:
                    big5_compatibility = sum(similarities) / len(similarities)
            
            # MBTI와 Big5 가중 평균
            return (mbti_compatibility * 0.6 + big5_compatibility * 0.4)
            
        except Exception as e:
            logger.error("calculate_personality_compatibility_failed", error=str(e))
            return 0.5
    
    def _calculate_emotion_compatibility(
        self, user1_data: Dict, user2_data: Dict
    ) -> float:
        """감정 호환성 계산"""
        try:
            emotion1 = user1_data["emotion"]
            emotion2 = user2_data["emotion"]
            
            if not emotion1 or not emotion2:
                return 0.5
            
            compatibility_factors = []
            
            # 감정 안정성 호환성
            if emotion1.emotional_volatility is not None and emotion2.emotional_volatility is not None:
                # 너무 차이가 나지 않는 것이 좋음
                volatility_diff = abs(emotion1.emotional_volatility - emotion2.emotional_volatility)
                volatility_compatibility = max(0, 1 - volatility_diff)
                compatibility_factors.append(volatility_compatibility)
            
            # 평균 감정 점수 호환성
            if emotion1.avg_sentiment_score is not None and emotion2.avg_sentiment_score is not None:
                # 비슷한 감정 경향을 가진 것이 좋음
                sentiment_diff = abs(emotion1.avg_sentiment_score - emotion2.avg_sentiment_score)
                sentiment_compatibility = max(0, 1 - sentiment_diff / 2)  # -1~1 범위이므로 /2
                compatibility_factors.append(sentiment_compatibility)
            
            # 감정 다양성 (상호 보완적)
            if emotion1.emotion_distribution and emotion2.emotion_distribution:
                # 감정 분포의 다양성이 상호 보완적인지 확인
                distribution_compatibility = self._calculate_emotion_distribution_compatibility(
                    emotion1.emotion_distribution, emotion2.emotion_distribution
                )
                compatibility_factors.append(distribution_compatibility)
            
            return sum(compatibility_factors) / len(compatibility_factors) if compatibility_factors else 0.5
            
        except Exception as e:
            logger.error("calculate_emotion_compatibility_failed", error=str(e))
            return 0.5
    
    def _calculate_lifestyle_compatibility(
        self, user1_data: Dict, user2_data: Dict
    ) -> float:
        """생활 패턴 호환성 계산"""
        try:
            vector1 = user1_data["vector"]
            vector2 = user2_data["vector"]
            
            if not vector1 or not vector2 or not vector1.lifestyle_vector or not vector2.lifestyle_vector:
                return 0.5
            
            # 벡터 간 코사인 유사도 계산
            lifestyle_similarity = self._calculate_cosine_similarity(
                vector1.lifestyle_vector, vector2.lifestyle_vector
            )
            
            return max(0.0, min(1.0, lifestyle_similarity))
            
        except Exception as e:
            logger.error("calculate_lifestyle_compatibility_failed", error=str(e))
            return 0.5
    
    def _calculate_interest_compatibility(
        self, user1_data: Dict, user2_data: Dict
    ) -> float:
        """관심사 호환성 계산"""
        try:
            user1 = user1_data["user"]
            user2 = user2_data["user"]
            
            # 사용자 설정에서 관심사 추출 (임시로 빈 리스트 사용)
            interests1 = user1.settings.get("interests", []) if user1.settings else []
            interests2 = user2.settings.get("interests", []) if user2.settings else []
            
            if not interests1 or not interests2:
                return 0.5
            
            # 공통 관심사 비율 계산
            common_interests = set(interests1) & set(interests2)
            total_interests = set(interests1) | set(interests2)
            
            if total_interests:
                jaccard_similarity = len(common_interests) / len(total_interests)
                return jaccard_similarity
            else:
                return 0.5
                
        except Exception as e:
            logger.error("calculate_interest_compatibility_failed", error=str(e))
            return 0.5
    
    def _calculate_cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """코사인 유사도 계산"""
        try:
            if not vector1 or not vector2 or len(vector1) != len(vector2):
                return 0.5
            
            dot_product = sum(a * b for a, b in zip(vector1, vector2))
            norm1 = math.sqrt(sum(a * a for a in vector1))
            norm2 = math.sqrt(sum(b * b for b in vector2))
            
            if norm1 == 0 or norm2 == 0:
                return 0.5
            
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.5
    
    def _calculate_emotion_distribution_compatibility(
        self, dist1: Dict, dist2: Dict
    ) -> float:
        """감정 분포 호환성 계산"""
        try:
            # 상호 보완적인 감정 분포인지 확인
            # 예: 한 사람이 불안하면 다른 사람이 안정적인 것이 좋음
            
            complementary_pairs = [
                ("anxiety", "calm"),
                ("sadness", "joy"),
                ("anger", "peace"),
                ("stress", "relaxation")
            ]
            
            compatibility_score = 0.5  # 기본값
            pair_scores = []
            
            for emotion1, emotion2 in complementary_pairs:
                score1_1 = dist1.get(emotion1, 0)
                score1_2 = dist1.get(emotion2, 0)
                score2_1 = dist2.get(emotion1, 0)
                score2_2 = dist2.get(emotion2, 0)
                
                # 상호 보완성 계산
                complementarity = abs((score1_1 - score1_2) + (score2_2 - score2_1)) / 2
                pair_scores.append(complementarity)
            
            if pair_scores:
                compatibility_score = sum(pair_scores) / len(pair_scores)
            
            return max(0.0, min(1.0, compatibility_score))
            
        except Exception:
            return 0.5
    
    async def _calculate_compatibility_breakdown(
        self, user1_data: Dict, user2_data: Dict
    ) -> CompatibilityBreakdown:
        """세부 호환성 분석"""
        personality_compatibility = self._calculate_personality_compatibility(
            user1_data, user2_data
        )
        emotion_compatibility = self._calculate_emotion_compatibility(
            user1_data, user2_data
        )
        lifestyle_compatibility = self._calculate_lifestyle_compatibility(
            user1_data, user2_data
        )
        interest_compatibility = self._calculate_interest_compatibility(
            user1_data, user2_data
        )
        
        # 소통 스타일 호환성 (성격 기반으로 추정)
        communication_compatibility = (
            personality_compatibility * 0.7 + emotion_compatibility * 0.3
        )
        
        return CompatibilityBreakdown(
            personality_compatibility=round(personality_compatibility, 3),
            emotion_compatibility=round(emotion_compatibility, 3),
            lifestyle_compatibility=round(lifestyle_compatibility, 3),
            interest_compatibility=round(interest_compatibility, 3),
            communication_compatibility=round(communication_compatibility, 3)
        )
    
    def _determine_compatibility_level(self, score: float) -> str:
        """호환성 수준 결정"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.65:
            return "good"
        elif score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    async def _analyze_relationship_dynamics(
        self, user1_data: Dict, user2_data: Dict, breakdown: CompatibilityBreakdown
    ) -> Tuple[List[str], List[str]]:
        """관계 역학 분석"""
        strengths = []
        challenges = []
        
        # 성격 기반 분석
        if breakdown.personality_compatibility > 0.7:
            strengths.append("성격적으로 잘 맞는 조합으로 서로를 이해하기 쉬울 것")
        elif breakdown.personality_compatibility < 0.4:
            challenges.append("성격 차이로 인한 갈등 가능성이 있어 상호 이해 노력 필요")
        
        # 감정 기반 분석
        if breakdown.emotion_compatibility > 0.7:
            strengths.append("감정적으로 안정된 관계를 유지할 수 있을 것")
        elif breakdown.emotion_compatibility < 0.4:
            challenges.append("감정적 차이로 인한 오해 발생 가능성")
        
        # 생활 패턴 분석
        if breakdown.lifestyle_compatibility > 0.7:
            strengths.append("생활 패턴이 비슷하여 함께 시간을 보내기 편할 것")
        elif breakdown.lifestyle_compatibility < 0.4:
            challenges.append("생활 방식의 차이로 인한 조율 필요")
        
        # 관심사 분석
        if breakdown.interest_compatibility > 0.6:
            strengths.append("공통 관심사가 많아 대화 주제가 풍부할 것")
        elif breakdown.interest_compatibility < 0.3:
            challenges.append("관심사 차이로 인해 서로의 취미를 이해하려는 노력 필요")
        
        return strengths, challenges
    
    async def _generate_relationship_recommendations(
        self, breakdown: CompatibilityBreakdown, strengths: List[str], challenges: List[str]
    ) -> List[str]:
        """관계 개선 추천사항 생성"""
        recommendations = []
        
        if breakdown.communication_compatibility < 0.6:
            recommendations.append("서로의 소통 스타일을 이해하고 존중하는 대화 방식 개발")
        
        if breakdown.emotion_compatibility < 0.5:
            recommendations.append("감정 표현과 공감 능력을 기르는 노력")
        
        if breakdown.lifestyle_compatibility < 0.5:
            recommendations.append("생활 패턴의 차이를 인정하고 서로 맞춰가는 유연성")
        
        if breakdown.interest_compatibility < 0.4:
            recommendations.append("서로의 관심사에 대해 배우고 새로운 공통분모 찾기")
        
        # 기본 추천사항
        if not recommendations:
            recommendations.append("서로의 장점을 인정하고 꾸준한 소통으로 관계 발전시키기")
        
        return recommendations
    
    def _calculate_compatibility_confidence(
        self, user1_data: Dict, user2_data: Dict
    ) -> float:
        """호환성 분석 신뢰도 계산"""
        try:
            confidence_factors = []
            
            # 데이터 완성도
            if user1_data["personality"] and user2_data["personality"]:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.3)
            
            if user1_data["vector"] and user2_data["vector"]:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.4)
            
            if user1_data["emotion"] and user2_data["emotion"]:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.4)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception:
            return 0.5
    
    async def _create_matching_candidate(
        self,
        candidate_user,  # User 타입 힌트 제거 (동적 import로 인해)
        candidate_data: Dict,
        compatibility_score: float,
        rank: int,
        requester_data: Dict
    ) -> MatchingCandidate:
        """매칭 후보 객체 생성"""
        try:
            # 기본 정보 (익명화)
            age_range = f"{candidate_user.age//10*10}대" if candidate_user.age else None
            location = candidate_user.location.split()[0] if candidate_user.location else None
            
            # 성격 정보
            personality_type = None
            personality_traits = []
            if candidate_data["personality"]:
                personality_type = candidate_data["personality"].overall_mbti
                personality_traits = candidate_data["personality"].personality_traits or []
            
            # 호환성 수준
            compatibility_level = self._determine_compatibility_level(compatibility_score)
            
            # 매칭 근거 생성
            match_reasons = await self._generate_match_reasons(
                requester_data, candidate_data, compatibility_score
            )
            
            # 공통점과 상호 보완적 특성
            common_traits, complementary_traits = await self._analyze_trait_compatibility(
                requester_data, candidate_data
            )
            
            return MatchingCandidate(
                user_id=str(candidate_user.id),
                compatibility_score=round(compatibility_score, 3),
                compatibility_level=compatibility_level,
                age_range=age_range,
                location=location,
                interests=[],  # TODO: 관심사 추출
                personality_type=personality_type,
                personality_traits=personality_traits[:3],
                match_reasons=match_reasons,
                common_traits=common_traits,
                complementary_traits=complementary_traits,
                last_active=candidate_user.last_active,
                match_rank=rank
            )
            
        except Exception as e:
            logger.error("create_matching_candidate_failed", error=str(e))
            # 기본 객체 반환
            return MatchingCandidate(
                user_id=str(candidate_user.id),
                compatibility_score=compatibility_score,
                compatibility_level="fair",
                match_rank=rank
            )
    
    async def _generate_match_reasons(
        self, user1_data: Dict, user2_data: Dict, compatibility_score: float
    ) -> List[str]:
        """매칭 근거 생성"""
        reasons = []
        
        try:
            # 성격 호환성 기반
            personality_compat = self._calculate_personality_compatibility(user1_data, user2_data)
            if personality_compat > 0.7:
                reasons.append("성격적으로 잘 어울리는 조합")
            
            # 감정 호환성 기반
            emotion_compat = self._calculate_emotion_compatibility(user1_data, user2_data)
            if emotion_compat > 0.7:
                reasons.append("감정적으로 안정적인 관계 형성 가능")
            
            # 전체 점수 기반
            if compatibility_score > 0.8:
                reasons.append("매우 높은 전체 호환성")
            elif compatibility_score > 0.65:
                reasons.append("좋은 전체 호환성")
            
            return reasons[:3] if reasons else ["분석 결과 호환성이 있는 상대"]
            
        except Exception:
            return ["호환성 분석 결과 추천"]
    
    async def _analyze_trait_compatibility(
        self, user1_data: Dict, user2_data: Dict
    ) -> Tuple[List[str], List[str]]:
        """특성 호환성 분석"""
        common_traits = []
        complementary_traits = []
        
        try:
            # 성격 특성 비교
            if user1_data["personality"] and user2_data["personality"]:
                traits1 = set(user1_data["personality"].personality_traits or [])
                traits2 = set(user2_data["personality"].personality_traits or [])
                
                # 공통 특성
                common = traits1 & traits2
                common_traits.extend(list(common)[:2])
                
                # 상호 보완적 특성 (예시)
                if "내향적 성향" in traits1 and "외향적 성향" in traits2:
                    complementary_traits.append("내향성과 외향성의 균형")
                
            return common_traits, complementary_traits
            
        except Exception:
            return [], []
    
    # 추가 메서드들 (간략화)
    async def get_matching_profile(self, user_id: str, db: AsyncSession) -> Optional[MatchingProfile]:
        """매칭용 프로필 조회"""
        # TODO: 구현 필요
        pass
    
    async def update_matching_preferences(
        self, user_id: str, preferences: Dict, db: AsyncSession
    ) -> bool:
        """매칭 선호도 업데이트"""
        # TODO: 구현 필요
        pass
    
    async def get_matching_preferences(self, user_id: str, db: AsyncSession) -> Dict:
        """매칭 선호도 조회"""
        # TODO: 구현 필요
        pass
    
    async def get_matching_history(
        self, user_id: str, limit: int, offset: int, db: AsyncSession
    ) -> List[Dict]:
        """매칭 이력 조회"""
        # TODO: 구현 필요
        pass
    
    async def submit_feedback(self, user_id: str, feedback_data: Dict, db: AsyncSession) -> bool:
        """매칭 피드백 제출"""
        # TODO: 구현 필요
        pass
    
    async def get_matching_analytics(self, user_id: str, db: AsyncSession) -> MatchingAnalytics:
        """매칭 분석 데이터 조회"""
        # TODO: 구현 필요
        pass
