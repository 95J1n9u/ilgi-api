# AI 일기 분석 백엔드 - 최적화된 Docker 이미지 (slim 최적화 버전)
# Flutter 앱 연동 및 프로덕션 배포용

# ============================
# 빌드 스테이지
# ============================
FROM python:3.11-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 빌드에 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libpq-dev \
    && pip install --upgrade pip

# requirements 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================
# 런타임 스테이지
# ============================
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 런타임에 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 유저 및 그룹 생성 (보안 목적)
RUN groupadd -g 1001 appgroup && useradd -u 1001 -g appgroup appuser

# 빌더에서 패키지 복사
COPY --from=builder /install /usr/local

# 애플리케이션 코드 복사
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini .
COPY --chown=appuser:appgroup .env* ./

# 환경변수 설정
ENV PATH=/usr/local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 권한 설정
RUN chown -R appuser:appgroup /app

# 비특권 사용자로 실행
USER appuser

# 포트 노출 (Railway는 $PORT 환경변수, 일반적으로는 8000)
EXPOSE ${PORT:-8000}

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-8000}/health', timeout=5)" || exit 1

# 애플리케이션 실행
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]

# 이미지 정보
LABEL maintainer="AI Diary Backend Team"
LABEL description="AI 일기 분석 백엔드 서버 - Flutter 앱 연동"
LABEL version="1.0.0"
