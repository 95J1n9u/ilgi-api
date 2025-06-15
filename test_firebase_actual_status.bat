@echo off
echo 🧪 Firebase 초기화 성공 확인 테스트
echo ====================================

set BASE_URL=https://ilgi-api-production.up.railway.app

echo.
echo 📊 현재 상황:
echo ====================================
echo ✅ Firebase Admin SDK initialized successfully
echo ✅ 프로젝트: ai-diary-matching
echo ✅ Private Key 처리 완료 (길이: 1704)
echo ⚠️ main.py에서 "비활성화 모드"로 잘못 표시

echo.
echo 🔍 1단계: Firebase 서비스 실제 상태 확인
echo ====================================

echo 📱 Firebase 인증 상태 확인...
curl -s "%BASE_URL%/api/v1/auth/status" | jq . 2>nul || curl -s "%BASE_URL%/api/v1/auth/status"
echo.

echo 🔧 환경 디버깅 (Firebase 설정)...
curl -s "%BASE_URL%/api/v1/debug/env" | jq ".firebase" 2>nul || curl -s "%BASE_URL%/api/v1/debug/env"
echo.

echo 🏥 전체 헬스체크...
curl -s "%BASE_URL%/health" | jq . 2>nul || curl -s "%BASE_URL%/health"
echo.

echo.
echo 🧪 2단계: Firebase 토큰 검증 테스트 (가능한 경우)
echo ====================================

echo.
echo Flutter에서 다음 코드로 토큰을 발급받으세요:
echo.
echo ```dart
echo User? user = FirebaseAuth.instance.currentUser;
echo if (user != null) {
echo   String? token = await user.getIdToken(true);
echo   print('Firebase Token: $token');
echo }
echo ```
echo.

echo 토큰을 받으면 다음 명령어로 검증:
echo curl -X POST "%BASE_URL%/api/v1/auth/verify-token" \
echo   -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
echo.

echo.
echo 🎯 예상 결과:
echo ====================================

echo ✅ Firebase 상태: "operational" 또는 "initialized": true
echo ✅ 토큰 검증: 성공 (실제 Firebase 토큰 사용 시)
echo ✅ 헬스체크: "firebase": true

echo.
echo 📋 3단계: main.py 로그 수정 배포
echo ====================================
echo 현재 main.py에서 "비활성화 모드"라고 잘못 표시하는 로직을
echo 수정하여 재배포할 예정입니다.

echo.
echo 💡 핵심 확인사항:
echo ====================================
echo 1. Firebase 초기화는 이미 성공 완료
echo 2. 토큰 검증 API가 정상 작동하는지 확인 필요
echo 3. main.py 로그 메시지만 수정하면 완료

echo.
echo 위의 테스트 결과를 확인하셨나요? (y/n)
set /p test_done=

if /i "%test_done%"=="y" (
    echo.
    echo 🚀 main.py 수정사항을 배포하겠습니다.
    echo    "Firebase 비활성화 모드" → "Firebase 초기화 완료"로 변경
    echo.
    echo 배포 후 로그에서 올바른 메시지를 확인할 수 있습니다.
) else (
    echo.
    echo 💡 위의 curl 명령어들을 먼저 실행해보세요.
    echo    Firebase가 실제로 작동하는지 확인할 수 있습니다.
)

echo.
pause
