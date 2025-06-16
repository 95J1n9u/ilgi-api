@echo off
chcp 65001 >nul
echo 🔧 Base64 토큰 검증 오류 수정 배포
echo ==============================

cd /d D:\ai-diary-backend

echo.
echo 📊 수정사항 요약:
echo ================
echo ✅ Base64 패딩 로직 개선
echo    - 나머지 1인 경우 오류 명확히 탐지
echo    - 토큰이 잘렸을 때 사용자에게 안내
echo ✅ 토큰 정제 로직 강화
echo    - 개행문자, 공백, 탭 모두 제거
echo ✅ 상세한 디버깅 로그 추가

echo.
echo 🚀 Git 커밋 및 배포...
git add app/core/security.py
git commit -m "🔧 Base64 토큰 검증 오류 수정

✨ 개선사항:
- Base64 패딩 로직 개선 (나머지 1 오류 탐지)
- 토큰 정제 강화 (개행문자, 공백 제거)
- 상세 디버깅 로그 추가
- 토큰 잘림 문제 명확한 안내

🎯 목적: Invalid base64-encoded string 오류 해결"
git push origin main

echo.
echo ⏰ Railway 배포 중... (약 2-3분 소요)
echo.

echo 📝 이제 다음 단계를 진행하세요:
echo ============================

echo.
echo 🔍 1단계: Flutter에서 새 토큰 발급
echo ------------------------------------
echo 다음 코드를 실행해서 토큰 상태 확인:
echo.
echo ```dart
echo User? user = FirebaseAuth.instance.currentUser;
echo if (user != null) {
echo   String? token = await user.getIdToken(true);
echo   print('=== 토큰 검증 ===');
echo   print('길이: ${token?.length}');
echo   print('점 개수: ${token?.split('.').length}');
echo   
echo   List^<String^> parts = token!.split('.');
echo   for (int i = 0; i ^< parts.length; i++) {
echo     print('Part $i 길이: ${parts[i].length}, 나머지: ${parts[i].length %% 4}');
echo   }
echo   print('전체 토큰:');
echo   print(token);
echo }
echo ```

echo.
echo 🧪 2단계: 디버깅 페이지 테스트
echo -----------------------------
echo 1. 위에서 출력된 토큰 전체를 복사
echo 2. https://ilgi-api-production.up.railway.app/api/v1/debug/debug 접속
echo 3. Firebase ID 토큰 입력란에 붙여넣기
echo 4. "Firebase 토큰 검증" 버튼 클릭

echo.
echo 🎯 예상 결과:
echo =============
echo ✅ 나머지가 모두 0, 2, 3이어야 함 (1이면 안됨)
echo ✅ 총 3개 부분이어야 함
echo ✅ 토큰 검증 성공

echo.
echo 🚨 만약 여전히 341자 오류가 발생한다면:
echo ====================================
echo 1. 토큰 복사 시 전체가 선택되었는지 확인
echo 2. 클립보드 관리자 앱이 토큰을 자르지 않았는지 확인
echo 3. 텍스트 에디터에 붙여넣어서 길이 확인
echo 4. Firebase 토큰이 아닌 다른 토큰을 복사했는지 확인

echo.
echo 💡 추가 디버깅:
echo ==============
echo Railway 배포 완료 후 로그에서 다음 메시지 확인:
echo "❌ payload 부분 Base64 오류: 나머지 1은 유효하지 않음"
echo "☝️ 토큰 복사 시 잘린 것 같습니다"

echo.
echo 🚀 배포 완료! 2-3분 후 새 로직이 적용됩니다.
echo.

pause
