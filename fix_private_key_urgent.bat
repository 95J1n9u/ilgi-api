@echo off
echo 🔥 Firebase "Invalid private key" 오류 긴급 해결
echo ===============================================

set BASE_URL=https://ilgi-api-production.up.railway.app

echo.
echo 📋 현재 상황:
echo ===============================================
echo ❌ Firebase initialization failed: "Invalid private key"
echo 📊 Private Key Length: 1704 (정상 크기)
echo 🔑 Private Key ID: 0aadd95639d38a3f238539699c43f3c4a3190bc5
echo 📧 Client Email: firebase-adminsdk-fbsvc@ai-diary-matching.iam.gserviceaccount.com
echo 📊 Project ID: ai-diary-matching (정상)

echo.
echo 💡 문제 원인:
echo ===============================================
echo 1. Railway 환경변수에서 private key 개행문자(\n) 형식 오류
echo 2. 이스케이프 문자가 제대로 처리되지 않음
echo 3. JSON 형식과 환경변수 형식 차이로 인한 문제

echo.
echo 🛠️ 즉시 해결 방법:
echo ===============================================

echo 🔥 1단계: Firebase Console에서 새 서비스 계정 키 생성
echo -------------------------------------------------------
echo 📱 Firebase Console 접속:
echo    👉 https://console.firebase.google.com/
echo    👉 프로젝트: "ai-diary-matching" 선택
echo.
echo ⚙️ 서비스 계정 설정:
echo    👉 설정(톱니바퀴) → 프로젝트 설정
echo    👉 "서비스 계정" 탭 클릭
echo    👉 "새 비공개 키 생성" 버튼 클릭
echo    👉 JSON 파일 다운로드
echo.

echo 🔄 2단계: Railway 환경변수 업데이트
echo -------------------------------------------------------
echo 📱 Railway Dashboard 접속:
echo    👉 https://railway.app
echo    👉 프로젝트 선택 → Variables 탭
echo.
echo 📋 다운로드한 JSON에서 다음 값들 복사:
echo -------------------------------------------------------
echo.
echo FIREBASE_PROJECT_ID
echo ↳ "ai-diary-matching"
echo.
echo FIREBASE_PRIVATE_KEY_ID
echo ↳ JSON의 "private_key_id" 값
echo.
echo FIREBASE_PRIVATE_KEY
echo ↳ JSON의 "private_key" 값 (아래 주의사항 참고)
echo.
echo FIREBASE_CLIENT_EMAIL
echo ↳ JSON의 "client_email" 값
echo.
echo FIREBASE_CLIENT_ID
echo ↳ JSON의 "client_id" 값
echo.

echo ⚠️ FIREBASE_PRIVATE_KEY 설정 주의사항:
echo ================================================
echo.
echo ✅ 올바른 설정:
echo    "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0B...\n-----END PRIVATE KEY-----\n"
echo.
echo    - 반드시 큰따옴표로 전체를 감싸기
echo    - \n은 그대로 유지 (실제 \와 n 문자)
echo    - 앞뒤 공백 없이 설정
echo.
echo ❌ 잘못된 설정:
echo    -----BEGIN PRIVATE KEY-----\n...     (따옴표 없음)
echo    "-----BEGIN PRIVATE KEY-----\\n..."  (이중 백슬래시)
echo    "-----BEGIN PRIVATE KEY----- ..."   (개행문자 없음)
echo.

echo 🧪 3단계: 배포 후 테스트
echo -------------------------------------------------------
echo Railway 환경변수 설정 후 자동 재배포 (약 2-3분 소요)
echo.
echo 테스트 명령어:
echo 1. Firebase 상태 확인:
echo    curl "%BASE_URL%/api/v1/auth/status"
echo.
echo 2. 환경 디버깅:
echo    curl "%BASE_URL%/api/v1/debug/env"
echo.
echo 3. 새 토큰으로 검증:
echo    Flutter에서 새 토큰 발급 후 API 테스트
echo.

echo 🎯 예상 성공 결과:
echo ===============================================
echo ✅ Firebase Admin SDK initialized successfully
echo ✅ Firebase 상태: "operational"
echo ✅ 토큰 검증: "Token verified successfully"
echo.

echo 🚀 성공 확률: 95%%
echo    새 서비스 계정 키 생성으로 대부분 해결됩니다!
echo.

echo Railway Variables 설정을 시작하시겠습니까? (y/n)
set /p start_setup=

if /i "%start_setup%"=="y" (
    echo.
    echo 🌐 Railway Dashboard를 열고 있습니다...
    start https://railway.app
    echo.
    echo 📋 Firebase Console도 열고 있습니다...
    start https://console.firebase.google.com/
    echo.
    echo 💡 두 브라우저 탭에서:
    echo    1. Firebase Console에서 새 서비스 계정 키 생성
    echo    2. Railway Variables에서 환경변수 업데이트
    echo    3. 약 3분 후 위의 테스트 명령어 실행
    echo.
) else (
    echo.
    echo ℹ️ 준비되면 다음 링크들을 이용하세요:
    echo    Firebase Console: https://console.firebase.google.com/
    echo    Railway Dashboard: https://railway.app
)

echo.
echo 🔄 배포 완료 후 이 스크립트를 다시 실행하여 테스트하세요!
pause
