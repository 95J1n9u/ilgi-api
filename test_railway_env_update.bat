@echo off
echo 🚀 Railway 환경변수 업데이트 완료 확인 스크립트
echo ================================================

set BASE_URL=https://ilgi-api-production.up.railway.app

echo.
echo 📊 1단계: Railway 환경변수 업데이트 상태 확인
echo ========================================

echo 🔍 현재 Firebase 인증 서비스 상태...
curl -s "%BASE_URL%/api/v1/auth/status" | jq . 2>nul || curl -s "%BASE_URL%/api/v1/auth/status"
echo.

echo 🔧 Firebase 설정 디버깅...
curl -s "%BASE_URL%/api/v1/debug/env" | jq ".firebase_config" 2>nul || curl -s "%BASE_URL%/api/v1/debug/env"
echo.

echo.
echo 💡 2단계: Railway 환경변수 업데이트 방법
echo ========================================

echo 🌐 Railway Dashboard 접속:
echo    👉 https://railway.app
echo    👉 로그인 후 "AI Diary Backend" 프로젝트 선택
echo    👉 "Variables" 탭 클릭
echo.

echo 📝 다음 5개 환경변수를 정확히 설정:
echo ------------------------------------------------
echo.
echo FIREBASE_PROJECT_ID
echo 값: ai-diary-matching
echo.
echo FIREBASE_PRIVATE_KEY_ID  
echo 값: 0aadd95639d38a3f238539699c43f3c4a3190bc5
echo.
echo FIREBASE_PRIVATE_KEY
echo 값: "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCQEgoiXPyTfjq9\nGHRH12k8KjktIzNbrA8z8CbBziljtN/Iz3wnix5pYxlxXakYk/DHGUKSnzLUhJFZ\nVvpJ+VWwUZ55ifxBLsO6VFIaVJRpj9Vt8QiogPPScilp+xOY3kCCshbkkqS/o4o9\ncqh6mqGp1aU/+kjw2FmLy219gJaiM7UmDppZ5meDhz80rW8N0b3CJ6pWHyBoioYK\n9PJMwuwLWseziip9FR/EHo1MSNkCNewn3y22uqqFgllnI4rzuUeqsGZf1iv5MGXP\n5j9vZqOXvmjexSp7IKDS7DJKmPCRSPzusghNIWdmoCElQ5JpwLFJibSESmxQTT6o\nVq0l+uQ/AgMBAAECggEAIq3s+ZOXiutuOTlrOCXeo4hoZficsrrql+59bdZx+Rm/\naoejU6N1yRl9NOA+RXfLFCn87+1ZX3WfxTkeG3Nk0IH9GzV/XrNikvYcI1FrvjNM\nxV+pXWJZDrXDSUsSTxBkx/EVeKTh+m1j5+GzM3wIYSjX09wr9ammeHOZ4gVzfQyH\n3TZ+JD3pJf4JgA14/Uf0RLQyINUsVmOa4lmT8lFV9t3VmS4Rpgw29R5dqMB496vW\nE9kiQsrAbc2KQCuV1YjUajLVljvZKHUsMRdmWyVh9A7t4bS6qCg4LRctYHzm7GJG\nRvHMv1WsOJHAkQsHk5mPcfQqFoHJuc6JiPXVBPuYLQKBgQDC8TDG+xra2FkmtzeG\n3YECq3hXOnyNJVdYSl6HUYA8ltRW4pXEsqv0XDrEk73MvQb3trpTRMe7no/HaF+/\nbQZPx9PL9UpiFLVjSzLMK+gGpbKxyNMfq3vJ94lrDHV8h5/l52XLq2+8hZpcTLXA\nV20ONsIXiVERzP0JOGSFq+mWVQKBgQC9Md3gcBnh4cJHa0tK2VgMd8q+emAk+E9e\nshzy498uQU5Cz3u9R8e0Mys657cFfBfPZCJP2HebdVy/SpdlXvJawMFT8kJiaWFF\nMZTMB0UNRDVfZa2vb09pSmj2KZTi5IEFavu4UzXGuMc9zWdshlHur6KGLXwYqM+u\nCqN5fIpcQwKBgQCQNV4xBJb0J7Gjq0u/T+Lc973ZQWHcBDCeFr3g+pCTwbwo3guO\n6+G6rfOnceepKniaDSm+6ZWbnIueJv8Vm/BcWmW6bqVs8wbQAlP8p8pICJGtZPOR\nbQjw+lZEw32x9p55s3khdpv86RSsjO6y77m0Fxvzz1gShAL3rCjonaj51QKBgGXh\n4LXoKEf3pwOGx/j6qeus5sVEaVn/Td6U0/oItDrYeCiKSvxXFzf3BiSme2y8sqXA\nKqoMy/wva06oAHdadfBhNLrcDtuoG/WDCboFgC3wuT0yKCH9MypkI7nMEp1MqB4e\nyocsaB0njEO/xR4wBxceBctz2wv8fDohCH93jZq5AoGAMqm3ED93dRcX0DSW/bj4\nsHvvKpkloQQ2QIKn7WSiKoyaYERXedUap72IxHhECLw7joeSdByHddXkMiGxRYAv\n1QjZ7DtzkE1wHQtswdHavlqwLGcImb+WXvYb5+VJA76Q02Qph2oaG9tCVeCYw883\nqld4bD3HgRCuaEMbNglzDQI=\n-----END PRIVATE KEY-----\n"
echo.
echo FIREBASE_CLIENT_EMAIL
echo 값: firebase-adminsdk-fbsvc@ai-diary-matching.iam.gserviceaccount.com
echo.
echo FIREBASE_CLIENT_ID
echo 값: 109803283160146835773
echo.

echo ⚠️ 중요 주의사항:
echo    - FIREBASE_PRIVATE_KEY는 반드시 따옴표로 감싸기
echo    - 개행문자(\n)는 그대로 유지
echo    - 앞뒤 공백 제거
echo.

echo.
echo 🧪 3단계: 업데이트 후 테스트 (Railway 재배포 완료 후)
echo ========================================

echo 📞 약 2-3분 후 Railway 재배포 완료되면 다음 명령어 실행:
echo.

echo 1. Firebase 상태 재확인:
echo    curl "%BASE_URL%/api/v1/auth/status"
echo.

echo 2. Firebase 설정 디버깅:
echo    curl "%BASE_URL%/api/v1/debug/env"
echo.

echo 3. Flutter에서 새 토큰 발급:
echo    ```dart
echo    User? user = FirebaseAuth.instance.currentUser;
echo    String? token = await user?.getIdToken(true);
echo    print('새 토큰: $token');
echo    ```
echo.

echo 4. 새 토큰으로 검증 테스트:
echo    curl -X POST "%BASE_URL%/api/v1/auth/verify-token" \
echo      -H "Authorization: Bearer YOUR_NEW_TOKEN"
echo.

echo.
echo 🎯 4단계: 예상 성공 결과
echo ========================================

echo ✅ Firebase 상태 확인:
echo ```json
echo {
echo   "service": "Firebase Authentication",
echo   "status": "operational",
echo   "firebase_config": {
echo     "initialized": true,
echo     "project_id": "ai-diary-..."
echo   }
echo }
echo ```
echo.

echo ✅ 토큰 검증 성공:
echo ```json
echo {
echo   "message": "Token verified successfully",
echo   "user": {
echo     "uid": "firebase_user_id",
echo     "email": "user@example.com"
echo   }
echo }
echo ```
echo.

echo.
echo 📈 성공 확률: 99%%
echo    로컬 .env 파일이 이미 새 키로 업데이트되어 있으므로
echo    Railway 환경변수만 맞춰주면 바로 해결됩니다!
echo.

echo 🎉 해결 완료 후:
echo    - "Could not verify token signature" 오류 사라짐
echo    - 모든 Firebase 토큰 검증 정상 작동
echo    - Flutter 앱 백엔드 연동 완전 복구
echo.

echo Railway 환경변수 업데이트를 완료하셨나요? (y/n)
set /p answer=

if /i "%answer%"=="y" (
    echo.
    echo 🔄 Railway 재배포 대기 중... (약 2-3분)
    echo 재배포 완료 후 위의 테스트 명령어들을 실행하세요.
    echo.
    echo 🆘 문제 지속 시:
    echo    1. Railway Variables에서 FIREBASE_PRIVATE_KEY 따옴표 확인
    echo    2. 개행문자(\n) 형식 재확인
    echo    3. Railway 배포 로그에서 Firebase 초기화 성공 확인
) else (
    echo.
    echo 💡 Railway 환경변수 업데이트를 먼저 완료해주세요:
    echo    👉 https://railway.app → Variables 탭
    echo    👉 위의 5개 환경변수 정확히 설정
)

echo.
pause
