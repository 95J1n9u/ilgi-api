@echo off
echo 🧪 Flutter 토큰으로 백엔드 토큰 서명 검증 테스트
echo ===============================================

set TOKEN=eyJhbGciOiJSUzI1NiIsImtpZCI6ImE0YTEwZGVjZTk4MzY2ZDZmNjNlMTY3Mjg2YWU5YjYxMWQyYmFhMjciLCJ0eXAiOiJKV1QifQ.eyJwcm92aWRlcl9pZCI6ImFub255bW91cyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9haS1kaWFyeS1tYXRjaGluZyIsImF1ZCI6ImFpLWRpYXJ5LW1hdGNoaW5nIiwiYXV0aF90aW1lIjoxNzQ5OTg4NDY3LCJ1c2VyX2lkIjoiZGVQbDFiNTV4aFg3cEo1QVFwcThab24xSFBzMiIsInN1YiI6ImRlUGwxYjU1eGhYN3BKNUFRcHE4Wm9uMUhQczIiLCJpYXQiOjE3NDk5ODg0NjksImV4cCI6MTc0OTk5MjA2OSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6e30sInNpZ25faW5fcHJvdmlkZXIiOiJhbm9ueW1vdXMifX0.Um_lyEfAmPkgNh8zBWbYUmHnjTxeNwUpsb2NTlKGCJTRsI_jigDXjEQJ3lMBe66ZuVA5x9y_ff3g_TMqwNPGyoNXhjIpkkLLQxgkE9zb0La4pwb7WPvViFbf1Q3q5pSlaqfuqHwYfK5AMFA3z_-jw-B-vrKMcm6nDRCfINzJ_wpJXAzcR7ti2BybPwOSvz7htoVD7ZuhpYE6LFgqToK23uS2rKxL3xvcMau9S9WSX_tqe2X95xT8xHtrhgPTbD80FvFbDEoQKHC0sHJ07FXtSuVSsXrDMsYQjT4-HboLgggbmaFpvvhdow3L1m9qU9nXiJyO-gn4sHK0soOmh9BqPg

echo.
echo 📊 Flutter에서 발급한 토큰 정보:
echo ===============================================
echo 토큰 길이: 853자
echo 사용자 ID: dePl1b55xhX7pJ5AQpq8Zon1HPs2
echo 프로젝트: ai-diary-matching
echo 제공자: anonymous
echo 발급 시간: 1749988469 (2025-06-15 11:54:29)
echo 만료 시간: 1749992069 (2025-06-15 12:54:29)

echo.
echo 🔍 1단계: 백엔드 직접 토큰 검증 테스트
echo ===============================================

echo Flutter에서 발급한 토큰으로 백엔드 검증 시도...
curl -X POST https://ilgi-api-production.up.railway.app/api/v1/auth/verify-token ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -v

echo.
echo.
echo 🔧 2단계: 백엔드 Firebase 설정 확인
echo ===============================================

echo Firebase 상태 확인...
curl -s https://ilgi-api-production.up.railway.app/api/v1/auth/status | jq . 2>nul || curl -s https://ilgi-api-production.up.railway.app/api/v1/auth/status

echo.
echo Firebase 환경 디버깅...
curl -s https://ilgi-api-production.up.railway.app/api/v1/debug/env | jq ".firebase" 2>nul || curl -s https://ilgi-api-production.up.railway.app/api/v1/debug/env

echo.
echo 🎯 예상 결과 분석:
echo ===============================================
echo.
echo ✅ 성공 시 (서비스 계정 키 올바름):
echo    - "message": "Token verified successfully"
echo    - "uid": "dePl1b55xhX7pJ5AQpq8Zon1HPs2"
echo.
echo ❌ 실패 시 (서비스 계정 키 문제):
echo    - "Could not verify token signature"
echo    - 상태 코드: 401
echo.

echo 💡 문제 원인 가능성:
echo ===============================================
echo 1. 서비스 계정 키가 잘못된 Firebase 프로젝트용
echo 2. Private key가 손상되었거나 형식 오류
echo 3. Firebase 프로젝트 ID 불일치
echo 4. 서버 시간 동기화 문제

echo.
echo 🛠️ 즉시 해결 방법:
echo ===============================================
echo 1. Firebase Console에서 새 서비스 계정 키 생성
echo    👉 https://console.firebase.google.com/project/ai-diary-matching/settings/serviceaccounts/adminsdk
echo.
echo 2. Railway 환경변수 전체 교체
echo    👉 새로 다운로드한 JSON의 모든 값으로 업데이트
echo.
echo 3. 즉시 재테스트
echo    👉 동일한 토큰으로 검증 재시도

echo.
echo 테스트 결과를 확인하셨나요? (y/n)
set /p result_checked=

if /i "%result_checked%"=="y" (
    echo.
    echo 🔄 결과에 따른 다음 단계:
    echo ===============================================
    echo.
    echo 성공한 경우:
    echo    ✅ 문제 해결 완료! Flutter 앱 정상 연동 가능
    echo.
    echo 여전히 실패하는 경우:
    echo    🔧 새 Firebase 서비스 계정 키가 필요합니다
    echo    👉 Firebase Console에서 키 재생성 후 Railway 업데이트
) else (
    echo.
    echo 💡 위의 curl 명령어를 실행하여 정확한 오류를 확인하세요.
    echo    결과에 따라 적절한 해결책을 제시하겠습니다.
)

echo.
pause
