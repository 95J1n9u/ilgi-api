-- AI Diary Backend 데이터베이스 설정

-- 사용자 생성 (비밀번호: !rkdwlsrn713)
CREATE USER ai_diary_user WITH PASSWORD '!rkdwlsrn713';

-- 데이터베이스 생성
CREATE DATABASE ai_diary_db OWNER ai_diary_user;
CREATE DATABASE ai_diary_test_db OWNER ai_diary_user;

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE ai_diary_db TO ai_diary_user;
GRANT ALL PRIVILEGES ON DATABASE ai_diary_test_db TO ai_diary_user;

-- 추가 권한 (스키마 생성 등)
ALTER USER ai_diary_user CREATEDB;

\echo 'AI Diary 데이터베이스 설정 완료!'
