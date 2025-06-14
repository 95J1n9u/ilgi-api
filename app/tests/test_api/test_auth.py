"""
인증 API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestAuthAPI:
    """인증 API 테스트 클래스"""
    
    def test_verify_token_success(self, test_client: TestClient):
        """토큰 검증 성공 테스트"""
        with patch('app.core.security.verify_firebase_token') as mock_verify:
            mock_verify.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "name": "Test User",
                "email_verified": True
            }
            
            response = test_client.post(
                "/api/v1/auth/verify-token",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user_info"]["uid"] == "test_user_123"
    
    def test_verify_token_invalid(self, test_client: TestClient):
        """토큰 검증 실패 테스트"""
        with patch('app.core.security.verify_firebase_token') as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")
            
            response = test_client.post(
                "/api/v1/auth/verify-token",
                headers={"Authorization": "Bearer invalid_token"}
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "Token verification failed" in data["detail"]
    
    def test_verify_token_no_header(self, test_client: TestClient):
        """인증 헤더 없음 테스트"""
        response = test_client.post("/api/v1/auth/verify-token")
        
        assert response.status_code == 403
    
    def test_get_current_user_success(self, test_client: TestClient, auth_headers: dict):
        """현재 사용자 조회 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user:
            mock_user.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "name": "Test User",
                "email_verified": True
            }
            
            response = test_client.get(
                "/api/v1/auth/me",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["uid"] == "test_user_123"
            assert data["email"] == "test@example.com"
    
    def test_get_current_user_unauthorized(self, test_client: TestClient):
        """미인증 사용자 조회 테스트"""
        response = test_client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
    
    def test_logout(self, test_client: TestClient):
        """로그아웃 테스트"""
        response = test_client.post("/api/v1/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert "Successfully logged out" in data["message"]
    
    def test_validate_token_success(self, test_client: TestClient):
        """토큰 유효성 검증 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user:
            mock_user.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com"
            }
            
            response = test_client.get(
                "/api/v1/auth/validate",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert data["user_id"] == "test_user_123"
    
    def test_validate_token_invalid(self, test_client: TestClient):
        """토큰 유효성 검증 실패 테스트"""
        response = test_client.get("/api/v1/auth/validate")
        
        assert response.status_code == 403
    
    def test_refresh_token_success(self, test_client: TestClient):
        """토큰 갱신 성공 테스트"""
        with patch('app.core.security.get_current_user_from_firebase') as mock_user:
            mock_user.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "name": "Test User"
            }
            
            response = test_client.post(
                "/api/v1/auth/refresh",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
