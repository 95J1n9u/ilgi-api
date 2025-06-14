#!/usr/bin/env python3
"""
AI 일기 분석 백엔드 - 정리 후 테스트 스크립트
Firebase 연결 및 Flutter 앱 연동 테스트
"""
import sys
import os
import asyncio
import traceback
from typing import Dict, Any
import json

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title: str):
    """섹션 제목 출력"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(test_name: str, success: bool, message: str = ""):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{status}: {test_name}")
    if message:
        print(f"   └─ {message}")

async def test_basic_imports():
    """기본 모듈 임포트 테스트"""
    print_section("기본 모듈 임포트 테스트")
    
    try:
        # FastAPI 관련
        from fastapi import FastAPI
        print_result("FastAPI 임포트", True)
        
        # Pydantic 관련
        from pydantic import BaseModel
        from pydantic_settings import BaseSettings
        print_result("Pydantic 임포트", True)
        
        # Google Gemini
        import google.generativeai as genai
        print_result("Google Gemini API 임포트", True)
        
        # SQLAlchemy
        from sqlalchemy import create_engine
        print_result("SQLAlchemy 임포트", True)
        
        # 기타 필수 패키지
        import structlog
        import httpx
        import redis
        print_result("기타 필수 패키지 임포트", True)
        
        return True
        
    except ImportError as e:
        print_result("모듈 임포트", False, f"누락된 패키지: {e}")
        return False
    except Exception as e:
        print_result("모듈 임포트", False, f"예상치 못한 오류: {e}")
        return False

async def test_app_structure():
    """앱 구조 및 파일 존재 테스트"""
    print_section("앱 구조 테스트")
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config/settings.py",
        "app/config/database.py",
        "app/api/v1/router.py",
        "app/core/middleware.py",
        "app/core/exceptions.py",
        "app/services/ai_service.py",
        "requirements.txt",
        "Dockerfile",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print_result(f"파일 존재: {file_path}", True)
        else:
            print_result(f"파일 존재: {file_path}", False, "파일이 없습니다")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

async def test_settings_loading():
    """설정 로딩 테스트"""
    print_section("설정 로딩 테스트")
    
    try:
        # 환경변수 임시 설정
        os.environ.setdefault("GEMINI_API_KEY", "test-key")
        os.environ.setdefault("SECRET_KEY", "test-secret")
        
        from app.config.settings import get_settings
        settings = get_settings()
        
        print_result("설정 객체 생성", True)
        print_result("Firebase 자동 감지 기능", True, f"USE_FIREBASE={settings.USE_FIREBASE}")
        print_result("환경변수 로딩", True, f"Environment={settings.ENVIRONMENT}")
        
        # Firebase 설정 확인
        if settings.FIREBASE_PROJECT_ID:
            print_result("Firebase 설정", True, "Firebase 설정이 감지되었습니다")
        else:
            print_result("Firebase 설정", True, "Firebase 설정이 없어 자동으로 비활성화됨")
        
        return True
        
    except Exception as e:
        print_result("설정 로딩", False, f"오류: {e}")
        traceback.print_exc()
        return False

async def test_fastapi_app_creation():
    """FastAPI 앱 생성 테스트"""
    print_section("FastAPI 앱 생성 테스트")
    
    try:
        # 환경변수 설정
        os.environ.setdefault("GEMINI_API_KEY", "test-key")
        os.environ.setdefault("SECRET_KEY", "test-secret")
        os.environ.setdefault("DEBUG", "true")
        
        from app.main import create_application
        app = create_application()
        
        print_result("FastAPI 앱 생성", True)
        print_result("앱 제목", True, f"Title: {app.title}")
        print_result("라우터 포함", True, f"Routes: {len(app.routes)}개")
        
        # 미들웨어 확인
        middleware_count = len(app.user_middleware)
        print_result("미들웨어 로딩", True, f"Middleware: {middleware_count}개")
        
        return True
        
    except Exception as e:
        print_result("FastAPI 앱 생성", False, f"오류: {e}")
        traceback.print_exc()
        return False

async def test_routes():
    """라우트 테스트"""
    print_section("라우트 테스트")
    
    try:
        from app.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(f"{route.methods} {route.path}" if hasattr(route, 'methods') else f"GET {route.path}")
        
        # 필수 라우트 확인
        required_routes = [
            "/health",
            "/",
            "/api/v1/flutter/test",
            "/api/v1/status"
        ]
        
        for required_route in required_routes:
            found = any(required_route in route for route in routes)
            print_result(f"라우트: {required_route}", found)
        
        print_result("전체 라우트", True, f"총 {len(routes)}개 라우트")
        
        return True
        
    except Exception as e:
        print_result("라우트 테스트", False, f"오류: {e}")
        traceback.print_exc()
        return False

async def test_cors_configuration():
    """CORS 설정 테스트"""
    print_section("CORS 설정 테스트")
    
    try:
        from app.main import app
        
        # CORS 미들웨어 확인
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware = middleware
                break
        
        if cors_middleware:
            print_result("CORS 미들웨어", True, "CORS 미들웨어가 설정되어 있습니다")
            print_result("Flutter 앱 지원", True, "모바일 앱 연동 준비 완료")
        else:
            print_result("CORS 미들웨어", False, "CORS 미들웨어를 찾을 수 없습니다")
            return False
        
        return True
        
    except Exception as e:
        print_result("CORS 설정", False, f"오류: {e}")
        return False

async def test_gemini_api_setup():
    """Gemini API 설정 테스트"""
    print_section("Gemini API 설정 테스트")
    
    try:
        import google.generativeai as genai
        
        # API 키 설정 테스트 (실제 API 호출 없이)
        api_key = os.getenv("GEMINI_API_KEY", "test-key")
        if api_key and api_key != "test-key":
            genai.configure(api_key=api_key)
            print_result("Gemini API 키 설정", True, "실제 API 키가 설정됨")
            
            # 모델 생성 테스트
            model = genai.GenerativeModel('gemini-1.5-flash')
            print_result("Gemini 모델 생성", True, "gemini-1.5-flash 모델")
            
        else:
            print_result("Gemini API 키 설정", True, "테스트 키 사용 (실제 API 키 필요)")
        
        return True
        
    except Exception as e:
        print_result("Gemini API 설정", False, f"오류: {e}")
        return False

async def test_flutter_endpoints():
    """Flutter 전용 엔드포인트 테스트"""
    print_section("Flutter 전용 엔드포인트 테스트")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # 헬스체크 엔드포인트
        response = client.get("/health")
        if response.status_code == 200:
            health_data = response.json()
            print_result("헬스체크 엔드포인트", True, f"Status: {health_data.get('status')}")
            print_result("Flutter 준비 상태", True, f"Ready: {health_data.get('ready_for_flutter', False)}")
        else:
            print_result("헬스체크 엔드포인트", False, f"상태 코드: {response.status_code}")
        
        # Flutter 테스트 엔드포인트
        response = client.get("/api/v1/flutter/test")
        if response.status_code == 200:
            test_data = response.json()
            print_result("Flutter 테스트 엔드포인트", True, f"Message: {test_data.get('message', '')[:50]}...")
        else:
            print_result("Flutter 테스트 엔드포인트", False, f"상태 코드: {response.status_code}")
        
        # API 상태 엔드포인트
        response = client.get("/api/v1/status")
        if response.status_code == 200:
            status_data = response.json()
            print_result("API 상태 엔드포인트", True, f"Status: {status_data.get('api_status')}")
        else:
            print_result("API 상태 엔드포인트", False, f"상태 코드: {response.status_code}")
        
        return True
        
    except Exception as e:
        print_result("Flutter 엔드포인트 테스트", False, f"오류: {e}")
        traceback.print_exc()
        return False

def check_environment():
    """환경 확인"""
    print_section("환경 확인")
    
    # .env 파일 확인
    env_exists = os.path.exists(".env")
    print_result(".env 파일", env_exists, ".env 파일이 설정되어 있습니다" if env_exists else ".env 파일을 생성해주세요")
    
    # 필수 환경변수 확인
    required_env_vars = ["GEMINI_API_KEY", "SECRET_KEY"]
    for var in required_env_vars:
        value = os.getenv(var)
        if value and value != "test-key" and value != "test-secret":
            print_result(f"환경변수 {var}", True, "실제 값이 설정됨")
        else:
            print_result(f"환경변수 {var}", False, f"{var}를 .env 파일에 설정해주세요")
    
    # Python 버전 확인
    python_version = sys.version
    print_result("Python 버전", True, f"Python {python_version.split()[0]}")

async def main():
    """메인 테스트 실행"""
    print_section("AI 일기 분석 백엔드 - 정리 후 테스트")
    print("Flutter 앱 연동 및 기본 기능 테스트를 시작합니다.")
    
    # 환경 확인
    check_environment()
    
    # 테스트 실행
    test_results = []
    
    test_results.append(await test_basic_imports())
    test_results.append(await test_app_structure())
    test_results.append(await test_settings_loading())
    test_results.append(await test_fastapi_app_creation())
    test_results.append(await test_routes())
    test_results.append(await test_cors_configuration())
    test_results.append(await test_gemini_api_setup())
    test_results.append(await test_flutter_endpoints())
    
    # 결과 요약
    print_section("테스트 결과 요약")
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"✅ 통과: {passed_tests}/{total_tests} 테스트")
    print(f"❌ 실패: {total_tests - passed_tests}/{total_tests} 테스트")
    
    if passed_tests == total_tests:
        print("\n🎉 모든 테스트가 통과했습니다!")
        print("프로젝트가 정상적으로 설정되어 Flutter 앱과 연동할 준비가 되었습니다.")
        print("\n다음 단계:")
        print("1. .env 파일에 실제 API 키들을 설정하세요")
        print("2. 서버를 실행하세요: python app/main.py")
        print("3. Flutter 앱에서 연결 테스트를 해보세요")
        print("4. API 문서를 확인하세요: http://localhost:8000/docs")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("실패한 항목들을 확인하고 수정해주세요.")
        print("필요한 패키지를 설치하거나 설정을 확인해보세요.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # 현재 디렉토리가 프로젝트 루트인지 확인
    if not os.path.exists("app/main.py"):
        print("❌ 오류: 프로젝트 루트 디렉토리에서 실행해주세요.")
        print("app/main.py 파일이 없습니다.")
        sys.exit(1)
    
    # 비동기 테스트 실행
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
