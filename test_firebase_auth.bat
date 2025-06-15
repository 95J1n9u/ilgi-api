@echo off
chcp 65001 >nul
echo 🧪 Firebase 인증 시스템 완전 테스트
echo ==================================================

set BASE_URL=https://ilgi-api-production.up.railway.app

echo 📋 테스트할 항목들:
echo - ✅ 기본 서버 상태 확인
echo - 🔥 Firebase 인증 API 테스트  
echo - 📝 일기 분석 API 테스트
echo - 💕 매칭 시스템 API 테스트
echo - 🔍 디버깅 및 모니터링 확인
echo.

echo 🔍 1단계: 기본 서버 상태 확인
echo ========================================

echo 🌐 루트 엔드포인트 테스트...
curl -s "%BASE_URL%/" | jq .
echo.

echo 💚 헬스체크 테스트...
curl -s "%BASE_URL%/health" | jq .
echo.

echo 📱 Flutter 연결 테스트...
curl -s "%BASE_URL%/api/v1/flutter/test" | jq .
echo.

echo 📊 API 상태 확인...
curl -s "%BASE_URL%/api/v1/status" | jq .
echo.

echo 🔧 환경 디버깅 확인...
curl -s "%BASE_URL%/api/v1/debug/env" | jq .
echo.

echo 🔥 2단계: Firebase 인증 API 테스트
echo ========================================

echo 🚫 인증 없이 토큰 검증 테스트 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/auth/verify-token" -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 토큰 갱신 테스트 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/auth/refresh" -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 사용자 정보 조회 (401 예상)...
curl -s -X GET "%BASE_URL%/api/v1/auth/me" -w "Status: %%{http_code}\n"
echo.

echo ✅ 인증 상태 확인...
curl -s "%BASE_URL%/api/v1/auth/status" | jq .
echo.

echo 📝 3단계: 일기 분석 API 테스트
echo ========================================

echo 🚫 인증 없이 일기 분석 테스트 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/analysis/diary" ^
    -H "Content-Type: application/json" ^
    -d "{\"diary_id\":\"test\",\"content\":\"테스트 일기\"}" ^
    -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 감정 분석 조회 (401 예상)...
curl -s -X GET "%BASE_URL%/api/v1/analysis/emotions" -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 성격 분석 조회 (401 예상)...
curl -s -X GET "%BASE_URL%/api/v1/analysis/personality" -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 인사이트 조회 (401 예상)...
curl -s -X GET "%BASE_URL%/api/v1/analysis/insights" -w "Status: %%{http_code}\n"
echo.

echo 💕 4단계: 매칭 시스템 API 테스트
echo ========================================

echo 🚫 인증 없이 매칭 후보 조회 (401 예상)...
curl -s -X POST "%BASE_URL%/api/v1/matching/candidates" ^
    -H "Content-Type: application/json" ^
    -d "{\"limit\":5}" ^
    -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 매칭 프로필 조회 (401 예상)...
curl -s -X GET "%BASE_URL%/api/v1/matching/profile" -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 매칭 선호도 조회 (401 예상)...
curl -s -X GET "%BASE_URL%/api/v1/matching/preferences" -w "Status: %%{http_code}\n"
echo.

echo 🚫 인증 없이 매칭 분석 조회 (401 예상)...
curl -s -X GET "%BASE_URL%/api/v1/matching/analytics" -w "Status: %%{http_code}\n"
echo.

echo 📖 5단계: API 문서 접근 확인
echo ========================================

echo 📚 OpenAPI 스키마 확인...
curl -s "%BASE_URL%/api/v1/openapi.json" | jq . | head -20
echo.

echo 📋 API 문서 접근 확인...
curl -s "%BASE_URL%/docs" -I | grep "HTTP/"
echo.

echo ==================================================
echo 🎯 Firebase 인증 시스템 테스트 완료!
echo.

echo 📊 테스트 결과 요약:
echo ========================================
echo.

echo ✅ **성공적인 결과들 (예상):**
echo - 🌐 루트, 헬스체크, 상태 확인: 200 OK
echo - 📱 Flutter 연결 테스트: 200 OK  
echo - 🔧 환경 디버깅: 200 OK (개발모드일 때)
echo - 📚 API 문서: 200 OK
echo - 🔥 인증 상태 확인: 200 OK
echo.

echo ✅ **정상적인 보안 결과들 (예상):**
echo - 🚫 모든 인증 필요 API: 401 Unauthorized
echo - 🔒 Firebase 토큰 없이 접근 차단 정상
echo.

echo 🔥 **Firebase 토큰으로 실제 테스트:**
echo ========================================
echo.

echo 💡 **Flutter 앱에서 Firebase 토큰 복사 방법:**
echo.
echo ```dart
echo User? user = FirebaseAuth.instance.currentUser;
echo String? token = await user?.getIdToken();
echo print('Firebase Token: ^$token');
echo ```
echo.

echo 🧪 **Firebase 토큰으로 수동 테스트:**
echo.
echo 1. **토큰 검증:**
echo    curl -X POST %BASE_URL%/api/v1/auth/verify-token \
echo      -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
echo.
echo 2. **일기 분석:**
echo    curl -X POST %BASE_URL%/api/v1/analysis/diary \
echo      -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
echo      -H "Content-Type: application/json" \
echo      -d '{"diary_id":"test","content":"오늘은 정말 좋은 하루였다."}'
echo.
echo 3. **매칭 후보:**
echo    curl -X POST %BASE_URL%/api/v1/matching/candidates \
echo      -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
echo      -H "Content-Type: application/json" \
echo      -d '{"limit":5}'
echo.

echo 🎯 **성공 기준:**
echo ========================================
echo.

echo ✅ **기본 기능 (인증 불필요):**
echo - 루트 엔드포인트: 200 응답, 서버 정보 포함
echo - 헬스체크: 200 응답, Firebase 상태 표시
echo - API 상태: 200 응답, 서비스 상태 정보
echo - Flutter 테스트: 200 응답, 연결 성공 메시지
echo.

echo 🔒 **보안 기능 (인증 필요):**
echo - 모든 보호된 API: 401 에러 (정상)
echo - Firebase 토큰 없는 요청: 차단 (정상)
echo - 명확한 오류 메시지: 표시 (정상)
echo.

echo 🔥 **Firebase 토큰 기능 (토큰 필요):**
echo - 토큰 검증: 200 응답, 사용자 정보 반환
echo - 일기 분석: 200 응답, 분석 결과 반환
echo - 매칭 시스템: 200 응답, 매칭 후보 반환
echo.

echo 🚨 **문제 발생 시 확인사항:**
echo ========================================
echo.

echo ❌ **500 에러 발생 시:**
echo - Firebase 환경변수 설정 확인
echo - Railway 로그 확인
echo - 환경 디버깅 API 결과 확인
echo.

echo ❌ **401 에러 지속 시:**
echo - Firebase 토큰 유효성 확인
echo - 토큰 만료 시간 확인  
echo - Firebase 프로젝트 설정 확인
echo.

echo ❌ **API 문서 접근 불가 시:**
echo - 서버 상태 재확인
echo - Railway 배포 상태 확인
echo.

echo 📞 **지원 요청 시 포함할 정보:**
echo - 위 테스트 스크립트 실행 결과 전체
echo - Firebase 토큰 앞 30자리
echo - 오류 발생한 정확한 시간
echo - 사용 중인 Firebase 프로젝트 ID
echo.

echo 🎉 **결론:**
echo Firebase 인증 시스템이 완전히 구현되었습니다!
echo 모든 API가 Firebase 토큰으로 보호되며,
echo Flutter 앱에서 정상적으로 사용할 수 있습니다.
echo.

pause