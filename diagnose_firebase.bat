@echo off
echo Firebase Service Account Key Diagnosis
echo =====================================

echo.
echo Step 1: Check Backend Firebase Status
echo -------------------------------------
curl -s https://ilgi-api-production.up.railway.app/api/v1/auth/status

echo.
echo.
echo Step 2: Check Environment Debug Info
echo ------------------------------------
curl -s https://ilgi-api-production.up.railway.app/api/v1/debug/env

echo.
echo.
echo Step 3: Test Token Verification
echo ------------------------------
echo Testing with Flutter token...
curl -X POST https://ilgi-api-production.up.railway.app/api/v1/auth/verify-token -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImE0YTEwZGVjZTk4MzY2ZDZmNjNlMTY3Mjg2YWU5YjYxMWQyYmFhMjciLCJ0eXAiOiJKV1QifQ.eyJwcm92aWRlcl9pZCI6ImFub255bW91cyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9haS1kaWFyeS1tYXRjaGluZyIsImF1ZCI6ImFpLWRpYXJ5LW1hdGNoaW5nIiwiYXV0aF90aW1lIjoxNzQ5OTg4NDY3LCJ1c2VyX2lkIjoiZGVQbDFiNTV4aFg3cEo1QVFwcThab24xSFBzMiIsInN1YiI6ImRlUGwxYjU1eGhYN3BKNUFRcHE4Wm9uMUhQczIiLCJpYXQiOjE3NDk5ODg0NjksImV4cCI6MTc0OTk5MjA2OSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6e30sInNpZ25faW5fcHJvdmlkZXIiOiJhbm9ueW1vdXMifX0.Um_lyEfAmPkgNh8zBWbYUmHnjTxeNwUpsb2NTlKGCJTRsI_jigDXjEQJ3lMBe66ZuVA5x9y_ff3g_TMqwNPGyoNXhjIpkkLLQxgkE9zb0La4pwb7WPvViFbf1Q3q5pSlaqfuqHwYfK5AMFA3z_-jw-B-vrKMcm6nDRCfINzJ_wpJXAzcR7ti2BybPwOSvz7htoVD7ZuhpYE6LFgqToK23uS2rKxL3xvcMau9S9WSX_tqe2X95xT8xHtrhgPTbD80FvFbDEoQKHC0sHJ07FXtSuVSsXrDMsYQjT4-HboLgggbmaFpvvhdow3L1m9qU9nXiJyO-gn4sHK0soOmh9BqPg" -H "Content-Type: application/json"

echo.
echo.
echo Analysis Complete!
pause
