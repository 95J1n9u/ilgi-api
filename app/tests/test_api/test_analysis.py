"""
AI 분석 API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestAnalysisAPI:
    """AI 분석 API 테스트 클래스"""
    
    def test_analyze_diary_success(self, test_client: TestClient, sample_diary_data: dict):
        """일기 분석 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.analyze_diary') as mock_analyze:
            
            # Mock 사용자
            mock_user.return_value = {"uid": "test_user_123"}
            
            # Mock 분석 결과
            mock_result = MagicMock()
            mock_result.diary_id = sample_diary_data["diary_id"]
            mock_result.analysis_id = "analysis_123"
            mock_result.status = "completed"
            mock_result.confidence_score = 0.85
            mock_analyze.return_value = mock_result
            
            response = test_client.post(
                "/api/v1/analysis/diary",
                json=sample_diary_data,
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["diary_id"] == sample_diary_data["diary_id"]
            assert data["status"] == "completed"
    
    def test_analyze_diary_invalid_content(self, test_client: TestClient):
        """일기 분석 - 잘못된 내용 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user:
            mock_user.return_value = {"uid": "test_user_123"}
            
            invalid_data = {
                "diary_id": "diary_test_123",
                "content": "짧음",  # 너무 짧은 내용
                "metadata": {}
            }
            
            response = test_client.post(
                "/api/v1/analysis/diary",
                json=invalid_data,
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 422
    
    def test_analyze_diary_unauthorized(self, test_client: TestClient, sample_diary_data: dict):
        """일기 분석 - 미인증 테스트"""
        response = test_client.post(
            "/api/v1/analysis/diary",
            json=sample_diary_data
        )
        
        assert response.status_code == 403
    
    def test_get_analysis_result_success(self, test_client: TestClient):
        """분석 결과 조회 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.get_analysis_result') as mock_get:
            
            mock_user.return_value = {"uid": "test_user_123"}
            
            # Mock 분석 결과
            mock_result = MagicMock()
            mock_result.diary_id = "diary_test_123"
            mock_result.analysis_id = "analysis_123"
            mock_result.status = "completed"
            mock_get.return_value = mock_result
            
            response = test_client.get(
                "/api/v1/analysis/diary/diary_test_123",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["diary_id"] == "diary_test_123"
    
    def test_get_analysis_result_not_found(self, test_client: TestClient):
        """분석 결과 조회 - 결과 없음 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.get_analysis_result') as mock_get:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_get.return_value = None
            
            response = test_client.get(
                "/api/v1/analysis/diary/non_existent_diary",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 404
    
    def test_batch_analyze_success(self, test_client: TestClient):
        """일괄 분석 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.batch_analyze') as mock_batch:
            
            mock_user.return_value = {"uid": "test_user_123"}
            
            batch_data = {
                "diary_entries": [
                    {
                        "diary_id": "diary_1",
                        "content": "오늘은 즐거운 하루였다.",
                        "metadata": {}
                    },
                    {
                        "diary_id": "diary_2", 
                        "content": "조금 우울한 기분이다.",
                        "metadata": {}
                    }
                ]
            }
            
            response = test_client.post(
                "/api/v1/analysis/batch",
                json=batch_data,
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_entries"] == 2
            assert data["status"] == "processing"
    
    def test_get_user_emotions_success(self, test_client: TestClient):
        """사용자 감정 패턴 조회 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.emotion_service.EmotionAnalysisService.get_user_emotion_patterns') as mock_emotions:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_emotions.return_value = {
                "user_id": "test_user_123",
                "dominant_emotions": ["happiness", "contentment"],
                "emotion_trends": {}
            }
            
            response = test_client.get(
                "/api/v1/analysis/emotions/test_user_123",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "test_user_123"
    
    def test_get_user_emotions_forbidden(self, test_client: TestClient):
        """사용자 감정 패턴 조회 - 접근 금지 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user:
            mock_user.return_value = {"uid": "test_user_123"}
            
            response = test_client.get(
                "/api/v1/analysis/emotions/other_user_456",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 403
    
    def test_get_user_personality_success(self, test_client: TestClient):
        """사용자 성격 분석 조회 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.personality_service.PersonalityAnalysisService.get_user_personality') as mock_personality:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_personality.return_value = {
                "user_id": "test_user_123",
                "overall_mbti": "ENFJ",
                "confidence_level": 0.8
            }
            
            response = test_client.get(
                "/api/v1/analysis/personality/test_user_123",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "test_user_123"
            assert data["overall_mbti"] == "ENFJ"
    
    def test_get_user_insights_success(self, test_client: TestClient):
        """사용자 종합 인사이트 조회 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.get_user_insights') as mock_insights:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_insights.return_value = MagicMock()
            
            response = test_client.get(
                "/api/v1/analysis/insights/test_user_123",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
    
    def test_delete_analysis_success(self, test_client: TestClient):
        """분석 결과 삭제 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.delete_analysis') as mock_delete:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_delete.return_value = True
            
            response = test_client.delete(
                "/api/v1/analysis/diary/diary_test_123",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data["message"]
    
    def test_delete_analysis_not_found(self, test_client: TestClient):
        """분석 결과 삭제 - 결과 없음 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.delete_analysis') as mock_delete:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_delete.return_value = False
            
            response = test_client.delete(
                "/api/v1/analysis/diary/non_existent_diary",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 404
    
    def test_get_analysis_stats_success(self, test_client: TestClient):
        """분석 통계 조회 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.get_analysis_stats') as mock_stats:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_stats.return_value = {
                "total_analyses": 10,
                "avg_sentiment_score": 0.6,
                "dominant_emotions": ["happiness", "contentment"]
            }
            
            response = test_client.get(
                "/api/v1/analysis/stats/test_user_123",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_analyses"] == 10
    
    def test_get_analysis_history_success(self, test_client: TestClient):
        """분석 이력 조회 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user, \
             patch('app.services.ai_service.AIAnalysisService.get_analysis_history') as mock_history:
            
            mock_user.return_value = {"uid": "test_user_123"}
            mock_history.return_value = [
                {
                    "analysis_id": "analysis_1",
                    "diary_id": "diary_1",
                    "primary_emotion": "happiness",
                    "sentiment_score": 0.8
                }
            ]
            
            response = test_client.get(
                "/api/v1/analysis/history/test_user_123?limit=10&offset=0",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["analysis_id"] == "analysis_1"
