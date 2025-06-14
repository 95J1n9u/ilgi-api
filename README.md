# 🤖 AI 일기 분석 백엔드

Flutter 앱과 연동 가능한 AI 일기 분석 백엔드 서버입니다. Google Gemini API를 사용하여 일기 내용을 분석하고 감정, 성격, 생활 패턴을 추출합니다.

## ✨ 주요 기능

- 🧠 **AI 일기 분석**: Google Gemini를 사용한 감정 및 성격 분석
- 📱 **Flutter 앱 연동**: CORS 설정 및 모바일 앱 지원
- 🔥 **Firebase 인증**: 조건부 Firebase 인증 시스템
- 🗄️ **PostgreSQL**: 분석 결과 영구 저장
- 🔴 **Redis 캐싱**: 성능 최적화 (선택사항)
- 📊 **실시간 API**: RESTful API 엔드포인트
- 🚀 **Railway 배포**: 최적화된 Docker 이미지

## 🏗️ 기술 스택

| 분야 | 기술 |
|------|------|
| **백엔드** | Python 3.11, FastAPI |
| **AI 분석** | Google Gemini API |
| **데이터베이스** | PostgreSQL, Redis |
| **인증** | Firebase Authentication (조건부) |
| **ORM** | SQLAlchemy 2.0, Alembic |
| **배포** | Docker, Railway |

## 🚀 빠른 시작

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd ai-diary-backend
```

### 2. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 설정:

```bash
# 필수 설정
GEMINI_API_KEY=your_google_gemini_api_key
SECRET_KEY=your_super_secret_jwt_key

# 환경 설정
DEBUG=true
ENVIRONMENT=development

# Firebase 설정 (선택사항 - 없으면 자동으로 비활성화)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_service_account@your_project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id

# 데이터베이스 설정 (선택사항)
DATABASE_URL=postgresql://username:password@localhost:5432/ai_diary
REDIS_URL=redis://localhost:6379/0
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 서버 실행
```bash
# 개발 모드
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 직접 실행
python app/main.py
```

### 5. API 문서 확인
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **헬스체크**: http://localhost:8000/health

## 📱 Flutter 앱 연동

### 연결 테스트
```dart
// Flutter에서 백엔드 연결 테스트
final response = await http.get(
  Uri.parse('http://localhost:8000/api/v1/flutter/test'),
);
```

### 주요 API 엔드포인트
```bash
# 기본 정보
GET  /                          # 서버 정보
GET  /health                    # 헬스체크
GET  /api/v1/status            # API 상태

# Flutter 전용
GET  /api/v1/flutter/test      # 연결 테스트

# 인증 (Firebase 활성화시)
POST /api/v1/auth/register     # 사용자 등록
POST /api/v1/auth/login        # 로그인

# 일기 분석
POST /api/v1/analysis/diary    # 일기 분석 요청
GET  /api/v1/analysis/history  # 분석 이력

# 매칭
POST /api/v1/matching/find     # 사용자 매칭
```

## 🐳 Docker 배포

### 로컬 Docker 실행
```bash
# 이미지 빌드
docker build -t ai-diary-backend .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env ai-diary-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## 🚂 Railway 배포

### 필수 환경변수 설정
Railway 대시보드에서 다음 환경변수를 설정:

```bash
# 필수
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key

# 권장
ENVIRONMENT=production
DEBUG=false
```

### 배포 방법
1. **GitHub 연동**: 코드를 GitHub에 push 후 Railway에서 자동 배포
2. **Railway CLI**: `railway up` 명령어로 직접 배포

최적화된 Docker 이미지로 **6.7GB → <1.5GB** (80% 감소) 달성!

## 🔧 개발 가이드

### 프로젝트 구조
```
app/
├── main.py              # 메인 애플리케이션 (Flask와 연동)
├── api/v1/             # API 라우터들
├── config/             # 설정 파일들
├── core/               # 핵심 기능 (미들웨어, 보안)
├── models/             # SQLAlchemy 모델들
├── schemas/            # Pydantic 스키마들
├── services/           # 비즈니스 로직 (AI 분석)
└── utils/              # 유틸리티 함수들
```

### 새 기능 추가
1. **API 엔드포인트**: `api/v1/` 디렉토리에 추가
2. **비즈니스 로직**: `services/` 디렉토리에 추가
3. **DB 모델**: `models/` 디렉토리에 추가
4. **스키마**: `schemas/` 디렉토리에 추가

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head
```

## 🎯 특징

### 🔄 환경별 자동 설정
- **개발환경**: 모든 CORS 허용, 디버그 모드
- **프로덕션**: 제한된 CORS, 보안 강화
- **Railway**: 자동 포트 감지, 최소 환경변수

### 🔥 Firebase 조건부 활성화
- Firebase 설정이 있으면 자동 활성화
- 설정이 없으면 자동으로 비활성화 (Railway 배포 최적화)

### 📱 Flutter 앱 완벽 지원
- Capacitor, Ionic 앱 지원
- 모바일 친화적 CORS 설정
- 전용 테스트 엔드포인트 제공

### 🚀 최적화된 배포
- 16개 핵심 패키지만 사용 (기존 30+개에서 50% 감소)
- Multi-stage Docker 빌드로 크기 최적화
- 불필요한 ML 라이브러리 제거로 빌드 시간 단축

## 📊 성능

| 지표 | 최적화 전 | 최적화 후 | 개선율 |
|------|-----------|-----------|--------|
| Docker 이미지 | 6.7GB | <1.5GB | 80%↓ |
| 빌드 시간 | 10-15분 | 3-5분 | 70%↓ |
| 메모리 사용량 | 2-3GB | 500MB-1GB | 70%↓ |
| 패키지 수 | 30+ | 16개 | 50%↓ |

## 🔧 문제 해결

### 자주 묻는 질문

**Q: Firebase 없이 사용할 수 있나요?**
A: 네! Firebase 환경변수가 없으면 자동으로 비활성화됩니다.

**Q: Railway 배포시 헬스체크가 실패해요.**
A: `GEMINI_API_KEY`와 `SECRET_KEY` 환경변수가 설정되었는지 확인하세요.

**Q: Flutter 앱에서 CORS 에러가 발생해요.**
A: `DEBUG=true`로 설정하거나 `ALLOWED_ORIGINS`에 앱 도메인을 추가하세요.

### 로그 확인
```bash
# 개발 모드에서 상세 로그 확인
DEBUG=true python app/main.py
```

## 📚 추가 문서

- [프로젝트 가이드](PROJECT_GUIDE.md) - 상세 개발 가이드
- [정리 가이드](PROJECT_CLEANUP_GUIDE.md) - 불필요한 파일 정리 방법
- [API 문서](http://localhost:8000/docs) - 실시간 API 문서

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

This project is licensed under the MIT License.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요.

---

**이제 Flutter 앱과 완벽하게 연동되는 최적화된 AI 일기 분석 백엔드를 사용할 수 있습니다!** 🎉
