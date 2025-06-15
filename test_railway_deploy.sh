#!/bin/bash

# AI Diary Backend - Railway 배포 후 테스트 스크립트

echo "🚀 AI Diary Backend Railway 배포 테스트 시작..."
echo "=================================================="

BASE_URL="https://ilgi-api-production.up.railway.app"

# 색깔 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 테스트 함수
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"
    
    echo -e "${BLUE}테스트: $name${NC}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url")
    status=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS:.*//g')
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ 성공 ($status)${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ 실패 (예상: $expected_status, 실제: $status)${NC}"
        echo "$body"
    fi
    echo ""
}

# 인증 테스트 함수 (Firebase 토큰 필요)
test_auth_endpoint() {
    local name="$1"
    local url="$2"
    local token="$3"
    local expected_status="$4"
    
    echo -e "${BLUE}테스트: $name${NC}"
    
    if [ -z "$token" ]; then
        echo -e "${YELLOW}⚠️ Firebase 토큰이 제공되지 않음 - 테스트 건너뜀${NC}"
        echo ""
        return
    fi
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        "$url")
    
    status=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS:.*//g')
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ 성공 ($status)${NC}"
    else
        echo -e "${RED}❌ 실패 (예상: $expected_status, 실제: $status)${NC}"
    fi
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
}

echo "1. 기본 서버 상태 확인"
echo "------------------------"

# 기본 엔드포인트 테스트
test_endpoint "루트 엔드포인트" "$BASE_URL/" 200
test_endpoint "헬스체크" "$BASE_URL/health" 200
test_endpoint "Flutter 연결 테스트" "$BASE_URL/api/v1/flutter/test" 200
test_endpoint "API 상태 확인" "$BASE_URL/api/v1/status" 200

echo "2. 환경 설정 확인 (디버깅)"
echo "---------------------------"

# 환경변수 디버깅 (개발 모드에서만 작동)
test_endpoint "환경변수 디버깅" "$BASE_URL/api/v1/debug/env" 200

echo "3. 인증 시스템 테스트"
echo "---------------------"

# Firebase 토큰이 있다면 여기에 입력
FIREBASE_TOKEN=""

if [ -z "$FIREBASE_TOKEN" ]; then
    echo -e "${YELLOW}⚠️ Firebase 토큰이 설정되지 않았습니다.${NC}"
    echo "Firebase 토큰을 테스트하려면 이 스크립트의 FIREBASE_TOKEN 변수에 값을 설정하세요."
    echo ""
    
    # 토큰 없이도 응답 확인 (401 또는 503 예상)
    test_auth_endpoint "Firebase 토큰 검증 (토큰 없음)" "$BASE_URL/api/v1/auth/verify-token" "" 401
else
    echo "Firebase 토큰으로 인증 테스트 진행..."
    test_auth_endpoint "Firebase 토큰 검증" "$BASE_URL/api/v1/auth/verify-token" "$FIREBASE_TOKEN" 200
    
    # 일기 분석 테스트 (인증 필요)
    curl -s -X POST "$BASE_URL/api/v1/analysis/diary" \
        -H "Authorization: Bearer $FIREBASE_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "diary_id": "test_diary_'$(date +%s)'",
            "content": "오늘은 정말 좋은 하루였다. 친구들과 함께 즐거운 시간을 보냈고, 날씨도 맑아서 기분이 좋았다.",
            "metadata": {
                "date": "'$(date +%Y-%m-%d)'",
                "weather": "맑음",
                "activities": ["친구만남", "카페"],
                "location": "서울"
            }
        }' \
        -w "HTTPSTATUS:%{http_code}" | \
        { 
            read response
            status=$(echo $response | sed -e 's/.*HTTPSTATUS://')
            body=$(echo $response | sed -e 's/HTTPSTATUS:.*//g')
            echo -e "${BLUE}테스트: 일기 분석 API${NC}"
            if [ "$status" -eq 200 ]; then
                echo -e "${GREEN}✅ 성공 ($status)${NC}"
            else
                echo -e "${RED}❌ 실패 ($status)${NC}"
            fi
            echo "$body" | jq '.' 2>/dev/null || echo "$body"
        }
fi

echo ""
echo "=================================================="
echo "🎯 테스트 완료!"
echo ""
echo "📊 결과 요약:"
echo "- ✅ 기본 서버 기능이 정상 작동하면 Firebase 설정과 관계없이 서버는 구동됨"
echo "- 🔥 Firebase 관련 API는 환경변수 설정 상태에 따라 동작"
echo "- 🚀 모든 기본 엔드포인트가 200으로 응답하면 수정 성공!"
echo ""

if [ -z "$FIREBASE_TOKEN" ]; then
    echo -e "${YELLOW}💡 Firebase 인증 테스트를 위해:${NC}"
    echo "1. Flutter 앱에서 Firebase 로그인 후 토큰 복사"
    echo "2. 이 스크립트의 FIREBASE_TOKEN 변수에 설정"
    echo "3. 스크립트 재실행"
fi

echo ""
echo "🔗 추가 확인 가능한 URL들:"
echo "- API 문서: $BASE_URL/docs"
echo "- 헬스체크: $BASE_URL/health"
echo "- 상태 확인: $BASE_URL/api/v1/status"
echo ""
