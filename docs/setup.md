# AI Diary Backend 설치 가이드

## 시스템 요구사항

### 최소 요구사항
- **Python**: 3.11 이상
- **메모리**: 2GB RAM
- **저장공간**: 5GB 이상
- **운영체제**: Ubuntu 20.04+, macOS 12+, Windows 10+

### 권장 요구사항
- **Python**: 3.11
- **메모리**: 4GB RAM
- **저장공간**: 10GB 이상
- **CPU**: 2코어 이상

## 사전 준비

### 1. Python 설치
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# macOS (Homebrew)
brew install python@3.11

# Windows
# Python.org에서 Python 3.11 다운로드 및 설치
```

### 2. PostgreSQL 설치
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Windows
# PostgreSQL 공식 사이트에서 설치 프로그램 다운로드
```

### 3. Redis 설치
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis
brew services start redis

# Windows
# Redis 공식 사이트에서 Windows용 Redis 다운로드
```

### 4. Git 설치
```bash
# Ubuntu/Debian
sudo apt install git

# macOS
xcode-select --install

# Windows
# Git 공식 사이트에서 Git for Windows 다운로드
```

## 프로젝트 설치

### 1. 저장소 클론
```bash
git clone https://github.com/your-repo/ai-diary-backend.git
cd ai-diary-backend
```

### 2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python3.11 -m venv venv

# 가상환경 활성화
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 데이터베이스 설정

### 1. PostgreSQL 데이터베이스 생성
```sql
-- PostgreSQL에 접속
sudo -u postgres psql

-- 데이터베이스 생성
CREATE DATABASE ai_diary_db;

-- 사용자 생성 및 권한 부여
CREATE USER ai_diary_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_diary_db TO ai_diary_user;

-- 연결 종료
\q
```

### 2. Redis 설정 확인
```bash
# Redis 서비스 상태 확인
redis-cli ping
# 응답: PONG
```

## 환경 변수 설정

### 1. 환경 변수 파일 생성
```bash
cp .env.example .env
```

### 2. .env 파일 편집
```bash
# 데이터베이스 설정
DATABASE_URL=postgresql+asyncpg://ai_diary_user:your_password@localhost/ai_diary_db
DATABASE_TEST_URL=postgresql+asyncpg://ai_diary_user:your_password@localhost/ai_diary_test_db

# Redis 설정
REDIS_URL=redis://localhost:6379/0

# Google AI API 키 설정
GEMINI_API_KEY=your_gemini_api_key_here

# Firebase 설정
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_private_key_here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_service_account@your_project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id

# JWT 설정
SECRET_KEY=your_super_secret_key_here_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 애플리케이션 설정
APP_NAME=AI Diary Analysis Backend
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development
```

## API 키 설정

### 1. Google Gemini API 키 발급
1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. "Create API Key" 클릭
3. 발급받은 API 키를 `.env` 파일의 `GEMINI_API_KEY`에 설정

### 2. Firebase 설정
1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. **Authentication** 설정:
   - Authentication > Sign-in method에서 이메일/비밀번호 활성화
3. **Service Account 키 생성**:
   - Project Settings > Service Accounts
   - "Generate new private key" 클릭
   - 다운로드한 JSON 파일의 내용을 `.env` 파일에 설정

## 데이터베이스 마이그레이션

### 1. Alembic 초기화 (이미 설정됨)
```bash
# 마이그레이션 파일 확인
ls alembic/versions/
```

### 2. 데이터베이스 마이그레이션 실행
```bash
alembic upgrade head
```

## 프로젝트 초기 설정

### 1. 초기 설정 스크립트 실행
```bash
python scripts/setup.py
```

이 스크립트는 다음 작업을 수행합니다:
- 환경 변수 검증
- 데이터베이스 연결 확인
- 테이블 생성
- 기본 데이터 설정

### 2. 설정 확인
스크립트가 성공적으로 완료되면 다음과 같은 메시지가 표시됩니다:
```
🎉 AI Diary Backend 초기 설정 완료!
```

## 서버 실행

### 1. 개발 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 서버 접속 확인
브라우저에서 다음 URL에 접속:
- **API 문서**: http://localhost:8000/docs
- **헬스체크**: http://localhost:8000/health
- **루트 엔드포인트**: http://localhost:8000

## Docker를 사용한 설치 (권장)

### 1. Docker 설치
- [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치

### 2. Docker Compose로 실행
```bash
# 환경 변수 파일 설정
cp .env.example .env
# .env 파일 편집

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 서비스 확인
```bash
# 컨테이너 상태 확인
docker-compose ps

# 서비스 접속 테스트
curl http://localhost:8000/health
```

## 테스트 실행

### 1. 전체 테스트 실행
```bash
python -m pytest
```

### 2. 커버리지와 함께 테스트
```bash
python -m pytest --cov=app --cov-report=html
```

### 3. 특정 테스트 실행
```bash
# API 테스트만 실행
python -m pytest app/tests/test_api/

# 서비스 테스트만 실행
python -m pytest app/tests/test_services/
```

## 개발 도구 설정

### 1. 코드 포맷팅
```bash
# Black으로 코드 포맷팅
black app/

# Flake8으로 린팅
flake8 app/

# MyPy로 타입 체크
mypy app/
```

### 2. pre-commit 훅 설정 (선택사항)
```bash
# pre-commit 설치
pip install pre-commit

# 훅 설치
pre-commit install

# 모든 파일에 훅 실행
pre-commit run --all-files
```

## IDE 설정

### VS Code
1. Python Extension 설치
2. `.vscode/settings.json` 설정:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

### PyCharm
1. Project Interpreter를 가상환경 Python으로 설정
2. Code style을 Black으로 설정
3. Test runner를 pytest로 설정

## 문제 해결

### 자주 발생하는 오류

#### 1. 모듈 import 오류
```bash
# 해결: PYTHONPATH 설정
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 또는 패키지 모드로 실행
python -m app.main
```

#### 2. 데이터베이스 연결 오류
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 서비스 시작
sudo systemctl start postgresql

# 연결 테스트
psql -h localhost -U ai_diary_user -d ai_diary_db
```

#### 3. Redis 연결 오류
```bash
# Redis 서비스 상태 확인
sudo systemctl status redis

# 서비스 시작
sudo systemctl start redis

# 연결 테스트
redis-cli ping
```

#### 4. 권한 오류
```bash
# Python 가상환경 권한 확인
ls -la venv/

# 디렉토리 권한 수정
chmod -R 755 venv/
```

### 로그 확인
```bash
# 애플리케이션 로그
tail -f logs/app.log

# 시스템 로그
journalctl -u your-service-name -f
```

## 성능 최적화

### 1. Python 설정
```bash
# Python 최적화 모드로 실행
python -O -m uvicorn app.main:app
```

### 2. 데이터베이스 최적화
```sql
-- PostgreSQL 설정 최적화
-- postgresql.conf 파일 편집
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
```

### 3. Redis 최적화
```bash
# Redis 설정 최적화
# redis.conf 파일 편집
maxmemory 512mb
maxmemory-policy allkeys-lru
```

## 보안 설정

### 1. 방화벽 설정
```bash
# Ubuntu UFW 설정
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 8000/tcp  # API 서버
sudo ufw enable
```

### 2. SSL 인증서 설정
```bash
# Let's Encrypt 인증서 발급
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
```

### 3. 환경 변수 보안
```bash
# .env 파일 권한 설정
chmod 600 .env

# Git에서 제외 확인
echo ".env" >> .gitignore
```

## 백업 설정

### 1. 데이터베이스 백업
```bash
# 자동 백업 스크립트 생성
cat > backup_db.sh << 'EOF'
#!/bin/bash
pg_dump -h localhost -U ai_diary_user ai_diary_db > backup_$(date +%Y%m%d_%H%M%S).sql
EOF

chmod +x backup_db.sh

# Cron 작업 등록
crontab -e
# 매일 2시에 백업
0 2 * * * /path/to/backup_db.sh
```

### 2. 코드 백업
```bash
# Git 원격 저장소 설정
git remote add origin https://github.com/your-repo/ai-diary-backend.git
git push -u origin main
```

## 다음 단계

설치가 완료되면:
1. [API 문서](api.md)를 참고하여 API 사용법 학습
2. [배포 가이드](deployment.md)를 참고하여 프로덕션 배포
3. 모니터링 및 로깅 시스템 구축
4. CI/CD 파이프라인 설정

## 지원

문제가 발생하면:
- GitHub Issues: https://github.com/your-repo/ai-diary-backend/issues
- 이메일: support@example.com
- 문서: https://docs.example.com
