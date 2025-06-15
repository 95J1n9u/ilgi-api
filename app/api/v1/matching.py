"""
매칭 관련 API 엔드포인트 - Firebase 인증 적용
"""
import logging
import time
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.matching import (
    MatchingRequest,
    CompatibilityRequest,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/candidates")
async def get_matching_candidates(
    request: MatchingRequest,
    current_user: Dict = Depends(get_current_user),
):
    """
    사용자 매칭 후보 추천 - Firebase 인증 적용
    """
    try:
        user_uid = current_user["uid"]
        logger.info(f"💕 매칭 후보 요청: user={user_uid}")
        
        # 시뮬레이션 매칭 후보
        candidates = [
            {
                "user_uid": f"candidate_{i}",
                "name": f"매칭후보_{i}",
                "compatibility_score": 0.85 - (i * 0.05),
                "common_interests": ["독서", "영화", "카페"],
                "personality_match": "높음",
                "age_range": "20대",
                "distance": f"{5 + i}km",
                "last_active": "2일 전"
            }
            for i in range(1, min(request.limit + 1, 6))
        ]
        
        return {
            "user_uid": user_uid,
            "candidates": candidates,
            "total_count": len(candidates),
            "filters_applied": request.filters or {},
            "generated_at": "2025-06-14T15:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ 매칭 후보 검색 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find matching candidates: {str(e)}"
        )


@router.post("/compatibility")
async def calculate_compatibility(
    request: CompatibilityRequest,
    current_user: Dict = Depends(get_current_user),
):
    """
    두 사용자 간 호환성 점수 계산
    """
    try:
        user_uid = current_user["uid"]
        target_user_uid = request.target_user_id
        
        logger.info(f"💘 호환성 계산: {user_uid} vs {target_user_uid}")
        
        # 자기 자신과의 호환성 계산 방지
        if user_uid == target_user_uid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot calculate compatibility with yourself"
            )
        
        # 시뮬레이션 호환성 결과
        compatibility = {
            "user1_uid": user_uid,
            "user2_uid": target_user_uid,
            "overall_score": 0.82,
            "compatibility_breakdown": {
                "personality_match": 0.85,
                "interest_overlap": 0.78,
                "communication_style": 0.80,
                "lifestyle_compatibility": 0.86,
                "emotional_compatibility": 0.83
            },
            "shared_traits": ["낙관적", "사교적", "창의적"],
            "complementary_traits": ["계획적 vs 자유로운", "이성적 vs 감성적"],
            "potential_challenges": ["시간 관리 스타일 차이", "의사결정 방식 차이"],
            "recommendations": [
                "공통 관심사인 독서와 영화 감상을 함께 즐겨보세요",
                "서로 다른 시간 관리 스타일을 존중하며 조율해보세요",
                "정기적인 대화 시간을 가져 소통을 늘려보세요"
            ],
            "calculated_at": "2025-06-14T15:00:00Z"
        }
        
        return compatibility
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 호환성 계산 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate compatibility: {str(e)}"
        )


@router.get("/profile")
async def get_matching_profile(
    current_user: Dict = Depends(get_current_user),
):
    """
    매칭용 사용자 프로필 조회
    """
    try:
        user_uid = current_user["uid"]
        logger.info(f"👤 매칭 프로필 조회: user={user_uid}")
        
        # 시뮬레이션 매칭 프로필
        profile = {
            "user_uid": user_uid,
            "display_name": current_user.get("name", "익명 사용자"),
            "email": current_user.get("email"),
            "age_range": "20대",
            "location": "서울",
            "personality_summary": {
                "mbti": "ENFP",
                "traits": ["낙관적", "창의적", "사교적", "공감능력"],
                "communication_style": "감정적이고 표현적"
            },
            "interests": ["독서", "영화감상", "카페투어", "여행", "사진"],
            "lifestyle": {
                "activity_level": "활발함",
                "social_preference": "사교적",
                "work_life_balance": "균형 추구"
            },
            "matching_preferences": {
                "age_range": "20-30대",
                "distance_limit": "20km",
                "personality_types": ["ENFP", "INFP", "ENFJ"],
                "deal_breakers": ["흡연", "극도의 내향성"]
            },
            "recent_activity": {
                "last_diary": "2일 전",
                "mood_trend": "긍정적",
                "active_days": 15
            },
            "privacy_settings": {
                "show_real_name": False,
                "show_detailed_location": False,
                "allow_contact": True
            },
            "updated_at": "2025-06-14T15:00:00Z"
        }
        
        return profile
        
    except Exception as e:
        logger.error(f"❌ 매칭 프로필 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching profile: {str(e)}"
        )


@router.put("/preferences")
async def update_matching_preferences(
    preferences: Dict,
    current_user: Dict = Depends(get_current_user),
):
    """
    매칭 선호도 설정 업데이트
    """
    try:
        user_uid = current_user["uid"]
        logger.info(f"⚙️ 매칭 선호도 업데이트: user={user_uid}")
        
        # 시뮬레이션 업데이트
        return {
            "message": "Matching preferences updated successfully",
            "user_uid": user_uid,
            "preferences": preferences,
            "updated_at": "2025-06-14T15:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ 매칭 선호도 업데이트 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update matching preferences: {str(e)}"
        )


@router.get("/preferences")
async def get_matching_preferences(
    current_user: Dict = Depends(get_current_user),
):
    """
    매칭 선호도 설정 조회
    """
    try:
        user_uid = current_user["uid"]
        logger.info(f"📋 매칭 선호도 조회: user={user_uid}")
        
        # 시뮬레이션 선호도
        preferences = {
            "user_uid": user_uid,
            "age_range": {"min": 22, "max": 32},
            "distance_limit": 20,
            "personality_preferences": ["ENFP", "INFP", "ENFJ", "INFJ"],
            "interest_priorities": ["독서", "영화", "여행", "음식"],
            "lifestyle_preferences": {
                "activity_level": "중간-높음",
                "social_frequency": "주 2-3회",
                "communication_style": "직접적이고 솔직한"
            },
            "deal_breakers": ["흡연", "과도한 음주", "불성실함"],
            "importance_weights": {
                "personality": 0.4,
                "interests": 0.3,
                "lifestyle": 0.2,
                "location": 0.1
            },
            "last_updated": "2025-06-14T15:00:00Z"
        }
        
        return preferences
        
    except Exception as e:
        logger.error(f"❌ 매칭 선호도 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching preferences: {str(e)}"
        )


@router.get("/history")
async def get_matching_history(
    limit: int = 20,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user),
):
    """
    매칭 이력 조회
    """
    try:
        user_uid = current_user["uid"]
        logger.info(f"📚 매칭 이력 조회: user={user_uid}")
        
        # 시뮬레이션 매칭 이력
        history = {
            "user_uid": user_uid,
            "total_matches": 23,
            "successful_connections": 5,
            "limit": limit,
            "offset": offset,
            "matches": [
                {
                    "match_id": f"match_{i+offset}",
                    "partner_uid": f"user_{i+offset}",
                    "partner_name": f"매칭상대_{i}",
                    "compatibility_score": 0.85 - (i * 0.03),
                    "matched_date": f"2025-06-{14-i:02d}T15:00:00Z",
                    "status": ["connected", "declined", "pending"][i % 3],
                    "connection_duration": f"{7-i}일" if i % 3 == 0 else None,
                    "feedback_given": i % 2 == 0
                }
                for i in range(min(limit, 8))
            ]
        }
        
        return history
        
    except Exception as e:
        logger.error(f"❌ 매칭 이력 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching history: {str(e)}"
        )


@router.post("/feedback")
async def submit_matching_feedback(
    feedback_data: Dict,
    current_user: Dict = Depends(get_current_user),
):
    """
    매칭 피드백 제출
    """
    try:
        user_uid = current_user["uid"]
        logger.info(f"📝 매칭 피드백 제출: user={user_uid}")
        
        # 시뮬레이션 피드백 처리
        return {
            "message": "Feedback submitted successfully",
            "user_uid": user_uid,
            "feedback_id": f"feedback_{int(time.time())}",
            "status": "received",
            "submitted_at": "2025-06-14T15:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ 매칭 피드백 제출 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/analytics")
async def get_matching_analytics(
    current_user: Dict = Depends(get_current_user),
):
    """
    매칭 분석 데이터 조회
    """
    try:
        user_uid = current_user["uid"]
        logger.info(f"📊 매칭 분석 조회: user={user_uid}")
        
        # 시뮬레이션 분석 데이터
        analytics = {
            "user_uid": user_uid,
            "matching_stats": {
                "total_potential_matches": 156,
                "matches_generated": 23,
                "successful_connections": 5,
                "connection_rate": 0.22,
                "average_compatibility": 0.78
            },
            "preference_insights": {
                "most_compatible_types": ["ENFP", "INFP", "ENFJ"],
                "successful_traits": ["창의적", "공감능력", "사교적"],
                "improvement_areas": ["의사소통 스타일", "계획성"]
            },
            "activity_patterns": {
                "peak_matching_days": ["금요일", "토요일", "일요일"],
                "response_time_avg": "2.5시간",
                "profile_view_frequency": "높음"
            },
            "recommendations": [
                "프로필에 취미 정보를 더 상세히 추가해보세요",
                "매칭 선호도를 조금 더 넓게 설정해보세요",
                "정기적인 일기 작성으로 매칭 정확도를 높여보세요"
            ],
            "generated_at": "2025-06-14T15:00:00Z"
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"❌ 매칭 분석 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching analytics: {str(e)}"
        )
