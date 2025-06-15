@echo off
chcp 65001 >nul
echo 🔧 JWT 토큰 갱신 문제 수정 후 테스트 시작...
echo ==================================================

set BASE_URL=https://ilgi-api-production.up.railway.app

echo 1. 기본 서버 상태 확인
echo ------------------------

echo 🔍 루트 엔드포인트 테스트...
curl -s "%BASE_URL%/" | jq .
echo.

echo 🔍 헬스체크 테스트...
curl -s "%BASE_URL%/health" | jq .
echo.

echo 🔍 Flutter 연결 테스트...
curl -s "%BASE_URL%/api/v1/flutter/test" | jq .
echo.

echo 🔍 API 상태 확인...
curl -s "%BASE_URL%/api/v1/status" | jq .
echo.

echo 2. 환경 설정 확인
echo ------------------

echo 🔍 환경변수 디버깅...
curl -s "%BASE_URL%/api/v1/debug/env" | jq .
echo.

echo 3. JWT 토큰 갱신 테스트
echo ======================

echo 🔍 Firebase 토큰 검증 테스트 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/auth/verify-token" -w "Status: %%{http_code}\n"
echo.

echo 🔍 JWT 토큰 갱신 테스트 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/auth/refresh" -w "Status: %%{http_code}\n"
echo.

echo 🔍 일기 분석 API 테스트 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/analysis/diary" ^
    -H "Content-Type: application/json" ^
    -d "{\"diary_id\":\"test\",\"content\":\"테스트\"}" ^
    -w "Status: %%{http_code}\n"
echo.

echo ==================================================
echo 🎯 JWT 토큰 갱신 수정 테스트 완료!
echo.
echo 📊 수정 사항 요약:
echo - ✅ Firebase 조건부 초기화: 500 에러 해결
echo - ✅ JWT 토큰 갱신 로직: 401 에러 해결  
echo - ✅ 모든 API가 JWT 토큰 사용: 일관성 확보
echo - ✅ 에러 메시지 개선: 디버깅 용이성 향상
echo.
echo 🔗 확인 결과:
echo - ✅ 기본 엔드포인트들이 200으로 응답하면 서버 정상
echo - ✅ 인증 관련 API가 401로 응답하면 토큰 검증 정상 작동
echo - ❌ 500 에러가 더 이상 발생하지 않으면 수정 성공!
echo.
echo 💡 Firebase 토큰 테스트:
echo 1. Flutter 앱에서 Firebase 로그인 후 ID 토큰 복사
echo 2. Postman 등에서 다음 단계로 테스트:
echo    Step 1: POST %BASE_URL%/api/v1/auth/verify-token (Firebase ID 토큰)
echo    Step 2: POST %BASE_URL%/api/v1/auth/refresh (발급받은 JWT 토큰)
echo    Step 3: POST %BASE_URL%/api/v1/analysis/diary (JWT 토큰)
echo.
echo 🔗 추가 확인:
echo - API 문서: %BASE_URL%/docs
echo - 환경 디버깅: %BASE_URL%/api/v1/debug/env
echo.
pause
