@echo off
echo AI Diary Backend 설치를 시작합니다...

echo.
echo 1. pip 업그레이드 중...
python.exe -m pip install --upgrade pip

echo.
echo 2. 핵심 패키지 설치 중...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install python-dotenv==1.0.0

echo.
echo 3. 테스트 서버 실행...
echo 브라우저에서 http://localhost:8000 에 접속하여 확인하세요.
echo 종료하려면 Ctrl+C를 누르세요.
python test_server.py

pause
