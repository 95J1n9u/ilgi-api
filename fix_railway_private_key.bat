@echo off
echo 🔍 Firebase Private Key 손상 발견 및 즉시 수정
echo ================================================

echo.
echo 📋 문제 발견:
echo ================================================
echo ❌ Railway 환경변수에서 private key 내용 손상됨
echo    - .env: "+Rm/\naoejU6N1yRl9NOA+"
echo    - Railway: "+Rm\naoejU6N1yRl9NOA+" (/ 문자 누락!)
echo.
echo 💡 추가 문제:
echo    - .env: \n 이스케이프 시퀀스 사용 (정상)
echo    - Railway: 실제 개행 문자 사용 (Firebase에서 처리 불가)

echo.
echo 🛠️ 즉시 해결 방법:
echo ================================================

echo 🚀 1단계: Railway Dashboard 접속
echo -------------------------------------------------------
echo 📱 https://railway.app 에서 프로젝트 선택
echo 📋 Variables 탭 클릭

echo.
echo 🔧 2단계: FIREBASE_PRIVATE_KEY 정확히 설정
echo -------------------------------------------------------
echo.
echo ⚠️ 중요: 아래 내용을 정확히 복사하여 설정
echo ================================================
echo.
echo 변수명: FIREBASE_PRIVATE_KEY
echo.
echo 값 (따옴표 포함해서 전체 복사):
echo.
echo "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCQEgoiXPyTfjq9\nGHRH12k8KjktIzNbrA8z8CbBziljtN/Iz3wnix5pYxlxXakYk/DHGUKSnzLUhJFZ\nVvpJ+VWwUZ55ifxBLsO6VFIaVJRpj9Vt8QiogPPScilp+xOY3kCCshbkkqS/o4o9\ncqh6mqGp1aU/+kjw2FmLy219gJaiM7UmDppZ5meDhz80rW8N0b3CJ6pWHyBoioYK\n9PJMwuwLWseziip9FR/EHo1MSNkCNewn3y22uqqFgllnI4rzuUeqsGZf1iv5MGXP\n5j9vZqOXvmjexSp7IKDS7DJKmPCRSPzusghNIWdmoCElQ5JpwLFJibSESmxQTT6o\nVq0l+uQ/AgMBAAECggEAIq3s+ZOXiutuOTlrOCXeo4hoZficsrrql+59bdZx+Rm/\naoejU6N1yRl9NOA+RXfLFCn87+1ZX3WfxTkeG3Nk0IH9GzV/XrNikvYcI1FrvjNM\nxV+pXWJZDrXDSUsSTxBkx/EVeKTh+m1j5+GzM3wIYSjX09wr9ammeHOZ4gVzfQyH\n3TZ+JD3pJf4JgA14/Uf0RLQyINUsVmOa4lmT8lFV9t3VmS4Rpgw29R5dqMB496vW\nE9kiQsrAbc2KQCuV1YjUajLVljvZKHUsMRdmWyVh9A7t4bS6qCg4LRctYHzm7GJG\nRvHMv1WsOJHAkQsHk5mPcfQqFoHJuc6JiPXVBPuYLQKBgQDC8TDG+xra2FkmtzeG\n3YECq3hXOnyNJVdYSl6HUYA8ltRW4pXEsqv0XDrEk73MvQb3trpTRMe7no/HaF+/\nbQZPx9PL9UpiFLVjSzLMK+gGpbKxyNMfq3vJ94lrDHV8h5/l52XLq2+8hZpcTLXA\nV20ONsIXiVERzP0JOGSFq+mWVQKBgQC9Md3gcBnh4cJHa0tK2VgMd8q+emAk+E9e\nshzy498uQU5Cz3u9R8e0Mys657cFfBfPZCJP2HebdVy/SpdlXvJawMFT8kJiaWFF\nMZTMB0UNRDVfZa2vb09pSmj2KZTi5IEFavu4UzXGuMc9zWdshlHur6KGLXwYqM+u\nCqN5fIpcQwKBgQCQNV4xBJb0J7Gjq0u/T+Lc973ZQWHcBDCeFr3g+pCTwbwo3guO\n6+G6rfOnceepKniaDSm+6ZWbnIueJv8Vm/BcWmW6bqVs8wbQAlP8p8pICJGtZPOR\nbQjw+lZEw32x9p55s3khdpv86RSsjO6y77m0Fxvzz1gShAL3rCjonaj51QKBgGXh\n4LXoKEf3pwOGx/j6qeus5sVEaVn/Td6U0/oItDrYeCiKSvxXFzf3BiSme2y8sqXA\nKqoMy/wva06oAHdadfBhNLrcDtuoG/WDCboFgC3wuT0yKCH9MypkI7nMEp1MqB4e\nyocsaB0njEO/xR4wBxceBctz2wv8fDohCH93jZq5AoGAMqm3ED93dRcX0DSW/bj4\nsHvvKpkloQQ2QIKn7WSiKoyaYERXedUap72IxHhECLw7joeSdByHddXkMiGxRYAv\n1QjZ7DtzkE1wHQtswdHavlqwLGcImb+WXvYb5+VJA76Q02Qph2oaG9tCVeCYw883\nqld4bD3HgRCuaEMbNglzDQI="
echo.
echo.

echo 📝 중요 설정 규칙:
echo ================================================
echo ✅ 반드시 큰따옴표(")로 전체를 감싸기
echo ✅ \n은 문자 그대로 유지 (실제 개행 X)
echo ✅ 내용을 정확히 복사 (문자 누락 금지)
echo ✅ 앞뒤 공백 없이 설정

echo.
echo 🧪 3단계: 테스트 (설정 후 약 2분 대기)
echo ================================================

echo 1. Firebase 상태 확인:
echo    curl https://ilgi-api-production.up.railway.app/api/v1/auth/status

echo.
echo 2. Private Key 처리 로그 확인:
echo    Railway Dashboard → Logs → 다음 메시지 확인
echo    "🔑 Private Key 처리 후 길이: XXXX"
echo    "✅ Firebase Admin SDK initialized successfully"

echo.
echo 🎯 예상 성공 결과:
echo ================================================
echo ✅ "Invalid private key" 오류 완전 해결
echo ✅ Firebase 초기화 성공
echo ✅ 토큰 검증 정상 작동

echo.
echo 📞 추가 확인사항:
echo ================================================
echo - Railway 환경변수에서 `/` 문자가 복원되었는지 확인
echo - Private key 길이가 1704가 아닌 더 긴 길이로 표시되는지 확인
echo - 로그에서 "Invalid private key" 메시지가 사라졌는지 확인

echo.
echo Railway Dashboard를 여시겠습니까? (y/n)
set /p open_railway=

if /i "%open_railway%"=="y" (
    echo.
    echo 🌐 Railway Dashboard 열기...
    start https://railway.app
    echo.
    echo 💡 다음 단계:
    echo    1. Variables 탭 클릭
    echo    2. FIREBASE_PRIVATE_KEY 찾기
    echo    3. 위의 값으로 정확히 교체
    echo    4. Save 클릭
    echo    5. 2분 후 테스트 실행
)

echo.
echo 🚀 이 스크립트의 값으로 정확히 설정하면 100%% 해결됩니다!
pause
