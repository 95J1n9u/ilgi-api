"""
AI 분석 관련 API 엔드포인트
"""
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.api.deps import get_database, get_ai_service, get_emotion_service, get_personality_service
from app.core.security import get_current_user_from_firebase
from app.schemas.analysis import (
    DiaryAnalysisRequest,
    DiaryAnalysisResponse,
    BatchAnalysisRequest,
    UserInsightsResponse,
)
from app.services.ai_service import AIAnalysisService
from app.services.emotion_service import EmotionAnalysisService
from app.services.personality_service import PersonalityAnalysisService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/diary", response_model=DiaryAnalysisResponse)
async def analyze_diary(
    request: DiaryAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user_from_firebase),
    ai_service: AIAnalysisService = Depends(get_ai_service),
    db: AsyncSession = Depends(get_database),
):
    """
    일기 텍스트 AI 분석
    
    - **diary_id**: 일기 고유 ID
    - **content**: 분석할 일기 내용
    - **metadata**: 추가 메타데이터 (날짜, 날씨, 활동 등)
    """
    try:
        # 사용자 ID 설정
        request.user_id = current_user["uid"]
        
        # AI 분석 실행
        analysis_result = await ai_service.analyze_diary(request, db)
        
        # 백그라운드에서 사용자 벡터 업데이트
        background_tasks.add_task(
            ai_service.update_user_vectors,
            user_id=current_user["uid"],
            analysis_result=analysis_result,
            db=db
        )
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/diary/{diary_id}", response_model=DiaryAnalysisResponse)
async def get_analysis_result(
    diary_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    ai_service: AIAnalysisService = Depends(get_ai_service),
    db: AsyncSession = Depends(get_database),
):
    """
    분석 결과 조회
    """
    try:
        analysis_result = await ai_service.get_analysis_result(
            diary_id=diary_id,
            user_id=current_user["uid"],
            db=db
        )
        
        if not analysis_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis result not found"
            )
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )


@router.post("/batch")
async def analyze_batch(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user_from_firebase),
    ai_service: AIAnalysisService = Depends(),
):
    """
    일괄 분석 (관리자 전용)
    """
    # TODO: 관리자 권한 확인 추가
    
    try:
        # 백그라운드에서 일괄 분석 실행
        background_tasks.add_task(
            ai_service.batch_analyze,
            diary_requests=request.diary_entries,
            user_id=current_user["uid"]
        )
        
        return {
            "message": "Batch analysis started",
            "total_entries": len(request.diary_entries),
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )


@router.get("/emotions/{user_id}")
async def get_user_emotions(
    user_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    emotion_service: EmotionAnalysisService = Depends(),
):
    """
    사용자 감정 패턴 조회
    """
    # 본인 데이터만 조회 가능
    if user_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        emotion_patterns = await emotion_service.get_user_emotion_patterns(user_id)
        return emotion_patterns
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve emotion patterns: {str(e)}"
        )


@router.get("/personality/{user_id}")
async def get_user_personality(
    user_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    personality_service: PersonalityAnalysisService = Depends(),
):
    """
    사용자 성격 분석 결과 조회
    """
    # 본인 데이터만 조회 가능
    if user_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        personality_analysis = await personality_service.get_user_personality(user_id)
        return personality_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve personality analysis: {str(e)}"
        )


@router.get("/insights/{user_id}", response_model=UserInsightsResponse)
async def get_user_insights(
    user_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    ai_service: AIAnalysisService = Depends(),
):
    """
    사용자 종합 인사이트 조회
    """
    # 본인 데이터만 조회 가능
    if user_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        insights = await ai_service.get_user_insights(user_id)
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve insights: {str(e)}"
        )


@router.get("/history/{user_id}")
async def get_analysis_history(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user_from_firebase),
    ai_service: AIAnalysisService = Depends(),
):
    """
    분석 이력 조회
    """
    # 본인 데이터만 조회 가능
    if user_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        history = await ai_service.get_analysis_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis history: {str(e)}"
        )


@router.delete("/diary/{diary_id}")
async def delete_analysis(
    diary_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    ai_service: AIAnalysisService = Depends(),
):
    """
    분석 결과 삭제
    """
    try:
        success = await ai_service.delete_analysis(
            diary_id=diary_id,
            user_id=current_user["uid"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        return {"message": "Analysis deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete analysis: {str(e)}"
        )


@router.get("/stats/{user_id}")
async def get_analysis_stats(
    user_id: str,
    current_user: Dict = Depends(get_current_user_from_firebase),
    ai_service: AIAnalysisService = Depends(),
):
    """
    분석 통계 조회
    """
    # 본인 데이터만 조회 가능
    if user_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        stats = await ai_service.get_analysis_stats(user_id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis stats: {str(e)}"
        )
