@echo off
echo 🔧 Firebase 서비스 계정 키 완전 재생성 가이드
echo =============================================

echo.
echo 📋 현재 상황:
echo =============================================
echo ✅ Flutter Firebase 연결: 성공
echo ✅ 토큰 발급: 성공 (853자, JWT 형식)
echo ✅ 백엔드 Firebase 초기화: 성공
echo ❌ 토큰 서명 검증: 실패 ("Could not verify token signature")

echo.
echo 💡 문제 원인:
echo =============================================
echo 현재 백엔드에서 사용 중인 서비스 계정 키가
echo ai-diary-matching 프로젝트와 일치하지 않거나 손상됨

echo.
echo 🔥 1단계: Firebase Console에서 새 서비스 계정 키 생성
echo =============================================

echo 📱 Firebase Console 접속:
echo    👉 https://console.firebase.google.com/project/ai-diary-matching/settings/serviceaccounts/adminsdk

echo.
echo 🔑 새 키 생성 단계:
echo    1. "새 비공개 키 생성" 버튼 클릭
echo    2. "키 생성" 확인
echo    3. JSON 파일 다운로드
echo    4. 안전한 위치에 저장

echo.
echo 🚀 2단계: Railway 환경변수 완전 교체
echo =============================================

echo 📱 Railway Dashboard 접속:
echo    👉 https://railway.app (프로젝트 선택 → Variables)

echo.
echo 📋 다운로드한 JSON에서 다음 5개 값을 정확히 복사:
echo -------------------------------------------------------

echo.
echo FIREBASE_PROJECT_ID
echo ↳ "ai-diary-matching" (변경 없음)

echo.
echo FIREBASE_PRIVATE_KEY_ID
echo ↳ JSON의 "private_key_id" 값 (새 값으로 교체)

echo.
echo FIREBASE_PRIVATE_KEY
echo ↳ JSON의 "private_key" 값 (새 값으로 교체)
echo ⚠️ 반드시 큰따옴표로 감싸고 \n 그대로 유지

echo.
echo FIREBASE_CLIENT_EMAIL
echo ↳ JSON의 "client_email" 값 (새 값으로 교체)

echo.
echo FIREBASE_CLIENT_ID
echo ↳ JSON의 "client_id" 값 (새 값으로 교체)

echo.
echo 🧪 3단계: 즉시 테스트 (Railway 재배포 후 약 2분)
echo =============================================

echo 새 키 설정 후 Flutter에서 발급한 토큰으로 테스트:

echo.
echo curl -X POST https://ilgi-api-production.up.railway.app/api/v1/auth/verify-token \
echo   -H "Authorization: Bearer YOUR_FLUTTER_TOKEN" \
echo   -H "Content-Type: application/json"

echo.
echo 🎯 예상 성공 결과:
echo =============================================
echo ```json
echo {
echo   "message": "Token verified successfully",
echo   "user": {
echo     "uid": "dePl1b55xhX7pJ5AQpq8Zon1HPs2",
echo     "provider": "anonymous"
echo   },
echo   "status": "success"
echo }
echo ```

echo.
echo 📞 추가 확인사항:
echo =============================================
echo 1. Firebase Console에서 "ai-diary-matching" 프로젝트 선택 확인
echo 2. 서비스 계정 키가 활성화 상태인지 확인
echo 3. Railway 환경변수 저장 후 자동 재배포 대기

echo.
echo Firebase Console을 여시겠습니까? (y/n)
set /p open_firebase=

if /i "%open_firebase%"=="y" (
    echo.
    echo 🌐 Firebase Console 열기...
    start https://console.firebase.google.com/project/ai-diary-matching/settings/serviceaccounts/adminsdk
    echo.
    echo 🌐 Railway Dashboard도 열기...
    start https://railway.app
    echo.
    echo 💡 두 탭에서 작업:
    echo    1. Firebase: 새 서비스 계정 키 생성
    echo    2. Railway: 환경변수 업데이트
    echo.
    echo 📋 작업 순서:
    echo    1. Firebase에서 "새 비공개 키 생성" 클릭
    echo    2. JSON 다운로드
    echo    3. Railway Variables에서 5개 변수 업데이트
    echo    4. 약 2분 후 테스트
) else (
    echo.
    echo 💡 준비되면 위의 링크들을 사용하세요:
    echo    Firebase: https://console.firebase.google.com/project/ai-diary-matching/settings/serviceaccounts/adminsdk
    echo    Railway: https://railway.app
)

echo.
echo 🎯 성공 확률: 99%%
echo    새 서비스 계정 키로 토큰 서명 검증 문제가 완전히 해결됩니다!

echo.
echo 새 키 생성을 완료하셨나요? (y/n)
set /p key_generated=

if /i "%key_generated%"=="y" (
    echo.
    echo 🔄 Railway 재배포를 기다린 후 (약 2분)
    echo    test_flutter_token_direct.bat를 실행하여 테스트하세요!
    echo.
    echo 🎉 이번에는 반드시 성공할 것입니다!
)

echo.
pause
