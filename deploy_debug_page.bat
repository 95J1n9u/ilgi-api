@echo off
chcp 65001 >nul
echo 🚀 HTML 디버깅 페이지 추가 완료 - 즉시 배포 및 테스트
echo ==================================================

echo 📝 변경사항 요약:
echo - ✅ JWT 토큰 검증 로직 디버깅 정보 추가
echo - ✅ HTML 기반 실시간 API 테스트 페이지 생성
echo - ✅ JWT 토큰 디코딩 및 분석 API 추가
echo - ✅ 서버 설정 확인 API 추가
echo - ✅ 통합 테스트 도구 제공
echo.

echo 🔧 1단계: Git 커밋 및 푸시
git add .
git commit -m "🔧 HTML 디버깅 페이지 추가 - JWT 토큰 문제 빠른 진단

✨ 새로운 기능:
- HTML 기반 API 디버깅 페이지 (/api/v1/debug/debug)
- JWT 토큰 디코딩 API (/api/v1/debug/token-decode)
- 서버 설정 확인 API (/api/v1/debug/server-config)
- 실시간 인증 플로우 테스트 도구

🔧 개선사항:
- JWT 토큰 검증 로직에 상세 로깅 추가
- Firebase 토큰 vs JWT 토큰 구분 명확화
- 토큰 만료 시간 및 상태 확인 기능
- 통합 테스트 자동화 도구

🎯 목적: JWT 토큰 갱신 401 에러 빠른 디버깅"

echo ⏳ Git 푸시 중...
git push origin main

echo.
echo 🔗 2단계: 즉시 테스트 가능한 URL들
echo ==================================================
echo.

echo 🌟 **메인 디버깅 페이지 (즉시 테스트 가능):**
echo    https://ilgi-api-production.up.railway.app/api/v1/debug/debug
echo.

echo 📊 **개별 API 엔드포인트:**
echo    • 헬스체크: https://ilgi-api-production.up.railway.app/health
echo    • 환경 디버깅: https://ilgi-api-production.up.railway.app/api/v1/debug/env
echo    • 서버 설정: https://ilgi-api-production.up.railway.app/api/v1/debug/server-config
echo    • JWT 디코딩: https://ilgi-api-production.up.railway.app/api/v1/debug/token-decode?token=YOUR_JWT_TOKEN
echo.

echo 🎯 **디버깅 페이지 사용 방법:**
echo 1. 브라우저에서 디버깅 페이지 접속
echo 2. Firebase ID 토큰을 입력 (Flutter 앱에서 복사)
echo 3. 'Firebase 토큰 검증 및 JWT 발급' 버튼 클릭
echo 4. 발급된 JWT 토큰으로 '🔄 JWT 토큰 갱신' 버튼 클릭
echo 5. '🔍 JWT 토큰 디코딩' 버튼으로 토큰 상세 분석
echo 6. '🚀 전체 플로우 테스트 실행'으로 통합 테스트
echo.

echo ⚡ **예상 수정 시간:** 약 2-3분 (Railway 배포 완료 후)
echo.

echo 🔍 **문제 진단 체크리스트:**
echo □ 헬스체크 200 OK 확인
echo □ 서버 설정에서 JWT SECRET_KEY 존재 확인
echo □ Firebase 토큰으로 JWT 발급 성공 확인
echo □ JWT 토큰 디코딩에서 만료 시간 확인
echo □ JWT 토큰 갱신 API 200 OK 확인
echo □ 일기 분석 API 정상 응답 확인
echo.

echo 📱 **Flutter 앱에서 Firebase ID 토큰 복사 방법:**
echo 1. Firebase.initializeApp() 후
echo 2. User? user = FirebaseAuth.instance.currentUser;
echo 3. String? token = await user?.getIdToken();
echo 4. print('Firebase Token: $token'); // 콘솔에서 복사
echo.

echo 🎉 **배포 완료!**
echo 2-3분 후 위 URL에서 실시간 디버깅을 시작하세요!
echo.

echo 💡 **문제 해결 우선순위:**
echo 1. JWT SECRET_KEY 설정 확인
echo 2. JWT 토큰 만료 시간 확인
echo 3. Firebase vs JWT 토큰 타입 구분
echo 4. 토큰 갱신 로직 검증
echo.

echo 🆘 **여전히 문제가 있다면:**
echo 디버깅 페이지 결과를 스크린샷으로 공유해주세요!
echo.

pause
