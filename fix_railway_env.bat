@echo off
echo Firebase Environment Variables Check & Fix
echo ==========================================

echo Current working .env values:
echo ----------------------------
echo FIREBASE_PROJECT_ID=ai-diary-matching
echo FIREBASE_PRIVATE_KEY_ID=0aadd95639d38a3f238539699c43f3c4a3190bc5
echo.
echo FIREBASE_PRIVATE_KEY=
echo "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCQEgoiXPyTfjq9\nGHRH12k8KjktIzNbrA8z8CbBziljtN/Iz3wnix5pYxlxXakYk/DHGUKSnzLUhJFZ\nVvpJ+VWwUZ55ifxBLsO6VFIaVJRpj9Vt8QiogPPScilp+xOY3kCCshbkkqS/o4o9\ncqh6mqGp1aU/+kjw2FmLy219gJaiM7UmDppZ5meDhz80rW8N0b3CJ6pWHyBoioYK\n9PJMwuwLWseziip9FR/EHo1MSNkCNewn3y22uqqFgllnI4rzuUeqsGZf1iv5MGXP\n5j9vZqOXvmjexSp7IKDS7DJKmPCRSPzusghNIWdmoCElQ5JpwLFJibSESmxQTT6o\nVq0l+uQ/AgMBAAECggEAIq3s+ZOXiutuOTlrOCXeo4hoZficsrrql+59bdZx+Rm/\naoejU6N1yRl9NOA+RXfLFCn87+1ZX3WfxTkeG3Nk0IH9GzV/XrNikvYcI1FrvjNM\nxV+pXWJZDrXDSUsSTxBkx/EVeKTh+m1j5+GzM3wIYSjX09wr9ammeHOZ4gVzfQyH\n3TZ+JD3pJf4JgA14/Uf0RLQyINUsVmOa4lmT8lFV9t3VmS4Rpgw29R5dqMB496vW\nE9kiQsrAbc2KQCuV1YjUajLVljvZKHUsMRdmWyVh9A7t4bS6qCg4LRctYHzm7GJG\nRvHMv1WsOJHAkQsHk5mPcfQqFoHJuc6JiPXVBPuYLQKBgQDC8TDG+xra2FkmtzeG\n3YECq3hXOnyNJVdYSl6HUYA8ltRW4pXEsqv0XDrEk73MvQb3trpTRMe7no/HaF+/\nbQZPx9PL9UpiFLVjSzLMK+gGpbKxyNMfq3vJ94lrDHV8h5/l52XLq2+8hZpcTLXA\nV20ONsIXiVERzP0JOGSFq+mWVQKBgQC9Md3gcBnh4cJHa0tK2VgMd8q+emAk+E9e\nshzy498uQU5Cz3u9R8e0Mys657cFfBfPZCJP2HebdVy/SpdlXvJawMFT8kJiaWFF\nMZTMB0UNRDVfZa2vb09pSmj2KZTi5IEFavu4UzXGuMc9zWdshlHur6KGLXwYqM+u\nCqN5fIpcQwKBgQCQNV4xBJb0J7Gjq0u/T+Lc973ZQWHcBDCeFr3g+pCTwbwo3guO\n6+G6rfOnceepKniaDSm+6ZWbnIueJv8Vm/BcWmW6bqVs8wbQAlP8p8pICJGtZPOR\nbQjw+lZEw32x9p55s3khdpv86RSsjO6y77m0Fxvzz1gShAL3rCjonaj51QKBgGXh\n4LXoKEf3pwOGx/j6qeus5sVEaVn/Td6U0/oItDrYeCiKSvxXFzf3BiSme2y8sqXA\nKqoMy/wva06oAHdadfBhNLrcDtuoG/WDCboFgC3wuT0yKCH9MypkI7nMEp1MqB4e\nyocsaB0njEO/xR4wBxceBctz2wv8fDohCH93jZq5AoGAMqm3ED93dRcX0DSW/bj4\nsHvvKpkloQQ2QIKn7WSiKoyaYERXedUap72IxHhECLw7joeSdByHddXkMiGxRYAv\n1QjZ7DtzkE1wHQtswdHavlqwLGcImb+WXvYb5+VJA76Q02Qph2oaG9tCVeCYw883\nqld4bD3HgRCuaEMbNglzDQI="
echo.
echo FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@ai-diary-matching.iam.gserviceaccount.com
echo FIREBASE_CLIENT_ID=109803283160146835773

echo.
echo IMPORTANT: Copy these EXACT values to Railway Variables
echo ======================================================
echo.
echo 1. Go to: https://railway.app
echo 2. Select your project
echo 3. Click Variables tab
echo 4. Update these 5 variables with EXACT values above
echo 5. Make sure FIREBASE_PRIVATE_KEY has quotes and \n sequences
echo.

echo Open Railway Dashboard? (y/n)
set /p open_railway=
if /i "%open_railway%"=="y" start https://railway.app

pause
