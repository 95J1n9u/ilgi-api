@echo off
echo 🚨 UnboundLocalError 긴급 수정 및 배포
echo =======================================

echo 📊 수정 사항:
echo    - security.py에서 중복 "import firebase_admin" 제거
echo    - UnboundLocalError 원인 해결
echo    - Firebase 초기화 오류 수정

echo.
echo 🚀 Git 커밋 및 배포...

git add -A
git commit -m "🔧 Firebase UnboundLocalError 긴급 수정 - 중복 import 제거"
git push origin main

echo.
echo ⏰ Railway 자동 배포 대기 중... (약 2-3분)
echo    배포 완료 후 Firebase 초기화가 정상 작동할 예정입니다.

echo.
echo 📋 배포 완료 후 테스트 순서:
echo ================================

echo 1. Firebase 상태 확인:
echo    curl https://ilgi-api-production.up.railway.app/api/v1/auth/status

echo.
echo 2. 환경변수 확인:
echo    curl https://ilgi-api-production.up.railway.app/api/v1/debug/env

echo.
echo 3. Flutter에서 새 토큰 발급:
echo    User? user = FirebaseAuth.instance.currentUser;
echo    String? token = await user?.getIdToken(true);

echo.
echo 4. 토큰 검증 테스트:
echo    curl -X POST https://ilgi-api-production.up.railway.app/api/v1/auth/verify-token \
echo      -H "Authorization: Bearer YOUR_NEW_TOKEN"

echo.
echo 🎯 예상 결과:
echo ============

echo ✅ Firebase 초기화 성공
echo ✅ "initialized": true
echo ✅ 토큰 검증 정상 작동
echo ✅ "Could not verify token signature" 오류 해결

echo.
echo 배포가 완료되면 위의 테스트를 실행해주세요!
pause
