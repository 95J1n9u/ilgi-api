@echo off
chcp 65001 >nul
echo 🚀 AI Diary Backend Railway 배포 테스트 시작...
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

echo 2. 환경 설정 확인 (디버깅)
echo ---------------------------

echo 🔍 환경변수 디버깅...
curl -s "%BASE_URL%/api/v1/debug/env" | jq .
echo.

echo 3. 인증 시스템 테스트 (토큰 없이)
echo -----------------------------------

echo 🔍 Firebase 토큰 검증 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/auth/verify-token" -w "Status: %%{http_code}\n"
echo.

echo 🔍 일기 분석 API (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/analysis/diary" ^
    -H "Content-Type: application/json" ^
    -d "{\"diary_id\":\"test\",\"content\":\"테스트\"}" ^
    -w "Status: %%{http_code}\n"
echo.

echo ==================================================
echo 🎯 기본 테스트 완료!
echo.
echo 📊 결과 해석:
echo - ✅ 기본 엔드포인트들이 200으로 응답하면 수정 성공!
echo - 🔥 Firebase 관련 API는 401/503으로 응답 (정상)
echo - 🚀 500 에러가 사라졌다면 문제 해결됨!
echo.
echo 🔗 추가 확인:
echo - API 문서: %BASE_URL%/docs
echo - 헬스체크: %BASE_URL%/health
echo.
echo 💡 Firebase 토큰 테스트는 Flutter 앱에서 진행하세요!
pause
