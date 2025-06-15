@echo off
echo 🔧 Firebase Private Key 오류 즉시 해결 배포
echo =============================================

cd /d D:\ai-diary-backend

echo.
echo 📊 1단계: 코드 수정사항 배포
echo ========================================
echo ✅ Private key 처리 로직 개선 완료
echo    - 다양한 이스케이프 형식 처리
echo    - 상세 로깅 추가
echo    - Railway 환경변수 호환성 향상

echo.
echo 🚀 Git 커밋 및 배포...
git add -A
git commit -m "🔧 Firebase Private Key 처리 로직 개선 - Railway 환경변수 호환성 강화"
git push origin main

echo.
echo ⏰ Railway 자동 배포 시작... (약 2-3분 소요)
echo.

echo 📋 2단계: Firebase 새 서비스 계정 키 생성 (필수)
echo ========================================
echo.
echo 🔥 Firebase Console 접속 방법:
echo    1. https://console.firebase.google.com/ 접속
echo    2. "ai-diary-matching" 프로젝트 선택
echo    3. 설정(톱니바퀴) → 프로젝트 설정
echo    4. "서비스 계정" 탭 → "새 비공개 키 생성"
echo    5. JSON 파일 다운로드
echo.

echo 💡 Railway 환경변수 설정:
echo    1. https://railway.app 접속
echo    2. 프로젝트 선택 → Variables 탭
echo    3. 다음 5개 환경변수 업데이트:
echo.
echo    FIREBASE_PROJECT_ID="ai-diary-matching"
echo    FIREBASE_PRIVATE_KEY_ID="[JSON의 private_key_id]"
echo    FIREBASE_PRIVATE_KEY="[JSON의 private_key - 따옴표 필수]"
echo    FIREBASE_CLIENT_EMAIL="[JSON의 client_email]"
echo    FIREBASE_CLIENT_ID="[JSON의 client_id]"
echo.

echo 🧪 3단계: 배포 완료 후 테스트
echo ========================================

echo 배포가 완료되면 다음 명령어로 테스트:
echo.
echo 1. 서버 상태 확인:
echo    curl https://ilgi-api-production.up.railway.app/health
echo.
echo 2. Firebase 상태 확인:
echo    curl https://ilgi-api-production.up.railway.app/api/v1/auth/status
echo.
echo 3. Private Key 처리 로그 확인:
echo    Railway Dashboard → Logs에서 다음 로그 확인
echo    "🔑 Private Key 처리 후 길이: XXXX"
echo    "✅ Firebase Admin SDK initialized successfully"
echo.

echo 🎯 예상 성공 결과:
echo ========================================
echo ✅ Firebase 초기화 성공
echo ✅ "Invalid private key" 오류 해결
echo ✅ 토큰 검증 정상 작동
echo.

echo 📞 문제 지속 시:
echo ========================================
echo 1. Railway Logs에서 private key 로그 확인
echo 2. Firebase Console에서 새 키 재생성
echo 3. 환경변수 따옴표 및 형식 재확인
echo.

echo.
echo Firebase Console과 Railway Dashboard를 여시겠습니까? (y/n)
set /p open_browsers=

if /i "%open_browsers%"=="y" (
    echo.
    echo 🌐 브라우저 열기...
    start https://console.firebase.google.com/
    start https://railway.app
    echo.
    echo 💡 두 탭에서 병행 작업:
    echo    1. Firebase: 새 서비스 계정 키 생성
    echo    2. Railway: 환경변수 업데이트
    echo.
)

echo.
echo 🚀 코드 배포 완료! Railway에서 자동 배포 중...
echo    약 2-3분 후 새 로직이 적용됩니다.
echo.
echo 📋 할 일 체크리스트:
echo    [ ] 1. 코드 배포 (완료)
echo    [ ] 2. Firebase 새 서비스 계정 키 생성
echo    [ ] 3. Railway 환경변수 업데이트
echo    [ ] 4. 테스트 실행
echo.

pause
