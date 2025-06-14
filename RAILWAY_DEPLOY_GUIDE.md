# 🚀 Railway 배포 가이드

## Docker 이미지 크기 최적화 결과

### 최적화 전 → 후
- **이전**: 6.7GB (제한 초과)
- **목표**: < 4.0GB (Railway 제한)
- **예상**: ~800MB - 1.5GB

## 🛠️ 최적화 적용 사항

### 1. 불필요한 파일 제외 (.dockerignore)
- Git 히스토리 (.git/)
- 가상환경 (venv/)
- 캐시 파일 (__pycache__/)
- 테스트 파일들
- 문서 파일들
- 개발용 스크립트들

### 2. 경량 베이스 이미지 사용
- `python:3.11-slim` → `python:3.11-alpine`
- Alpine Linux 기반으로 크기 대폭 감소

### 3. 최소한의 패키지만 설치
- 전체 requirements.txt (30+ 패키지) → requirements-production.txt (15개 핵심 패키지)
- ML 라이브러리 제거: sentence-transformers, spacy, nltk 등
- 개발 도구 제거: pytest, black, flake8, mypy 등
- Google Gemini API만 사용 (가장 경량)

### 4. Multi-stage Build (옵션)
- 빌드 단계와 실행 단계 분리
- 빌드 도구들이 최종 이미지에 포함되지 않음

## 📦 배포 방법

### 방법 1: Railway Dockerfile 사용 (권장)
```bash
# Railway에서 자동으로 Dockerfile.railway 사용하도록 설정
# railway.json 파일 생성 또는 Railway 대시보드에서 설정
```

### 방법 2: 로컬에서 이미지 빌드 후 배포
```bash
# 최적화된 이미지 빌드
docker build -f Dockerfile.railway -t ai-diary-backend:railway .

# 이미지 크기 확인
docker images ai-diary-backend:railway

# Railway에 배포 (Railway CLI 필요)
railway up
```

### 방법 3: GitHub 연동 배포
1. 코드를 GitHub에 push
2. Railway에서 GitHub 리포지토리 연결
3. `Dockerfile.railway` 파일을 `Dockerfile`로 이름 변경
4. 자동 배포 실행

## ⚠️ 주의사항

### 환경변수 설정
Railway 대시보드에서 다음 환경변수들을 설정해야 합니다:
```
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgres_url
REDIS_URL=your_redis_url (옵션)
SECRET_KEY=your_secret_key
```

### 기능 제한사항
최적화를 위해 제거된 기능들:
- ❌ Sentence Transformers (벡터 임베딩)
- ❌ SpaCy NLP (고급 자연어처리)
- ❌ NLTK (자연어처리)
- ❌ Firebase Admin (인증 단순화)
- ❌ 개발/테스트 도구들

### 유지된 핵심 기능들
- ✅ Google Gemini AI 분석
- ✅ FastAPI 웹 서버
- ✅ PostgreSQL 데이터베이스
- ✅ Redis 캐싱 (선택사항)
- ✅ 기본 인증 시스템
- ✅ 일기 분석 API

## 🔄 되돌리기 방법

만약 기능상 문제가 있다면:
1. `Dockerfile` 원본 사용: `cp Dockerfile.original Dockerfile`
2. `requirements.txt` 원본 사용
3. Railway Plan 업그레이드 (이미지 크기 제한 증가)

## 📊 예상 성능

### 빌드 시간
- 이전: 10-15분
- 최적화 후: 3-5분

### 메모리 사용량
- 이전: 2-3GB
- 최적화 후: 500MB-1GB

### 시작 시간
- 이전: 30-60초
- 최적화 후: 10-20초
