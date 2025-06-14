# 🚀 AI 일기 분석 백엔드 서버 실행 가이드

## CORS 문제 해결 방법

### 방법 1: CORS 테스트 서버 실행 (권장)

CORS 문제를 완전히 해결한 간단한 테스트 서버입니다.

```bash
# 프로젝트 디렉토리로 이동
cd D:\ai-diary-backend

# CORS 테스트 서버 실행
python cors_test_server.py
```

### 방법 2: 메인 애플리케이션 실행

```bash
# 프로젝트 디렉토리로 이동
cd D:\ai-diary-backend

# 메인 앱 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 방법 3: Quick Start 서버 실행

```bash
# 프로젝트 디렉토리로 이동  
cd D:\ai-diary-backend

# Quick Start 서버 실행
python quick_start.py
```

## 테스트 방법

1. **서버 실행 후** 다음 중 하나로 테스트:
   
   - **브라우저**: http://localhost:8000/docs (Swagger UI)
   - **HTML 테스트**: `testweb.html` 파일을 브라우저에서 열기
   - **직접 요청**: curl 또는 Postman 사용

2. **testweb.html로 테스트하는 경우:**
   
   ```html
   파일을 브라우저에서 직접 열고
   "🧠 분석 API" 탭에서 일기 분석을 테스트하세요.
   ```

## CORS 에러 해결 상황

- ✅ **allow_origins: ["*"]** - 모든 origin 허용
- ✅ **allow_origin_regex: ".*"** - 정규식으로 모든 origin 허용  
- ✅ **allow_credentials: True** - 인증 정보 허용
- ✅ **allow_methods: ["*"]** - 모든 HTTP 메서드 허용
- ✅ **allow_headers: ["*"]** - 모든 헤더 허용

## 서버 실행 확인

서버가 제대로 실행되면 다음과 같은 메시지가 출력됩니다:

```
🚀 CORS 테스트 서버 시작...
🌐 모든 Origin에서 접근 가능하도록 설정됨
📝 브라우저에서 http://localhost:8000/docs 에서 API 문서 확인
🧪 testweb.html 파일로 테스트 가능
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 문제 해결

### 1. 포트 충돌 시
다른 포트로 실행:
```bash
python cors_test_server.py --port 8001
```

### 2. 패키지 설치 오류 시
```bash
pip install fastapi uvicorn pydantic
```

### 3. 여전히 CORS 에러 발생 시
- 서버가 실행 중인지 확인
- http://localhost:8000/health 로 서버 상태 확인
- 브라우저 개발자 도구에서 네트워크 탭 확인

## API 엔드포인트

### 주요 API:
- `GET /` - 루트 페이지
- `GET /health` - 서버 상태 확인
- `POST /api/v1/analysis/diary` - 일기 분석
- `GET /api/v1/analysis/history` - 분석 이력
- `POST /api/v1/auth/register` - 사용자 등록
- `POST /api/v1/auth/login` - 로그인

모든 API는 Mock 데이터로 동작하며, 실제 DB나 AI 모델 없이도 테스트 가능합니다.
