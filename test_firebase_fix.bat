@echo off
echo 🔧 Firebase 중복 초기화 문제 해결 테스트
echo ==========================================

cd /d D:\ai-diary-backend

echo 📍 현재 디렉토리: %CD%
echo 🐍 Python 환경 활성화...

if exist "venv\Scripts\activate.bat" (
    echo ✅ 가상환경 발견
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ 가상환경 없음 - 글로벌 Python 사용
)

echo.
echo 🧪 Firebase 초기화 테스트 실행...
python test_firebase_fix.py

echo.
echo 📋 추가 확인사항:
echo ===============

echo 1. 중복 초기화 로그 확인:
echo    "Firebase already initialized - 중복 초기화 방지" 메시지 출력 여부

echo.
echo 2. 서버 실행 테스트:
echo    python -m app.main

echo.
echo 3. API 엔드포인트 테스트:
echo    curl http://localhost:8000/health
echo    curl http://localhost:8000/api/v1/auth/status

echo.
echo 테스트 완료!
pause
