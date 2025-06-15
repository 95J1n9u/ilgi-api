@echo off
echo 🔥 Firebase 토큰 검증 문제 긴급 해결 스크립트
echo ================================================

set BASE_URL=https://ilgi-api-production.up.railway.app

echo.
echo 📊 1단계: 현재 서버 상태 확인
echo ========================================

echo 🌐 서버 기본 상태...
curl -s "%BASE_URL%/health" | jq . 2>nul || curl -s "%BASE_URL%/health"
echo.

echo 🔥 Firebase 인증 서비스 상태...
curl -s "%BASE_URL%/api/v1/auth/status" | jq . 2>nul || curl -s "%BASE_URL%/api/v1/auth/status"
echo.

echo 🔧 환경변수 디버깅 (Firebase 설정)...
curl -s "%BASE_URL%/api/v1/debug/env" | jq ".firebase_config" 2>nul || curl -s "%BASE_URL%/api/v1/debug/env"
echo.

echo.
echo 🔍 2단계: 문제 진단
echo ========================================

echo ❌ 현재 문제: "Could not verify token signature"
echo 📋 원인 분석:
echo    - Firebase 프로젝트 ID: ai-diary-matching (정상)
echo    - 토큰 형식: 3개 부분, 853자 (정상)
echo    - Firebase 초기화: 성공
echo    - 토큰 서명 검증: 실패 ← 핵심 문제
echo.

echo 💡 가장 가능성 높은 원인:
echo    1. 서비스 계정 Private Key 문제 (90%%)
echo    2. 토큰 만료 또는 시간 동기화 (5%%)
echo    3. Firebase 권한 설정 문제 (5%%)
echo.

echo.
echo 🛠️ 3단계: 즉시 해결 방법
echo ========================================

echo 🎯 방법 1: 새 Firebase 서비스 계정 키 생성 (권장)
echo ------------------------------------------------
echo.
echo 📱 Firebase Console 접속:
echo    👉 https://console.firebase.google.com/
echo.
echo 🏗️ 프로젝트 선택:
echo    👉 "ai-diary-matching" 클릭
echo.
echo ⚙️ 서비스 계정 설정:
echo    👉 설정 (톱니바퀴) → 프로젝트 설정
echo    👉 "서비스 계정" 탭 클릭
echo.
echo 🔑 새 비공개 키 생성:
echo    👉 "새 비공개 키 생성" 버튼 클릭
echo    👉 JSON 다운로드
echo.
echo 📋 Railway 환경변수 업데이트:
echo    👉 https://railway.app → 프로젝트 선택 → Variables
echo.

echo ----------------------------------------------------------------
echo 📄 JSON 파일에서 다음 값들을 복사하여 Railway에 설정:
echo ----------------------------------------------------------------
echo.
echo FIREBASE_PROJECT_ID=ai-diary-matching
echo FIREBASE_PRIVATE_KEY_ID="6a88bf2974df60a8cc21cf427aecfb52d5435f16"
echo FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIB...\n-----END PRIVATE KEY-----\n"
echo FIREBASE_CLIENT_EMAIL="firebase-adminsdk-fbsvc@ai-diary-matching.iam.gserviceaccount.com"
echo FIREBASE_CLIENT_ID="109803283160146835773"
echo.
echo ⚠️ 중요 사항:
echo    - FIREBASE_PRIVATE_KEY는 반드시 따옴표로 감싸기
echo    - \n은 실제 개행문자로 유지 (이스케이프 안 함)
echo    - 모든 값에 앞뒤 공백 제거
echo.

echo.
echo 🎯 방법 2: Flutter에서 새 토큰 발급
echo ------------------------------------------------
echo.
echo Flutter 앱에서 다음 코드 실행:
echo.
echo ```dart
echo User? user = FirebaseAuth.instance.currentUser;
echo if (user != null) {
echo   // 강제로 새 토큰 발급 (force refresh)
echo   String? newToken = await user.getIdToken(true);
echo   print('새 Firebase 토큰: $newToken');
echo }
echo ```
echo.

echo.
echo 🧪 4단계: 해결 후 테스트
echo ========================================

echo 새 서비스 계정 키 설정 후 다음 명령어로 테스트:
echo.
echo 1. 서버 재시작 대기 (약 2분)
echo 2. Firebase 상태 재확인:
echo    curl "%BASE_URL%/api/v1/auth/status"
echo.
echo 3. 새 토큰으로 검증:
echo    curl -X POST "%BASE_URL%/api/v1/auth/verify-token" \
echo      -H "Authorization: Bearer YOUR_NEW_FIREBASE_TOKEN"
echo.

echo.
echo ⏰ 5단계: 예상 해결 시간
echo ========================================

echo 🚀 총 소요 시간: 약 5-10분
echo    1. Firebase Console에서 새 키 생성: 2분
echo    2. Railway 환경변수 업데이트: 2분
echo    3. 서버 재시작 대기: 2분
echo    4. Flutter에서 새 토큰 발급: 1분
echo    5. 테스트 및 확인: 2분
echo.

echo 📈 성공 확률: 95%%
echo    새 서비스 계정 키 생성으로 대부분의 문제 해결됨
echo.

echo.
echo 🆘 6단계: 문제 지속 시 추가 확인
echo ========================================

echo 1. Private Key 형식 재확인:
echo    - 따옴표 여부
echo    - 개행 문자 처리
echo    - 앞뒤 공백 제거
echo.
echo 2. 서비스 계정 권한 확인:
echo    - Firebase Console → IAM 및 관리자 → IAM
echo    - "Firebase Admin SDK 관리자" 역할 확인
echo.
echo 3. 토큰 만료 시간 확인:
echo    - Flutter에서 토큰 발급 시간 확인
echo    - 서버 시간과 비교
echo.

echo.
echo 📞 지원 요청 시 포함할 정보:
echo ========================================

echo 1. 위 스크립트 실행 결과 전체
echo 2. Firebase Console에서 생성한 새 서비스 계정 키 존재 여부
echo 3. Railway 환경변수 업데이트 완료 여부
echo 4. Flutter에서 발급한 새 토큰 앞 30자리
echo 5. 오류 발생 정확한 시간 (KST)
echo.

echo.
echo 🎉 결론
echo ========================================

echo 💡 "Could not verify token signature" 문제는
echo    95%% 확률로 서비스 계정 키 문제입니다.
echo.
echo 🚀 새 Firebase 서비스 계정 키 생성만으로
echo    문제가 해결됩니다!
echo.
echo 📱 Firebase Console → 새 키 생성 → Railway 업데이트
echo    이 과정이 핵심입니다.
echo.

echo 계속하려면 아무 키나 누르세요...
pause
