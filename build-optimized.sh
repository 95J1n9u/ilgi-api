#!/bin/bash

# Docker 이미지 크기 최적화 빌드 스크립트

echo "🚀 최적화된 Docker 이미지 빌드 시작..."

# 기존 이미지 정리
echo "📦 기존 이미지 정리..."
docker system prune -f

# 최적화된 이미지 빌드
echo "🔨 최적화된 이미지 빌드..."
docker build -f Dockerfile.optimized -t ai-diary-backend:optimized .

# 이미지 크기 확인
echo "📊 이미지 크기 확인..."
docker images ai-diary-backend:optimized

echo "✅ 빌드 완료!"
echo "🚀 Railway 배포 명령어:"
echo "   docker tag ai-diary-backend:optimized your-registry/ai-diary-backend:latest"
echo "   docker push your-registry/ai-diary-backend:latest"
