"""
성격 분석 서비스
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import google.generativeai as genai
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.config.settings import get_settings
from app.models.analysis import DiaryAnalysis, UserPersonalitySummary
from app.schemas.analysis import PersonalityAnalysis, MBTIIndicators, Big5Traits

settings = get_settings()
logger = structlog.get_logger()

# Gemini API 설정
genai.configure(api_key=settings.GEMINI_API_KEY)


class PersonalityAnalysisService:
    """성격 분석 서비스 클래스"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # MBTI 차원 정의
        self.mbti_dimensions = {
            "E": "외향성 - 에너지를 외부 세계에서 얻고 사람들과의 상호작용을 선호",
            "I": "내향성 - 에너지를 내부 세계에서 얻고 혼자만의 시간을 선호",
            "S": "감각형 - 현실적이고 구체적인 정보를 선호, 경험과 사실 중시",
            "N": "직관형 - 가능성과 패턴을 보고 추상적 개념을 선호",
            "T": "사고형 - 논리적이고 객관적인 분석을 통한 의사결정",
            "F": "감정형 - 가치와 감정을 고려한 의사결정",
            "J": "판단형 - 계획적이고 체계적인 접근을 선호",
            "P": "인식형 - 유연하고 자발적인 접근을 선호"
        }
        
        # Big5 특성 정의
        self.big5_traits = {
            "openness": "개방성 - 새로운 경험과 아이디어에 대한 개방성",
            "conscientiousness": "성실성 - 목표 지향적이고 자기 통제 능력",
            "extraversion": "외향성 - 사회적 활동과 긍정적 감정 경험",
            "agreeableness": "친화성 - 타인에 대한 신뢰와 협력적 태도",
            "neuroticism": "신경성 - 부정적 감정과 스트레스에 대한 민감성"
        }
    
    async def analyze_personality(
        self, 
        content: str, 
        user_id: str, 
        db: AsyncSession
    ) -> PersonalityAnalysis:
        """
        텍스트 기반 성격 분석
        """
        try:
            # 1. 현재 텍스트 분석
            current_analysis = await self._analyze_single_text(content)
            
            # 2. 사용자의 이전 분석 결과 조회 (일관성 확인용)
            historical_analyses = await self._get_user_historical_analyses(user_id, db)
            
            # 3. 이전 분석과 비교하여 일관성 점수 계산
            consistency_score = self._calculate_personality_consistency(
                current_analysis, historical_analyses
            )
            
            # 4. 신뢰도 점수 계산
            confidence_level = self._calculate_confidence_level(
                content, historical_analyses, consistency_score
            )
            
            # 5. 성격 요약 생성
            personality_summary = await self._generate_personality_summary(
                current_analysis, historical_analyses
            )
            
            # 6. MBTI 유형 예측
            predicted_mbti = self._predict_mbti_type(current_analysis["mbti_indicators"])
            
            return PersonalityAnalysis(
                mbti_indicators=MBTIIndicators(**current_analysis["mbti_indicators"]),
                big5_traits=Big5Traits(**current_analysis["big5_traits"]),
                predicted_mbti=predicted_mbti,
                personality_summary=personality_summary,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error("personality_analysis_failed", error=str(e))
            return self._create_fallback_personality_analysis()
    
    async def _analyze_single_text(self, content: str) -> Dict[str, Any]:
        """단일 텍스트 성격 분석"""
        try:
            prompt = f"""
            다음 한국어 일기 텍스트를 분석하여 작성자의 성격 특성을 평가해주세요:

            텍스트: "{content}"

            다음 JSON 형식으로 정확히 응답해주세요:
            {{
                "mbti_indicators": {{
                    "E": 0.7, "I": 0.3,
                    "S": 0.4, "N": 0.6,
                    "T": 0.3, "F": 0.7,
                    "J": 0.6, "P": 0.4
                }},
                "big5_traits": {{
                    "openness": 0.75,
                    "conscientiousness": 0.68,
                    "extraversion": 0.82,
                    "agreeableness": 0.79,
                    "neuroticism": 0.23
                }},
                "personality_indicators": [
                    "사회적 상호작용을 즐김",
                    "감정적 결정을 선호",
                    "새로운 경험에 개방적"
                ],
                "reasoning": "분석 근거에 대한 설명"
            }}

            분석 기준:
            1. MBTI 지표: 각 차원별 점수 (0.0-1.0, 합이 1.0이 되도록)
               - E/I: 외향성/내향성
               - S/N: 감각형/직관형  
               - T/F: 사고형/감정형
               - J/P: 판단형/인식형

            2. Big5 특성: 각 특성별 점수 (0.0-1.0)
               - openness: 개방성
               - conscientiousness: 성실성
               - extraversion: 외향성
               - agreeableness: 친화성
               - neuroticism: 신경성

            3. 텍스트에서 나타나는 구체적인 성격 지표들을 찾아 분석
            4. 한국 문화적 맥락을 고려한 해석
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
            return self._validate_personality_result(result)
            
        except Exception as e:
            logger.error("single_text_personality_analysis_failed", error=str(e))
            raise
    
    async def _get_user_historical_analyses(
        self, user_id: str, db: AsyncSession, limit: int = 10
    ) -> List[Dict]:
        """사용자의 이전 성격 분석 결과 조회"""
        try:
            # UUID 형식 검증
            try:
                import uuid
                uuid.UUID(user_id)
            except ValueError:
                # 잘못된 UUID 형식이면 빈 배열 반환
                logger.warning("invalid_user_id_format", user_id=user_id)
                return []
            
            # 최근 10개 분석 결과 조회
            query = select(DiaryAnalysis).where(
                and_(
                    DiaryAnalysis.user_id == user_id,
                    DiaryAnalysis.personality.isnot(None),
                    DiaryAnalysis.status == "completed"
                )
            ).order_by(DiaryAnalysis.processed_at.desc()).limit(limit)
            
            result = await db.execute(query)
            analyses = result.scalars().all()
            
            historical_data = []
            for analysis in analyses:
                if analysis.personality and analysis.mbti_indicators:
                    historical_data.append({
                        "mbti_indicators": analysis.mbti_indicators,
                        "big5_traits": analysis.personality.get("big5_traits", {}),
                        "processed_at": analysis.processed_at,
                        "confidence_score": analysis.confidence_score
                    })
            
            return historical_data
            
        except Exception as e:
            logger.error("get_historical_analyses_failed", error=str(e))
            return []
    
    def _calculate_personality_consistency(
        self, current_analysis: Dict, historical_analyses: List[Dict]
    ) -> float:
        """성격 분석 일관성 점수 계산"""
        if not historical_analyses:
            return 0.5  # 기본값
        
        try:
            consistency_scores = []
            current_mbti = current_analysis["mbti_indicators"]
            current_big5 = current_analysis["big5_traits"]
            
            for historical in historical_analyses:
                # MBTI 일관성 계산
                mbti_consistency = 0
                for dimension in ["E", "I", "S", "N", "T", "F", "J", "P"]:
                    current_score = current_mbti.get(dimension, 0.5)
                    historical_score = historical["mbti_indicators"].get(dimension, 0.5)
                    mbti_consistency += 1 - abs(current_score - historical_score)
                
                mbti_consistency /= 8  # 평균
                
                # Big5 일관성 계산
                big5_consistency = 0
                for trait in ["openness", "conscientiousness", "extraversion", 
                             "agreeableness", "neuroticism"]:
                    current_score = current_big5.get(trait, 0.5)
                    historical_score = historical["big5_traits"].get(trait, 0.5)
                    big5_consistency += 1 - abs(current_score - historical_score)
                
                big5_consistency /= 5  # 평균
                
                # 전체 일관성
                total_consistency = (mbti_consistency + big5_consistency) / 2
                consistency_scores.append(total_consistency)
            
            # 가중 평균 (최근 분석에 더 높은 가중치)
            weights = [1.0 / (i + 1) for i in range(len(consistency_scores))]
            weighted_avg = sum(score * weight for score, weight in 
                              zip(consistency_scores, weights)) / sum(weights)
            
            return round(weighted_avg, 3)
            
        except Exception as e:
            logger.error("consistency_calculation_failed", error=str(e))
            return 0.5
    
    def _calculate_confidence_level(
        self, 
        content: str, 
        historical_analyses: List[Dict], 
        consistency_score: float
    ) -> float:
        """신뢰도 점수 계산"""
        try:
            # 1. 텍스트 길이 기반 신뢰도
            length_confidence = min(1.0, len(content) / 1000)  # 1000자 기준
            
            # 2. 분석 횟수 기반 신뢰도
            analysis_count = len(historical_analyses)
            count_confidence = min(1.0, analysis_count / 10)  # 10회 기준
            
            # 3. 일관성 기반 신뢰도
            consistency_confidence = consistency_score
            
            # 4. 종합 신뢰도
            confidence_level = (
                length_confidence * 0.3 +
                count_confidence * 0.3 +
                consistency_confidence * 0.4
            )
            
            return round(confidence_level, 3)
            
        except Exception:
            return 0.6  # 기본값
    
    async def _generate_personality_summary(
        self, current_analysis: Dict, historical_analyses: List[Dict]
    ) -> List[str]:
        """성격 요약 생성"""
        try:
            # MBTI 기반 주요 특성 추출
            mbti_indicators = current_analysis["mbti_indicators"]
            big5_traits = current_analysis["big5_traits"]
            
            summary = []
            
            # 외향성/내향성
            if mbti_indicators["E"] > mbti_indicators["I"]:
                summary.append("사회적 상호작용을 즐기고 외부 자극을 선호하는 외향적 성향")
            else:
                summary.append("깊이 있는 사고를 즐기고 내적 에너지를 중시하는 내향적 성향")
            
            # 감각/직관
            if mbti_indicators["S"] > mbti_indicators["N"]:
                summary.append("현실적이고 구체적인 정보를 선호하는 감각적 사고")
            else:
                summary.append("가능성과 창의적 아이디어를 추구하는 직관적 사고")
            
            # 사고/감정
            if mbti_indicators["T"] > mbti_indicators["F"]:
                summary.append("논리적이고 객관적인 판단을 중시하는 사고형 의사결정")
            else:
                summary.append("가치와 인간관계를 고려하는 감정형 의사결정")
            
            # 판단/인식
            if mbti_indicators["J"] > mbti_indicators["P"]:
                summary.append("계획적이고 체계적인 생활을 선호하는 판단형 성향")
            else:
                summary.append("유연하고 자발적인 접근을 선호하는 인식형 성향")
            
            # Big5 기반 추가 특성
            if big5_traits["openness"] > 0.7:
                summary.append("새로운 경험과 창의적 활동에 매우 개방적")
            
            if big5_traits["conscientiousness"] > 0.7:
                summary.append("목표 달성을 위한 강한 자기 통제력을 보임")
            
            if big5_traits["agreeableness"] > 0.7:
                summary.append("타인과의 협력과 조화를 중시하는 친화적 성격")
            
            if big5_traits["neuroticism"] < 0.3:
                summary.append("정서적으로 안정되고 스트레스 관리 능력이 우수")
            
            return summary[:5]  # 최대 5개 특성
            
        except Exception as e:
            logger.error("personality_summary_generation_failed", error=str(e))
            return ["성격 분석 결과를 바탕으로 개인적 특성을 파악했습니다."]
    
    def _predict_mbti_type(self, mbti_indicators: Dict[str, float]) -> Optional[str]:
        """MBTI 유형 예측"""
        try:
            mbti_type = ""
            
            # 각 차원에서 높은 점수를 가진 타입 선택
            mbti_type += "E" if mbti_indicators["E"] > mbti_indicators["I"] else "I"
            mbti_type += "S" if mbti_indicators["S"] > mbti_indicators["N"] else "N"
            mbti_type += "T" if mbti_indicators["T"] > mbti_indicators["F"] else "F"
            mbti_type += "J" if mbti_indicators["J"] > mbti_indicators["P"] else "P"
            
            # 신뢰도 확인 (차이가 0.1 미만이면 불확실한 것으로 간주)
            uncertainties = []
            if abs(mbti_indicators["E"] - mbti_indicators["I"]) < 0.1:
                uncertainties.append("E/I")
            if abs(mbti_indicators["S"] - mbti_indicators["N"]) < 0.1:
                uncertainties.append("S/N")
            if abs(mbti_indicators["T"] - mbti_indicators["F"]) < 0.1:
                uncertainties.append("T/F")
            if abs(mbti_indicators["J"] - mbti_indicators["P"]) < 0.1:
                uncertainties.append("J/P")
            
            # 불확실성이 너무 많으면 None 반환
            if len(uncertainties) >= 2:
                return None
            
            return mbti_type
            
        except Exception as e:
            logger.error("mbti_prediction_failed", error=str(e))
            return None
    
    def _validate_personality_result(self, result: Dict) -> Dict:
        """성격 분석 결과 검증 및 정제"""
        validated = {}
        
        # MBTI 지표 검증
        mbti_indicators = result.get("mbti_indicators", {})
        validated_mbti = {}
        
        for dimension in ["E", "I", "S", "N", "T", "F", "J", "P"]:
            value = float(mbti_indicators.get(dimension, 0.5))
            validated_mbti[dimension] = max(0.0, min(1.0, value))
        
        # E/I, S/N, T/F, J/P 쌍의 합이 1.0이 되도록 정규화
        pairs = [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]
        for first, second in pairs:
            total = validated_mbti[first] + validated_mbti[second]
            if total > 0:
                validated_mbti[first] = validated_mbti[first] / total
                validated_mbti[second] = validated_mbti[second] / total
            else:
                validated_mbti[first] = validated_mbti[second] = 0.5
        
        validated["mbti_indicators"] = validated_mbti
        
        # Big5 특성 검증
        big5_traits = result.get("big5_traits", {})
        validated_big5 = {}
        
        for trait in ["openness", "conscientiousness", "extraversion", 
                     "agreeableness", "neuroticism"]:
            value = float(big5_traits.get(trait, 0.5))
            validated_big5[trait] = max(0.0, min(1.0, value))
        
        validated["big5_traits"] = validated_big5
        
        # 기타 필드
        validated["personality_indicators"] = result.get("personality_indicators", [])
        validated["reasoning"] = result.get("reasoning", "")
        
        return validated
    
    def _create_fallback_personality_analysis(self) -> PersonalityAnalysis:
        """실패 시 기본 성격 분석 결과 생성"""
        return PersonalityAnalysis(
            mbti_indicators=MBTIIndicators(
                E=0.5, I=0.5, S=0.5, N=0.5,
                T=0.5, F=0.5, J=0.5, P=0.5
            ),
            big5_traits=Big5Traits(
                openness=0.5,
                conscientiousness=0.5,
                extraversion=0.5,
                agreeableness=0.5,
                neuroticism=0.5
            ),
            predicted_mbti=None,
            personality_summary=["성격 분석을 위해서는 더 많은 데이터가 필요합니다."],
            confidence_level=0.3
        )
    
    async def get_user_personality(self, user_id: str, db: AsyncSession) -> Dict:
        """사용자 종합 성격 분석 결과 조회"""
        try:
            # 사용자 성격 요약 조회
            query = select(UserPersonalitySummary).where(
                UserPersonalitySummary.user_id == user_id
            )
            result = await db.execute(query)
            personality_summary = result.scalar_one_or_none()
            
            if personality_summary:
                return {
                    "user_id": user_id,
                    "overall_mbti": personality_summary.overall_mbti,
                    "overall_big5": personality_summary.overall_big5,
                    "personality_traits": personality_summary.personality_traits,
                    "mbti_consistency": personality_summary.mbti_consistency,
                    "confidence_level": personality_summary.confidence_level,
                    "analysis_count": personality_summary.analysis_count,
                    "last_updated": personality_summary.updated_at.isoformat()
                }
            else:
                return {
                    "user_id": user_id,
                    "message": "성격 분석 데이터가 충분하지 않습니다.",
                    "analysis_count": 0
                }
                
        except Exception as e:
            logger.error("get_user_personality_failed", error=str(e))
            return {"error": "성격 분석 조회 중 오류가 발생했습니다."}
    
    async def update_user_personality_summary(
        self, user_id: str, db: AsyncSession
    ):
        """사용자 성격 요약 업데이트 (백그라운드 작업)"""
        try:
            # 최근 분석 결과들 조회 (최소 3개 이상)
            historical_analyses = await self._get_user_historical_analyses(
                user_id, db, limit=20
            )
            
            if len(historical_analyses) < 3:
                logger.info("insufficient_data_for_personality_summary", 
                           user_id=user_id, count=len(historical_analyses))
                return
            
            # 종합 성격 분석 계산
            overall_analysis = self._calculate_overall_personality(historical_analyses)
            
            # 데이터베이스 업데이트
            query = select(UserPersonalitySummary).where(
                UserPersonalitySummary.user_id == user_id
            )
            result = await db.execute(query)
            personality_summary = result.scalar_one_or_none()
            
            if personality_summary:
                # 기존 레코드 업데이트
                personality_summary.overall_mbti = overall_analysis["overall_mbti"]
                personality_summary.overall_big5 = overall_analysis["overall_big5"]
                personality_summary.personality_traits = overall_analysis["personality_traits"]
                personality_summary.mbti_consistency = overall_analysis["mbti_consistency"]
                personality_summary.confidence_level = overall_analysis["confidence_level"]
                personality_summary.analysis_count = len(historical_analyses)
            else:
                # 새 레코드 생성
                personality_summary = UserPersonalitySummary(
                    user_id=user_id,
                    overall_mbti=overall_analysis["overall_mbti"],
                    overall_big5=overall_analysis["overall_big5"],
                    personality_traits=overall_analysis["personality_traits"],
                    mbti_consistency=overall_analysis["mbti_consistency"],
                    confidence_level=overall_analysis["confidence_level"],
                    analysis_count=len(historical_analyses)
                )
                db.add(personality_summary)
            
            await db.commit()
            
            logger.info("personality_summary_updated", user_id=user_id)
            
        except Exception as e:
            logger.error("update_personality_summary_failed", user_id=user_id, error=str(e))
    
    def _calculate_overall_personality(self, historical_analyses: List[Dict]) -> Dict:
        """종합 성격 분석 계산"""
        try:
            # 가중 평균 계산 (최근 분석에 높은 가중치)
            weights = [1.0 / (i + 1) for i in range(len(historical_analyses))]
            total_weight = sum(weights)
            
            # MBTI 평균
            mbti_avg = {}
            for dimension in ["E", "I", "S", "N", "T", "F", "J", "P"]:
                weighted_sum = sum(
                    analysis["mbti_indicators"].get(dimension, 0.5) * weight
                    for analysis, weight in zip(historical_analyses, weights)
                )
                mbti_avg[dimension] = weighted_sum / total_weight
            
            # Big5 평균
            big5_avg = {}
            for trait in ["openness", "conscientiousness", "extraversion", 
                         "agreeableness", "neuroticism"]:
                weighted_sum = sum(
                    analysis["big5_traits"].get(trait, 0.5) * weight
                    for analysis, weight in zip(historical_analyses, weights)
                )
                big5_avg[trait] = weighted_sum / total_weight
            
            # 전체 MBTI 유형 결정
            overall_mbti = self._predict_mbti_type(mbti_avg)
            
            # 일관성 점수 계산
            mbti_consistency = self._calculate_mbti_consistency(historical_analyses)
            
            # 신뢰도 계산
            confidence_level = min(1.0, len(historical_analyses) / 10 * mbti_consistency)
            
            # 성격 특성 요약
            personality_traits = self._extract_personality_traits(mbti_avg, big5_avg)
            
            return {
                "overall_mbti": overall_mbti,
                "overall_big5": big5_avg,
                "personality_traits": personality_traits,
                "mbti_consistency": mbti_consistency,
                "confidence_level": confidence_level
            }
            
        except Exception as e:
            logger.error("calculate_overall_personality_failed", error=str(e))
            return {
                "overall_mbti": None,
                "overall_big5": {},
                "personality_traits": [],
                "mbti_consistency": 0.5,
                "confidence_level": 0.3
            }
    
    def _calculate_mbti_consistency(self, historical_analyses: List[Dict]) -> float:
        """MBTI 일관성 점수 계산"""
        if len(historical_analyses) < 2:
            return 1.0
        
        try:
            consistency_scores = []
            
            for i in range(len(historical_analyses) - 1):
                current = historical_analyses[i]["mbti_indicators"]
                next_analysis = historical_analyses[i + 1]["mbti_indicators"]
                
                dimension_consistency = []
                for dimension in ["E", "I", "S", "N", "T", "F", "J", "P"]:
                    current_score = current.get(dimension, 0.5)
                    next_score = next_analysis.get(dimension, 0.5)
                    consistency = 1 - abs(current_score - next_score)
                    dimension_consistency.append(consistency)
                
                avg_consistency = sum(dimension_consistency) / len(dimension_consistency)
                consistency_scores.append(avg_consistency)
            
            return sum(consistency_scores) / len(consistency_scores)
            
        except Exception:
            return 0.5
    
    def _extract_personality_traits(self, mbti_avg: Dict, big5_avg: Dict) -> List[str]:
        """성격 특성 추출"""
        traits = []
        
        try:
            # MBTI 기반 특성
            if mbti_avg["E"] > 0.6:
                traits.append("사교적이고 활동적인 성향")
            elif mbti_avg["I"] > 0.6:
                traits.append("깊이 있는 사고를 선호하는 내향적 성향")
            
            if mbti_avg["N"] > 0.6:
                traits.append("창의적이고 혁신적인 아이디어를 추구")
            elif mbti_avg["S"] > 0.6:
                traits.append("현실적이고 실용적인 접근을 선호")
            
            if mbti_avg["F"] > 0.6:
                traits.append("인간관계와 가치를 중시하는 감정적 판단")
            elif mbti_avg["T"] > 0.6:
                traits.append("논리적이고 분석적인 사고 과정")
            
            if mbti_avg["J"] > 0.6:
                traits.append("체계적이고 계획적인 생활 방식")
            elif mbti_avg["P"] > 0.6:
                traits.append("유연하고 적응력이 뛰어난 성격")
            
            # Big5 기반 특성
            if big5_avg["openness"] > 0.7:
                traits.append("새로운 경험에 매우 개방적")
            if big5_avg["conscientiousness"] > 0.7:
                traits.append("목표 지향적이고 책임감이 강함")
            if big5_avg["agreeableness"] > 0.7:
                traits.append("협력적이고 배려심이 깊음")
            if big5_avg["neuroticism"] < 0.3:
                traits.append("정서적으로 안정되고 스트레스 관리 능력 우수")
            
            return traits[:5]  # 최대 5개
            
        except Exception:
            return ["개인적 성격 특성이 나타남"]
