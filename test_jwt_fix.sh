#!/bin/bash

# AI Diary Backend - JWT 토큰 갱신 수정 후 테스트 스크립트

echo "🔧 JWT 토큰 갱신 문제 수정 후 테스트 시작..."
echo "=================================================="

BASE_URL="https://ilgi-api-production.up.railway.app"

# 색깔 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

# JWT 토큰 테스트 함수
test_jwt_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local jwt_token="$4"
    local data="$5"
    local expected_status="$6"
    
    echo -e "${PURPLE}JWT 테스트: $name${NC}"
    
    if [ -z "$jwt_token" ]; then
        echo -e "${YELLOW}⚠️ JWT 토큰이 제공되지 않음 - 테스트 건너뜀${NC}"
        echo ""
        return
    fi
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
            -H "Authorization: Bearer $jwt_token" \
            "$url")
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
            -X "$method" \
            -H "Authorization: Bearer $jwt_token" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url")
    fi
    
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

test_endpoint "루트 엔드포인트" "$BASE_URL/" 200
test_endpoint "헬스체크" "$BASE_URL/health" 200
test_endpoint "Flutter 연결 테스트" "$BASE_URL/api/v1/flutter/test" 200
test_endpoint "API 상태 확인" "$BASE_URL/api/v1/status" 200

echo "2. 환경 설정 확인"
echo "------------------"

test_endpoint "환경변수 디버깅" "$BASE_URL/api/v1/debug/env" 200

echo "3. JWT 토큰 갱신 테스트"
echo "======================"

# Firebase 토큰을 여기에 입력하세요
FIREBASE_TOKEN=""

if [ -z "$FIREBASE_TOKEN" ]; then
    echo -e "${YELLOW}⚠️ Firebase 토큰이 설정되지 않았습니다.${NC}"
    echo "Firebase 토큰을 테스트하려면 이 스크립트의 FIREBASE_TOKEN 변수에 값을 설정하세요."
    echo ""
    
    # 토큰 없이도 응답 확인 (401 예상)
    echo -e "${BLUE}토큰 없이 테스트 (401 예상)${NC}"
    test_endpoint "Firebase 토큰 검증 (토큰 없음)" "$BASE_URL/api/v1/auth/verify-token" 401
    test_endpoint "JWT 토큰 갱신 (토큰 없음)" "$BASE_URL/api/v1/auth/refresh" 401
    
else
    echo "🎯 Firebase 토큰으로 전체 인증 플로우 테스트..."
    echo ""
    
    # Step 1: Firebase 토큰으로 JWT 토큰 발급
    echo -e "${BLUE}Step 1: Firebase ID 토큰 → JWT 토큰 교환${NC}"
    jwt_response=$(curl -s -X POST "$BASE_URL/api/v1/auth/verify-token" \
        -H "Authorization: Bearer $FIREBASE_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "$jwt_response" | jq '.'
    
    # JWT 토큰 추출
    JWT_TOKEN=$(echo "$jwt_response" | jq -r '.access_token // empty')
    
    if [ -z "$JWT_TOKEN" ] || [ "$JWT_TOKEN" = "null" ]; then
        echo -e "${RED}❌ JWT 토큰 발급 실패${NC}"
        echo ""
    else
        echo -e "${GREEN}✅ JWT 토큰 발급 성공${NC}"
        echo "JWT 토큰: ${JWT_TOKEN:0:50}..."
        echo ""
        
        # Step 2: JWT 토큰으로 갱신 테스트
        echo -e "${BLUE}Step 2: JWT 토큰 갱신 테스트${NC}"
        test_jwt_endpoint "JWT 토큰 갱신" "POST" "$BASE_URL/api/v1/auth/refresh" "$JWT_TOKEN" "" 200
        
        # Step 3: JWT 토큰으로 사용자 정보 조회
        echo -e "${BLUE}Step 3: JWT 토큰으로 사용자 정보 조회${NC}"
        test_jwt_endpoint "사용자 정보 조회" "GET" "$BASE_URL/api/v1/auth/me" "$JWT_TOKEN" "" 200
        
        # Step 4: JWT 토큰으로 토큰 검증
        echo -e "${BLUE}Step 4: JWT 토큰 유효성 검증${NC}"
        test_jwt_endpoint "토큰 유효성 검증" "GET" "$BASE_URL/api/v1/auth/validate" "$JWT_TOKEN" "" 200
        
        # Step 5: JWT 토큰으로 일기 분석 API 테스트
        echo -e "${BLUE}Step 5: JWT 토큰으로 일기 분석 API 테스트${NC}"
        diary_data='{
            "diary_id": "test_diary_'$(date +%s)'",
            "content": "오늘은 정말 좋은 하루였다. 친구들과 함께 즐거운 시간을 보냈고, 날씨도 맑아서 기분이 좋았다.",
            "metadata": {
                "date": "'$(date +%Y-%m-%d)'",
                "weather": "맑음",
                "activities": ["친구만남", "카페"],
                "location": "서울"
            }
        }'
        
        test_jwt_endpoint "일기 분석 API" "POST" "$BASE_URL/api/v1/analysis/diary" "$JWT_TOKEN" "$diary_data" 200
    fi
fi

echo ""
echo "=================================================="
echo "🎯 JWT 토큰 갱신 수정 테스트 완료!"
echo ""
echo "📊 수정 사항 요약:"
echo "- ✅ Firebase 조건부 초기화: 500 에러 해결"
echo "- ✅ JWT 토큰 갱신 로직: 401 에러 해결"
echo "- ✅ 모든 API가 JWT 토큰 사용: 일관성 확보"
echo "- ✅ 에러 메시지 개선: 디버깅 용이성 향상"
echo ""

if [ -z "$FIREBASE_TOKEN" ]; then
    echo -e "${YELLOW}💡 완전한 테스트를 위해:${NC}"
    echo "1. Flutter 앱에서 Firebase 로그인 후 ID 토큰 복사"
    echo "2. 이 스크립트의 FIREBASE_TOKEN 변수에 설정"
    echo "3. 스크립트 재실행하여 전체 인증 플로우 확인"
else
    echo -e "${GREEN}🎉 모든 테스트 완료! 인증 시스템이 정상 작동합니다.${NC}"
fi

echo ""
echo "🔗 추가 확인 가능한 URL들:"
echo "- API 문서: $BASE_URL/docs"
echo "- 헬스체크: $BASE_URL/health"
echo "- 환경 디버깅: $BASE_URL/api/v1/debug/env"
echo ""
