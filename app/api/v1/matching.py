"""
매칭 관련 API 엔드포인트
"""
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user_from_firebase
from app.schemas.matching import (
    MatchingRequest,
    CompatibilityRequest,
    CompatibilityResponse,
    MatchingCandidatesResponse,
)
from app.services.matching_service import MatchingService

router = APIRouter()


@router.post("/candidates", response_model=MatchingCandidatesResponse)
async def get_matching_candidates(
    request: MatchingRequest,
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    사용자 매칭 후보 추천
    
    - **limit**: 추천할 후보 수 (기본값: 10)
    - **min_compatibility**: 최소 호환성 점수 (기본값: 0.5)
    - **filters**: 추가 필터링 조건
    """
    try:
        # 현재 사용자 ID 설정
        user_id = current_user["uid"]
        
        # 매칭 후보 검색
        candidates = await matching_service.find_matching_candidates(
            user_id=user_id,
            limit=request.limit,
            min_compatibility=request.min_compatibility,
            filters=request.filters
        )
        
        return MatchingCandidatesResponse(
            user_id=user_id,
            candidates=candidates,
            total_count=len(candidates),
            filters_applied=request.filters or {}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find matching candidates: {str(e)}"
        )


@router.post("/compatibility", response_model=CompatibilityResponse)
async def calculate_compatibility(
    request: CompatibilityRequest,
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    두 사용자 간 호환성 점수 계산
    
    - **target_user_id**: 호환성을 계산할 상대방 사용자 ID
    """
    try:
        user_id = current_user["uid"]
        target_user_id = request.target_user_id
        
        # 자기 자신과의 호환성 계산 방지
        if user_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot calculate compatibility with yourself"
            )
        
        # 호환성 점수 계산
        compatibility = await matching_service.calculate_compatibility(
            user_id_1=user_id,
            user_id_2=target_user_id
        )
        
        return compatibility
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate compatibility: {str(e)}"
        )


@router.get("/profile/{user_id}")
async def get_matching_profile(
    user_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    매칭용 사용자 프로필 조회
    """
    try:
        # 본인 프로필이거나 매칭 허용된 경우만 조회 가능
        current_user_id = current_user["uid"]
        
        if user_id != current_user_id:
            # TODO: 매칭 허용 여부 확인 로직 추가
            pass
        
        profile = await matching_service.get_matching_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching profile: {str(e)}"
        )


@router.put("/preferences")
async def update_matching_preferences(
    preferences: Dict,
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    매칭 선호도 설정 업데이트
    """
    try:
        user_id = current_user["uid"]
        
        success = await matching_service.update_matching_preferences(
            user_id=user_id,
            preferences=preferences
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )
        
        return {
            "message": "Matching preferences updated successfully",
            "preferences": preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update matching preferences: {str(e)}"
        )


@router.get("/preferences")
async def get_matching_preferences(
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    매칭 선호도 설정 조회
    """
    try:
        user_id = current_user["uid"]
        preferences = await matching_service.get_matching_preferences(user_id)
        
        return {
            "user_id": user_id,
            "preferences": preferences or {}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching preferences: {str(e)}"
        )


@router.get("/history")
async def get_matching_history(
    limit: int = 20,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    매칭 이력 조회
    """
    try:
        user_id = current_user["uid"]
        
        history = await matching_service.get_matching_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "user_id": user_id,
            "history": history,
            "total_count": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching history: {str(e)}"
        )


@router.post("/feedback")
async def submit_matching_feedback(
    feedback_data: Dict,
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    매칭 피드백 제출
    """
    try:
        user_id = current_user["uid"]
        
        success = await matching_service.submit_feedback(
            user_id=user_id,
            feedback_data=feedback_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit feedback"
            )
        
        return {
            "message": "Feedback submitted successfully",
            "status": "received"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/analytics/{user_id}")
async def get_matching_analytics(
    user_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    matching_service: MatchingService = Depends(),
):
    """
    매칭 분석 데이터 조회
    """
    # 본인 데이터만 조회 가능
    if user_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        analytics = await matching_service.get_matching_analytics(user_id)
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matching analytics: {str(e)}"
        )
