# AI Diary Backend 배포 가이드

## 배포 환경

### 지원하는 배포 플랫폼
- **Google Cloud Run** (권장)
- **AWS ECS/Fargate**
- **Azure Container Instances**
- **Docker Swarm**
- **Kubernetes**
- **일반 VPS/서버**

## 사전 준비

### 1. 필수 계정 및 서비스
- Google Cloud Platform 계정 (Cloud Run 사용 시)
- Firebase 프로젝트
- Google AI Studio API 키
- Docker Hub 계정 (선택사항)

### 2. 도메인 및 SSL
- 도메인 등록 및 DNS 설정
- SSL 인증서 (Let's Encrypt 권장)

### 3. 데이터베이스
- **Google Cloud SQL** (PostgreSQL)
- **Amazon RDS**
- **Azure Database for PostgreSQL**
- **자체 관리 PostgreSQL**

## Google Cloud Run 배포 (권장)

### 1. 사전 설정

#### Google Cloud CLI 설치
```bash
# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# macOS
brew install --cask google-cloud-sdk

# Windows
# Google Cloud CLI 설치 프로그램 다운로드
```

#### 프로젝트 설정
```bash
# Google Cloud 로그인
gcloud auth login

# 프로젝트 생성
gcloud projects create ai-diary-backend --name="AI Diary Backend"

# 프로젝트 설정
gcloud config set project ai-diary-backend

# 필요한 API 활성화
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sql-component.googleapis.com \
    secretmanager.googleapis.com
```

### 2. 데이터베이스 설정

#### Cloud SQL PostgreSQL 인스턴스 생성
```bash
# PostgreSQL 인스턴스 생성
gcloud sql instances create ai-diary-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=asia-northeast1

# 데이터베이스 생성
gcloud sql databases create ai_diary_prod \
    --instance=ai-diary-db

# 사용자 생성
gcloud sql users create ai_diary_user \
    --instance=ai-diary-db \
    --password=your_secure_password
```

#### Redis 인스턴스 생성 (Memorystore)
```bash
# Redis 인스턴스 생성
gcloud redis instances create ai-diary-redis \
    --size=1 \
    --region=asia-northeast1 \
    --redis-version=redis_7_0
```

### 3. 시크릿 관리

#### Secret Manager에 환경 변수 저장
```bash
# 데이터베이스 URL
echo "postgresql+asyncpg://ai_diary_user:your_password@/ai_diary_prod?host=/cloudsql/ai-diary-backend:asia-northeast1:ai-diary-db" | \
    gcloud secrets create database-url --data-file=-

# Gemini API 키
echo "your_gemini_api_key" | \
    gcloud secrets create gemini-api-key --data-file=-

# JWT Secret Key
echo "your_jwt_secret_key" | \
    gcloud secrets create jwt-secret-key --data-file=-

# Firebase 설정
cat firebase-service-account.json | \
    gcloud secrets create firebase-config --data-file=-
```

### 4. Docker 이미지 빌드 및 배포

#### 배포 스크립트 사용
```bash
# 프로덕션 환경으로 배포
python scripts/deploy.py --env production

# 또는 수동 배포
```

#### 수동 배포 과정
```bash
# Docker 이미지 빌드
docker build -t gcr.io/ai-diary-backend/ai-diary-api .

# 이미지 푸시
docker push gcr.io/ai-diary-backend/ai-diary-api

# Cloud Run 서비스 배포
gcloud run deploy ai-diary-api \
    --image gcr.io/ai-diary-backend/ai-diary-api \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-secrets="DATABASE_URL=database-url:latest,GEMINI_API_KEY=gemini-api-key:latest,SECRET_KEY=jwt-secret-key:latest" \
    --set-env-vars="ENVIRONMENT=production,APP_NAME=AI Diary Backend" \
    --add-cloudsql-instances=ai-diary-backend:asia-northeast1:ai-diary-db
```

### 5. 도메인 설정

#### 커스텀 도메인 매핑
```bash
# 도메인 매핑
gcloud run domain-mappings create \
    --service ai-diary-api \
    --domain api.yourdomain.com \
    --region asia-northeast1
```

#### DNS 설정
```
# A 레코드 또는 CNAME 설정
api.yourdomain.com -> Cloud Run에서 제공하는 주소
```

### 6. 모니터링 설정

#### Cloud Logging 설정
```bash
# 로그 확인
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ai-diary-api"

# 로그 기반 메트릭 생성
gcloud logging metrics create error_rate \
    --description="API Error Rate" \
    --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'
```

#### Cloud Monitoring 알림
```bash
# 알림 정책 생성 (JSON 파일로 설정)
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.json
```

## AWS ECS 배포

### 1. 사전 설정

#### AWS CLI 설치 및 설정
```bash
# AWS CLI 설치
pip install awscli

# 자격 증명 설정
aws configure
```

#### ECS 클러스터 생성
```bash
# ECS 클러스터 생성
aws ecs create-cluster --cluster-name ai-diary-cluster
```

### 2. RDS 데이터베이스 설정

```bash
# RDS PostgreSQL 인스턴스 생성
aws rds create-db-instance \
    --db-instance-identifier ai-diary-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15 \
    --master-username ai_diary_user \
    --master-user-password your_secure_password \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name default
```

### 3. ECR에 이미지 푸시

```bash
# ECR 레포지토리 생성
aws ecr create-repository --repository-name ai-diary-backend

# Docker 이미지 태그 및 푸시
docker tag ai-diary-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ai-diary-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ai-diary-backend:latest
```

### 4. ECS 서비스 배포

#### 태스크 정의 생성 (task-definition.json)
```json
{
  "family": "ai-diary-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "ai-diary-container",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/ai-diary-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:<region>:<account-id>:secret:database-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-diary",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 서비스 생성
```bash
# 태스크 정의 등록
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 서비스 생성
aws ecs create-service \
    --cluster ai-diary-cluster \
    --service-name ai-diary-service \
    --task-definition ai-diary-task:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxx],securityGroups=[sg-xxxxxx],assignPublicIp=ENABLED}"
```

## Docker Compose 배포 (단일 서버)

### 1. 서버 준비

#### VPS/서버 설정
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 프로젝트 복사
git clone https://github.com/your-repo/ai-diary-backend.git
cd ai-diary-backend
```

### 2. 프로덕션 Docker Compose 설정

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_diary_db
      POSTGRES_USER: ai_diary_user
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3. Nginx 설정

#### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://app/health;
            access_log off;
        }
    }
}
```

### 4. SSL 인증서 설정

```bash
# Certbot 설치
sudo apt install certbot

# SSL 인증서 발급
sudo certbot certonly --webroot -w /var/www/html -d api.yourdomain.com

# 인증서 자동 갱신 설정
sudo crontab -e
# 매월 1일 2시에 갱신 시도
0 2 1 * * certbot renew --quiet
```

### 5. 배포 실행

```bash
# 환경 변수 설정
cp .env.example .env.production
# .env.production 파일 편집

# 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

## 배포 후 설정

### 1. 헬스체크 설정

#### 헬스체크 스크립트
```bash
#!/bin/bash
# health_check.sh

API_URL="https://api.yourdomain.com"
HEALTH_ENDPOINT="$API_URL/health"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_ENDPOINT)

if [ $response = 200 ]; then
    echo "API is healthy"
    exit 0
else
    echo "API is not responding correctly. Status: $response"
    exit 1
fi
```

### 2. 모니터링 설정

#### Prometheus + Grafana (선택사항)
```yaml
# monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### 3. 백업 설정

#### 자동 백업 스크립트
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 데이터베이스 백업
docker exec ai-diary-backend_db_1 pg_dump -U ai_diary_user ai_diary_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# 파일 압축
gzip "$BACKUP_DIR/db_backup_$DATE.sql"

# 30일 이상된 백업 파일 삭제
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

#### Cron 작업 설정
```bash
# 매일 2시에 백업
0 2 * * * /opt/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### 4. 로그 관리

#### Logrotate 설정
```bash
# /etc/logrotate.d/ai-diary-backend
/path/to/ai-diary-backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /path/to/ai-diary-backend/docker-compose.prod.yml restart app
    endscript
}
```

## 성능 최적화

### 1. 애플리케이션 최적화

#### Gunicorn 설정 (선택사항)
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### 2. 데이터베이스 최적화

#### PostgreSQL 설정
```sql
-- postgresql.conf 최적화
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

### 3. 캐싱 전략

#### Redis 설정 최적화
```
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 보안 설정

### 1. 방화벽 설정

```bash
# UFW 방화벽 설정
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. 실패한 로그인 차단

```bash
# Fail2ban 설치 및 설정
sudo apt install fail2ban

# 설정 파일 생성
sudo cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. SSL 보안 강화

```nginx
# nginx SSL 설정 강화
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
add_header Strict-Transport-Security "max-age=63072000" always;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
```

## 롤백 전략

### 1. Blue-Green 배포

```bash
# 새 버전 배포 (Green)
docker-compose -f docker-compose.green.yml up -d

# 헬스체크
./health_check.sh green

# 트래픽 전환
# Load Balancer 설정 변경

# 이전 버전 정리 (Blue)
docker-compose -f docker-compose.blue.yml down
```

### 2. 데이터베이스 마이그레이션 롤백

```bash
# 현재 마이그레이션 상태 확인
alembic current

# 이전 리비전으로 롤백
alembic downgrade -1

# 특정 리비전으로 롤백
alembic downgrade <revision_id>
```

## 문제 해결

### 1. 일반적인 배포 문제

#### 메모리 부족
```bash
# 메모리 사용량 확인
docker stats

# 스왑 메모리 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 디스크 공간 부족
```bash
# 사용하지 않는 Docker 이미지 정리
docker system prune -a

# 로그 파일 정리
sudo journalctl --vacuum-time=7d
```

### 2. 네트워크 문제

```bash
# 포트 확인
sudo netstat -tlnp | grep :8000

# DNS 설정 확인
nslookup api.yourdomain.com

# 방화벽 규칙 확인
sudo ufw status
```

### 3. 성능 문제

```bash
# CPU 사용률 확인
top

# 메모리 사용률 확인
free -h

# 디스크 I/O 확인
iostat -x 1
```

## 모니터링 및 알림

### 1. 업타임 모니터링

```bash
# 간단한 업타임 모니터 스크립트
#!/bin/bash
# uptime_monitor.sh

URL="https://api.yourdomain.com/health"
EMAIL="admin@yourdomain.com"

if ! curl -f -s $URL > /dev/null; then
    echo "API is down!" | mail -s "API Alert" $EMAIL
fi
```

### 2. 로그 모니터링

```bash
# 에러 로그 모니터링
#!/bin/bash
# error_monitor.sh

LOG_FILE="/path/to/logs/app.log"
ERROR_COUNT=$(grep -c "ERROR" $LOG_FILE | tail -1)

if [ $ERROR_COUNT -gt 10 ]; then
    echo "High error rate detected: $ERROR_COUNT errors" | mail -s "Error Alert" admin@yourdomain.com
fi
```

## 다음 단계

배포 완료 후:
1. 모니터링 대시보드 설정
2. 알림 시스템 구축  
3. CI/CD 파이프라인 구축
4. 성능 테스트 및 최적화
5. 보안 감사 수행

배포에 대한 추가 지원이 필요하면 [지원 문서](setup.md)를 참고하거나 문의해 주세요.
