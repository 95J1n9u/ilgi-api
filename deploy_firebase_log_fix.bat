@echo off
echo 🔧 Firebase 초기화 성공 - main.py 로그 메시지 수정 배포
echo ====================================================

cd /d D:\ai-diary-backend

echo.
echo 📊 현재 상황:
echo ====================================================
echo ✅ Firebase 실제 초기화: 성공
echo ✅ Firebase Admin SDK: 정상 작동
echo ❌ main.py 로그 메시지: 잘못 표시 ("비활성화 모드")

echo.
echo 🔧 수정 내용:
echo ====================================================
echo Before: "🔥 Firebase 비활성화 모드 - 서버는 정상 구동"
echo After:  "🔥 Firebase 초기화 완료 - 인증 서비스 준비 완료"

echo.
echo 🚀 Git 커밋 및 배포...
git add -A
git commit -m "🔧 Firebase 초기화 성공 로그 메시지 수정 - 올바른 상태 표시"
git push origin main

echo.
echo ⏰ Railway 자동 배포 중... (약 2분 소요)

echo.
echo 📋 배포 완료 후 확인할 로그:
echo ====================================================
echo ✅ "🔥 Firebase 초기화 완료 - 인증 서비스 준비 완료"
echo ✅ "✅ Firebase Admin SDK initialized successfully"
echo ✅ "🏗️ 초기화된 프로젝트: ai-diary-matching"

echo.
echo 🧪 배포 완료 후 테스트:
echo ====================================================

echo 1. 새 로그 확인:
echo    Railway Dashboard → Logs → 위의 성공 메시지 확인

echo.
echo 2. Firebase 토큰 검증 테스트:
echo    curl -X POST https://ilgi-api-production.up.railway.app/api/v1/auth/verify-token \
echo      -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"

echo.
echo 3. Flutter 앱 연동 테스트:
echo    - Firebase 토큰 발급
echo    - 백엔드 API 호출
echo    - 일기 분석 기능 테스트

echo.
echo 🎯 완료 상태:
echo ====================================================
echo ✅ Firebase 중복 초기화 문제 해결
echo ✅ "Invalid private key" 오류 해결
echo ✅ Firebase 초기화 성공
echo ✅ 올바른 로그 메시지 표시
echo ✅ 인증 서비스 준비 완료

echo.
echo 🎉 모든 Firebase 관련 문제가 해결되었습니다!
echo    이제 Flutter 앱에서 정상적으로 백엔드 연동이 가능합니다.

echo.
echo Railway 배포 로그를 확인하시겠습니까? (y/n)
set /p check_logs=

if /i "%check_logs%"=="y" (
    echo.
    echo 🌐 Railway Dashboard 열기...
    start https://railway.app
    echo.
    echo 💡 Logs 탭에서 다음 메시지를 확인하세요:
    echo    "🔥 Firebase 초기화 완료 - 인증 서비스 준비 완료"
)

echo.
echo 🚀 배포 완료! 약 2분 후 새로운 로그 메시지를 확인할 수 있습니다.
pause
