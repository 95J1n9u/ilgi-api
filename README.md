# 🤖 AI 일기 분석 백엔드 서버

Flutter 앱의 일기 데이터를 받아 AI로 분석하여 감정, 성격, 행동 패턴을 추출하고 매칭을 위한 데이터를 제공하는 백엔드 API 서버입니다.

## 🚀 주요 기능

- **일기 텍스트 분석**: Gemini API를 활용한 자연어 처리
- **감정 분석**: 12가지+ 감정 분류 및 감정 점수 계산
- **성격 분석**: MBTI, Big5 성격 특성 추출
- **패턴 분석**: 생활 패턴, 관심사, 가치관 도출
- **매칭 데이터**: 호환성 계산을 위한 벡터 생성

## 🛠️ 기술 스택

- **백엔드**: FastAPI 0.104+, Python 3.11+
- **데이터베이스**: PostgreSQL 15+, Redis 7+
- **AI/ML**: Google Gemini Pro API, Sentence-Transformers
- **인증**: Firebase Authentication
- **배포**: Docker, Google Cloud Run

## 📋 프로젝트 구조

```
ai-diary-backend/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config/                 # 환경 설정
│   ├── api/v1/                # API 라우터
│   ├── core/                  # 보안, 미들웨어
│   ├── models/                # SQLAlchemy 모델
│   ├── schemas/               # Pydantic 스키마
│   ├── services/              # 비즈니스 로직
│   ├── utils/                 # 유틸리티
│   └── tests/                 # 테스트
├── scripts/                   # 스크립트
├── docs/                      # 문서
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd ai-diary-backend
```

### 2. 환경 설정
```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 편집하여 필요한 값들 입력
# - DATABASE_URL
# - GEMINI_API_KEY
# - FIREBASE 설정 등
```

### 3. Docker로 실행
```bash
# 전체 스택 실행
docker-compose up -d

# 또는 개발 모드로 실행
docker-compose up --build
```

### 4. 로컬 개발 환경 설정 (선택사항)
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

## 📡 API 엔드포인트

### 인증
- `POST /api/v1/auth/verify-token` - Firebase 토큰 검증
- `POST /api/v1/auth/refresh` - 토큰 갱신

### AI 분석
- `POST /api/v1/analysis/diary` - 일기 분석 요청
- `GET /api/v1/analysis/{diary_id}` - 분석 결과 조회
- `POST /api/v1/analysis/batch` - 일괄 분석

### 사용자 데이터
- `GET /api/v1/users/{user_id}/personality` - 성격 분석 결과
- `GET /api/v1/users/{user_id}/emotions` - 감정 패턴
- `GET /api/v1/users/{user_id}/insights` - 종합 인사이트

### 매칭
- `POST /api/v1/matching/candidates` - 매칭 후보 추천
- `POST /api/v1/matching/compatibility` - 호환성 점수 계산

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app

# 특정 테스트 파일 실행
pytest app/tests/test_api/test_analysis.py
```

## 📊 모니터링

서버 실행 후 다음 URL에서 확인할 수 있습니다:

- **API 문서**: http://localhost:8000/docs
- **Alternative API 문서**: http://localhost:8000/redoc
- **헬스체크**: http://localhost:8000/health
- **메트릭**: http://localhost:8000/metrics

## 🔧 개발 도구

```bash
# 코드 포맷팅
black app/

# 린팅
flake8 app/

# 타입 체크
mypy app/
```

## 📚 추가 문서

- [API 문서](docs/api.md)
- [설치 가이드](docs/setup.md)
- [배포 가이드](docs/deployment.md)

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.
