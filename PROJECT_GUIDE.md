# AI 일기 분석 백엔드 서버 개발 가이드

## 📋 프로젝트 개요

**AI 일기 분석 백엔드 서버**는 사용자 일기 데이터를 AI로 분석하여 감정, 성격, 생활 패턴을 추출하고, 이를 바탕으로 매칭 추천 데이터를 제공하는 API 서버입니다. Flutter 앱과 연동되며, 핵심은 **자연어처리 기반 감정/성격 분석 + 매칭 벡터화**입니다.

## 🚀 핵심 기술 스택

| 분야 | 기술 |
|------|------|
| **백엔드** | Python 3.11+, FastAPI |
| **AI 분석** | Google Gemini API, NLTK, spaCy, Sentence Transformers |
| **데이터베이스** | PostgreSQL, Redis |
| **인프라** | Docker, Google Cloud Run |
| **ORM** | SQLAlchemy 2.0, Alembic |
| **인증** | Firebase Authentication |
| **테스트** | pytest, pytest-asyncio |
| **CORS** | 모든 origin 허용 (개발환경), 제한적 허용 (프로덕션) |

## 🛠 작업 기본 원칙

| 구분 | 규칙 |
|------|------|
| **언어/프레임워크** | Python 3.11 / FastAPI |
| **프로젝트 구조** | `app/` 하위에 API, 서비스, 모델, 스키마, 유틸 분리 |
| **비즈니스 로직** | 반드시 `services/`에 작성 |
| **모델 & 스키마** | DB 모델: `models/`, Pydantic 스키마: `schemas/` |
| **DB 마이그레이션** | Alembic 사용 (`alembic revision --autogenerate`) |
| **AI 호출** | `services/ai_service.py`에서 Gemini 호출 통합 |
| **프롬프트 관리** | 각 서비스 클래스 메서드 내부에서 관리 |
| **벡터 생성** | `services/matching_service.py`의 `create_user_vector()` |
| **API 명세** | `/docs/API_SPECIFICATION.md` 참고 |
| **환경 설정** | `.env` 파일 사용, 코드에 하드코딩 금지 |
| **테스트** | pytest 기반 단위 테스트 작성 (`tests/`) |

## 📂 프로젝트 디렉토리 구조

```
app/
├── api/
│   ├── deps.py              # 의존성 주입
│   └── v1/
│       ├── auth.py          # 인증 API
│       ├── analysis.py      # AI 분석 API  
│       ├── matching.py      # 매칭 API
│       └── router.py        # 라우터 통합
├── services/
│   ├── ai_service.py        # 통합 AI 분석 서비스
│   ├── emotion_service.py   # 감정 분석 서비스
│   ├── personality_service.py # 성격 분석 서비스
│   └── matching_service.py  # 매칭 서비스 (벡터 생성 포함)
├── models/
│   ├── user.py             # 사용자 SQLAlchemy 모델
│   ├── diary.py            # 일기 SQLAlchemy 모델
│   └── analysis.py         # 분석 결과 SQLAlchemy 모델
├── schemas/
│   ├── user.py             # 사용자 Pydantic 스키마
│   ├── diary.py            # 일기 Pydantic 스키마
│   ├── analysis.py         # 분석 결과 Pydantic 스키마
│   └── matching.py         # 매칭 Pydantic 스키마
├── core/
│   ├── security.py         # 인증, 보안
│   ├── middleware.py       # 미들웨어
│   └── exceptions.py       # 예외 처리
├── config/
│   ├── settings.py         # 환경 설정
│   └── database.py         # DB 연결 설정
├── utils/
│   ├── helpers.py          # 헬퍼 함수
│   └── validators.py       # 데이터 검증
└── tests/
    ├── test_api/           # API 테스트
    ├── test_services/      # 서비스 테스트
    └── conftest.py         # 테스트 설정
```

## ⚙ 작업 흐름

### 1️⃣ 개발 워크플로우
**이슈 등록 → 브랜치 생성 → 작업 → PR → 코드리뷰 → Merge**

### 2️⃣ 신규 기능 작업시
- **API 엔드포인트** → `api/v1/`
- **DB 모델** → `models/`
- **비즈니스 로직** → `services/`
- **API 스키마** → `schemas/`
- **테스트** → `tests/`

### 3️⃣ AI 분석 작업시
```python
# 감정 분석
services/emotion_service.py
├── _analyze_with_gemini()     # Gemini API 호출
├── _validate_gemini_result()  # 결과 검증
└── analyze_emotions()         # 메인 분석 로직

# 성격 분석  
services/personality_service.py
├── _analyze_single_text()     # 단일 텍스트 분석
├── _predict_mbti_type()       # MBTI 예측
└── analyze_personality()      # 메인 분석 로직

# 통합 AI 서비스
services/ai_service.py
└── analyze_diary()            # 전체 분석 통합
```

### 4️⃣ 벡터 생성/매칭 작업시
```python
# 매칭 서비스
services/matching_service.py
├── create_user_vector()           # 사용자 벡터 생성
├── _calculate_compatibility_score() # 호환성 점수 계산
└── find_matching_candidates()     # 매칭 후보 검색
```

### 5️⃣ DB 마이그레이션 작업시
```bash
# 모델 변경 후 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1
```

### 6️⃣ 테스트 작성
```python
# API 테스트 예시
tests/test_api/test_analysis.py
└── test_analyze_diary_success()

# 서비스 테스트 예시  
tests/test_services/test_emotion_service.py
└── test_analyze_emotions_success()
```

## 🔐 보안 기본 원칙

### 인증 & 인가
- 모든 API → **Firebase Token 검증** 필수
- 사용자별 데이터 접근 → **본인 확인** 후 처리
- 관리자 기능 → **권한 체크** 필수

### 데이터 보안
- 외부 입력 → **validators.py에서 검증** 후 처리
- 민감 데이터 → **암호화/익명화** 후 저장
- 일기 내용 → **개인정보 마스킹** 처리

### 설정 관리
- **코드 내 하드코딩 금지** → `.env` 파일 관리
- 환경별 설정 파일:
  - 개발: `.env`
  - 프로덕션: `.env.production`  
  - 테스트: `.env.test`

### API 보안
- **Rate Limiting** (100 req/min per user)
- **Input Validation & Sanitization**
- **SQL Injection 방지**
- **CORS 설정**

## 🧪 테스트 전략

### 단위 테스트
```bash
# 전체 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app

# 특정 모듈 테스트
pytest tests/test_services/test_emotion_service.py
```

### 통합 테스트
```python
# API 엔드포인트 테스트
test_client.post("/api/v1/analysis/diary", json=data)

# 데이터베이스 통합 테스트
async with test_db as session:
    # DB 테스트 로직
```

## 🚀 배포 전략

### 개발 환경
```bash
# Docker Compose 사용
docker-compose up -d

# 또는 로컬 실행
uvicorn app.main:app --reload
```

### 프로덕션 환경
```bash
# Google Cloud Run 배포
python scripts/deploy.py --env production

# 또는 Docker 이미지 빌드
docker build -t ai-diary-backend .
```

## 📊 모니터링 & 로깅

### 주요 메트릭
- API 응답 시간 (< 2초 목표)
- Gemini API 호출 성공률 (> 99%)
- 일일 분석 처리량
- 사용자별 분석 정확도

### 로깅 전략
```python
import structlog
logger = structlog.get_logger()

# 요청 로깅
logger.info("analysis_started", user_id=user_id, diary_id=diary_id)

# 에러 로깅  
logger.error("analysis_failed", error=str(e), user_id=user_id)
```

## 🔄 버전 관리

### API 버전
- 현재 버전: **v1** (`/api/v1/`)
- 하위 호환성 유지
- 새 기능 → 버전 업그레이드 고려

### DB 스키마 버전
- Alembic으로 마이그레이션 관리
- 롤백 가능한 마이그레이션 작성
- 프로덕션 배포 전 테스트 필수

## 📚 참고 문서

- [API 명세서](docs/API_SPECIFICATION.md) ⭐ **새로 추가!**
- [API 문서 (Legacy)](docs/api.md)
- [설치 가이드](docs/setup.md)
- [배포 가이드](docs/deployment.md)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Google Gemini API 문서](https://ai.google.dev/docs)

---

## 🎯 개발 체크리스트

### 새 기능 개발시
- [ ] 이슈 생성 및 브랜치 생성
- [ ] API 엔드포인트 구현
- [ ] 비즈니스 로직 구현 (services/)
- [ ] DB 모델 및 스키마 정의
- [ ] 유효성 검증 로직 추가
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] API 문서 업데이트
- [ ] 코드 리뷰 요청
- [ ] 배포 테스트

### 배포 전 체크리스트
- [ ] 모든 테스트 통과
- [ ] 환경 변수 설정 확인
- [ ] DB 마이그레이션 테스트
- [ ] 성능 테스트 수행
- [ ] 보안 취약점 검사
- [ ] 로그 및 모니터링 설정
- [ ] 롤백 계획 수립

## 🚪 CORS 문제 해결 가이드

### 문제 상황
개발 중 HTML 파일에서 직접 API를 호출할 때 CORS 에러 발생:
```
Access to fetch at 'http://localhost:8000/api/v1/analysis/diary' from origin 'null' has been blocked by CORS policy
```

### ✅ 해결 완료!
다음 문제들이 모두 해결되었습니다:
- **CORS 에러**: 모든 origin 허용 (파일 시스템 포함)
- **Gemini API 모델 에러**: `gemini-pro` → `gemini-1.5-flash` 업데이트
- **SQLAlchemy 관계 에러**: Foreign Key 제약조건 추가

### 🔧 해결된 사항들

#### 1️⃣ Gemini API 모델 업데이트
```python
# 이전 (404 에러 발생)
self.model = genai.GenerativeModel('gemini-pro')

# 수정 후 (정상 작동)
self.model = genai.GenerativeModel('gemini-1.5-flash')
```

#### 2️⃣ SQLAlchemy Foreign Key 추가
```python
# UserVector, MatchingPreference, UserPersonalitySummary 등
user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True, index=True)
```

#### 3️⃣ CORS 설정 강화
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=".*",  # 파일 시스템 지원
)
```

### 🚀 실행 방법

#### 방법 1: 완전 수정된 테스트 서버 (권장)
```bash
cd D:\ai-diary-backend
python fixed_test_server.py
```

#### 방법 2: 수정된 메인 애플리케이션
```bash
cd D:\ai-diary-backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 방법 3: CORS 테스트 서버
```bash
cd D:\ai-diary-backend
python cors_test_server.py
```

#### 방법 4: Quick Start 서버
```bash
cd D:\ai-diary-backend
python quick_start.py
```

### 테스트 방법
1. **서버 실행 후**:
   - Swagger UI: http://localhost:8000/docs
   - 테스트 HTML: `testweb.html` 파일 열기
   - 직접 요청: curl 또는 Postman

2. **서버 상태 확인**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **CORS 테스트**:
   ```bash
   curl -X OPTIONS http://localhost:8000/api/v1/analysis/diary \
   -H "Origin: null" \
   -H "Access-Control-Request-Method: POST"
   ```

### 문제 해결 체크리스트
- [ ] 서버가 정상 실행 중인가?
- [ ] `DEBUG=True` 설정되어 있는가?
- [ ] CORS 미들웨어가 올바르게 설정되어 있는가?
- [ ] 브라우저에서 OPTIONS 요청이 성공하는가?
- [ ] 네트워크 탭에서 에러 메시지 확인

---

이 가이드를 따라 개발하시면 안정적이고 확장 가능한 AI 일기 분석 백엔드 시스템을 구축할 수 있습니다! 🚀
