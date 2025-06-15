# 🤖 AI 일기 분석 백엔드 API 명세서

## 📋 **개요**

**프로젝트명:** AI Diary Analysis Backend  
**버전:** v1.0.0  
**인증 방식:** Firebase Admin SDK  
**베이스 URL:** `https://ilgi-api-production.up.railway.app`  
**API 문서:** `https://ilgi-api-production.up.railway.app/docs`  

**주요 기능:**
- 🔥 Firebase 기반 사용자 인증
- 📝 AI 일기 분석 (감정, 성격, 키워드)
- 💕 사용자 매칭 시스템
- 📊 분석 통계 및 인사이트
- 🔍 실시간 모니터링 및 디버깅

---

## 🔐 **인증 시스템**

### **인증 방식**
- **Firebase ID Token** 필수
- **Authorization 헤더:** `Bearer {firebase_id_token}`
- **토큰 획득:** Flutter Firebase Auth SDK 사용

### **Firebase 토큰 예시**
```dart
// Flutter에서 토큰 획득
User? user = FirebaseAuth.instance.currentUser;
String? token = await user?.getIdToken();

// API 호출 시 헤더에 포함
headers: {
  'Authorization': 'Bearer $token',
  'Content-Type': 'application/json',
}
```

---

## 📚 **API 엔드포인트**

### **🌐 기본 엔드포인트 (인증 불필요)**

#### **1. 루트 엔드포인트**
```http
GET /
```
**설명:** 서버 기본 정보 조회  
**인증:** 불필요  
**응답:**
```json
{
  "message": "🤖 AI Diary Analysis Backend",
  "version": "1.0.0",
  "environment": "production",
  "authentication": "Firebase Admin SDK",
  "docs": "/docs",
  "health": "/health",
  "api_base": "/api/v1",
  "flutter_ready": true,
  "endpoints": {
    "auth": "/api/v1/auth",
    "analysis": "/api/v1/analysis",
    "matching": "/api/v1/matching"
  },
  "features": {
    "diary_analysis": true,
    "emotion_analysis": true,
    "personality_analysis": true,
    "user_matching": true,
    "firebase_auth": true
  }
}
```

#### **2. 헬스체크**
```http
GET /health
```
**설명:** 서버 상태 및 서비스 가용성 확인  
**인증:** 불필요  
**응답:**
```json
{
  "status": "healthy",
  "app_name": "AI Diary Analysis Backend",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-06-14T15:00:00Z",
  "services": {
    "gemini_api": true,
    "firebase": true,
    "database": false,
    "redis": false
  },
  "authentication": "Firebase Admin SDK",
  "ready_for_flutter": true,
  "deployment": {
    "platform": "Railway",
    "port": 8000,
    "environment": "production"
  }
}
```

#### **3. Flutter 연결 테스트**
```http
GET /api/v1/flutter/test
```
**설명:** Flutter 앱 연결 테스트  
**인증:** 불필요  
**응답:**
```json
{
  "status": "success",
  "message": "Flutter 앱과 백엔드 연결 성공!",
  "timestamp": "2025-06-14T15:00:00Z",
  "authentication": "Firebase Admin SDK",
  "server_info": {
    "name": "AI Diary Analysis Backend",
    "version": "1.0.0",
    "environment": "production"
  }
}
```

#### **4. API 상태 확인**
```http
GET /api/v1/status
```
**설명:** API 서비스별 상태 확인  
**인증:** 불필요  
**응답:**
```json
{
  "api_status": "operational",
  "authentication_method": "Firebase Admin SDK",
  "services": {
    "gemini_ai": "operational",
    "firebase_auth": "operational",
    "database": "unavailable",
    "redis_cache": "unavailable"
  },
  "last_check": "2025-06-14T15:00:00Z"
}
```

---

### **🔥 Firebase 인증 API**

#### **1. Firebase 토큰 검증**
```http
POST /api/v1/auth/verify-token
```
**설명:** Firebase ID 토큰 검증 및 사용자 정보 반환  
**인증:** Firebase ID 토큰 필요  
**헤더:**
```http
Authorization: Bearer {firebase_id_token}
```
**응답:**
```json
{
  "message": "Token verified successfully",
  "user": {
    "uid": "firebase_user_uid",
    "email": "user@example.com",
    "name": "사용자 이름",
    "picture": "https://...",
    "email_verified": true,
    "provider": "google.com"
  },
  "token_type": "firebase_id_token",
  "expires_at": 1735574400,
  "issued_at": 1735570800
}
```

#### **2. 토큰 갱신 안내**
```http
POST /api/v1/auth/refresh
```
**설명:** Firebase 토큰 갱신 안내 (클라이언트에서 처리)  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "message": "Token refresh should be handled by Firebase SDK on client side",
  "user_uid": "firebase_user_uid",
  "instruction": "Call firebase.auth().currentUser.getIdToken(true) to get fresh token",
  "current_token_valid": true
}
```

#### **3. 현재 사용자 정보**
```http
GET /api/v1/auth/me
```
**설명:** 현재 로그인된 사용자 정보 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "uid": "firebase_user_uid",
  "email": "user@example.com",
  "name": "사용자 이름",
  "picture": "https://...",
  "email_verified": true
}
```

#### **4. 토큰 유효성 검증**
```http
GET /api/v1/auth/validate
```
**설명:** Firebase 토큰 유효성 검증  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "valid": true,
  "uid": "firebase_user_uid",
  "email": "user@example.com",
  "email_verified": true,
  "provider": "google.com"
}
```

#### **5. 로그아웃**
```http
POST /api/v1/auth/logout
```
**설명:** 로그아웃 안내 (클라이언트에서 처리)  
**인증:** 불필요  
**응답:**
```json
{
  "message": "Logout should be handled by Firebase SDK on client side",
  "instruction": "Call firebase.auth().signOut() to logout user",
  "server_action": "No server-side session to clear"
}
```

#### **6. 인증 서비스 상태**
```http
GET /api/v1/auth/status
```
**설명:** Firebase 인증 서비스 상태 확인  
**인증:** 불필요  
**응답:**
```json
{
  "service": "Firebase Authentication",
  "status": "operational",
  "firebase_config": {
    "initialized": true,
    "use_firebase": true,
    "project_id": "your-proj...",
    "client_email": "firebase-adminsdk..."
  },
  "available_endpoints": [
    "/verify-token - Firebase ID 토큰 검증",
    "/refresh - 토큰 갱신 안내",
    "/me - 사용자 정보 조회",
    "/validate - 토큰 유효성 검증",
    "/logout - 로그아웃 안내",
    "/status - 서비스 상태 확인"
  ]
}
```

---

### **📝 일기 분석 API**

#### **1. 일기 AI 분석**
```http
POST /api/v1/analysis/diary
```
**설명:** 일기 텍스트 AI 분석 (감정, 성격, 키워드 추출)  
**인증:** Firebase 토큰 필요  
**요청 바디:**
```json
{
  "diary_id": "diary_12345",
  "content": "오늘은 정말 좋은 하루였다. 친구들과 카페에서 즐거운 시간을 보냈고, 새로운 책도 읽었다.",
  "metadata": {
    "date": "2025-06-14",
    "weather": "맑음",
    "location": "서울",
    "activities": ["친구만남", "독서", "카페"]
  }
}
```
**응답:**
```json
{
  "analysis_id": "analysis_1735570800",
  "diary_id": "diary_12345",
  "user_uid": "firebase_user_uid",
  "content": "오늘은 정말 좋은 하루였다...",
  "emotion_analysis": {
    "primary_emotion": "기쁨",
    "emotions": {
      "기쁨": 0.7,
      "만족": 0.5,
      "평온": 0.3,
      "설렘": 0.2
    },
    "sentiment_score": 0.8,
    "confidence": 0.9
  },
  "personality_insights": {
    "openness": 0.7,
    "conscientiousness": 0.6,
    "extraversion": 0.5,
    "agreeableness": 0.8,
    "neuroticism": 0.2,
    "dominant_traits": ["낙관적", "사교적", "성실함"]
  },
  "themes": ["일상", "관계", "성장"],
  "keywords": ["친구", "즐거움", "카페", "대화"],
  "mood_score": 8.5,
  "stress_level": 2.0,
  "life_satisfaction": 8.0,
  "recommendations": [
    "현재의 긍정적인 마음가짐을 유지하세요",
    "친구들과의 시간을 더 많이 가져보세요",
    "새로운 취미나 활동을 시도해보는 것도 좋겠습니다"
  ],
  "created_at": "2025-06-14T15:00:00Z",
  "processed_by": "gemini-1.5-flash"
}
```

#### **2. 분석 결과 조회**
```http
GET /api/v1/analysis/diary/{diary_id}
```
**설명:** 특정 일기의 분석 결과 조회  
**인증:** Firebase 토큰 필요  
**경로 파라미터:**
- `diary_id`: 일기 ID
**응답:** 일기 분석과 동일한 형태

#### **3. 감정 패턴 조회**
```http
GET /api/v1/analysis/emotions
```
**설명:** 사용자의 감정 패턴 및 추이 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "period": "last_30_days",
  "dominant_emotions": ["기쁨", "만족", "평온"],
  "emotion_trends": {
    "기쁨": [0.6, 0.7, 0.8, 0.7, 0.9],
    "슬픔": [0.1, 0.2, 0.1, 0.0, 0.1],
    "분노": [0.0, 0.1, 0.0, 0.1, 0.0],
    "불안": [0.2, 0.1, 0.3, 0.2, 0.1]
  },
  "average_sentiment": 0.75,
  "mood_stability": 0.8,
  "last_updated": "2025-06-14T15:00:00Z"
}
```

#### **4. 성격 분석 조회**
```http
GET /api/v1/analysis/personality
```
**설명:** 사용자의 성격 분석 결과 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "big_five": {
    "openness": 0.7,
    "conscientiousness": 0.6,
    "extraversion": 0.5,
    "agreeableness": 0.8,
    "neuroticism": 0.2
  },
  "personality_type": "ENFP",
  "dominant_traits": ["낙관적", "창의적", "사교적", "공감능력"],
  "growth_areas": ["계획성", "집중력"],
  "communication_style": "감정적이고 표현적",
  "stress_response": "사회적 지지 추구",
  "motivation_factors": ["새로운 경험", "인간관계", "창의적 표현"],
  "last_updated": "2025-06-14T15:00:00Z"
}
```

#### **5. 종합 인사이트**
```http
GET /api/v1/analysis/insights
```
**설명:** 사용자의 종합 인사이트 및 추천사항  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "summary": "전반적으로 긍정적인 감정 상태를 유지하고 있으며, 사회적 관계에서 에너지를 얻는 성향이 강합니다.",
  "emotional_wellbeing": {
    "score": 8.2,
    "trend": "improving",
    "key_factors": ["친구와의 만남", "새로운 활동", "창의적 취미"]
  },
  "behavioral_patterns": [
    "주말에 감정이 더 긍정적",
    "친구들과 시간을 보낸 후 만족도 상승",
    "혼자만의 시간도 중요하게 생각"
  ],
  "recommendations": [
    "현재의 긍정적인 라이프스타일 유지",
    "스트레스 관리를 위한 명상이나 요가 시도",
    "창의적 활동을 더 많이 포함시키기"
  ],
  "growth_opportunities": [
    "감정 표현 능력 향상",
    "장기 목표 설정 및 계획 수립",
    "새로운 기술이나 취미 학습"
  ],
  "generated_at": "2025-06-14T15:00:00Z"
}
```

#### **6. 분석 이력**
```http
GET /api/v1/analysis/history?limit=20&offset=0
```
**설명:** 사용자의 분석 이력 조회  
**인증:** Firebase 토큰 필요  
**쿼리 파라미터:**
- `limit`: 조회할 개수 (기본값: 20)
- `offset`: 시작 위치 (기본값: 0)
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "total_analyses": 45,
  "limit": 20,
  "offset": 0,
  "analyses": [
    {
      "analysis_id": "analysis_1",
      "diary_id": "diary_1",
      "date": "2025-06-14T15:00:00Z",
      "primary_emotion": "기쁨",
      "mood_score": 8.5,
      "themes": ["일상", "관계"]
    }
  ]
}
```

#### **7. 분석 삭제**
```http
DELETE /api/v1/analysis/diary/{diary_id}
```
**설명:** 특정 일기의 분석 결과 삭제  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "message": "Analysis deleted successfully",
  "diary_id": "diary_12345",
  "user_uid": "firebase_user_uid",
  "deleted_at": "2025-06-14T15:00:00Z"
}
```

#### **8. 분석 통계**
```http
GET /api/v1/analysis/stats
```
**설명:** 사용자의 분석 통계 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "total_analyses": 45,
  "this_month": 12,
  "avg_mood_score": 7.8,
  "most_common_emotion": "기쁨",
  "emotional_diversity": 0.7,
  "consistency_score": 0.8,
  "growth_trend": "positive",
  "streak_days": 15,
  "last_analysis": "2025-06-14T15:00:00Z"
}
```

---

### **💕 매칭 시스템 API**

#### **1. 매칭 후보 추천**
```http
POST /api/v1/matching/candidates
```
**설명:** 사용자에게 적합한 매칭 후보 추천  
**인증:** Firebase 토큰 필요  
**요청 바디:**
```json
{
  "limit": 10,
  "min_compatibility": 0.7,
  "filters": {
    "age_range": "20-30",
    "location": "서울",
    "interests": ["독서", "영화"]
  }
}
```
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "candidates": [
    {
      "user_uid": "candidate_1",
      "name": "매칭후보_1",
      "compatibility_score": 0.85,
      "common_interests": ["독서", "영화", "카페"],
      "personality_match": "높음",
      "age_range": "20대",
      "distance": "5km",
      "last_active": "2일 전"
    }
  ],
  "total_count": 5,
  "filters_applied": {
    "age_range": "20-30",
    "location": "서울"
  },
  "generated_at": "2025-06-14T15:00:00Z"
}
```

#### **2. 호환성 계산**
```http
POST /api/v1/matching/compatibility
```
**설명:** 두 사용자 간 호환성 점수 계산  
**인증:** Firebase 토큰 필요  
**요청 바디:**
```json
{
  "target_user_id": "target_user_uid"
}
```
**응답:**
```json
{
  "user1_uid": "firebase_user_uid",
  "user2_uid": "target_user_uid",
  "overall_score": 0.82,
  "compatibility_breakdown": {
    "personality_match": 0.85,
    "interest_overlap": 0.78,
    "communication_style": 0.80,
    "lifestyle_compatibility": 0.86,
    "emotional_compatibility": 0.83
  },
  "shared_traits": ["낙관적", "사교적", "창의적"],
  "complementary_traits": ["계획적 vs 자유로운", "이성적 vs 감성적"],
  "potential_challenges": ["시간 관리 스타일 차이", "의사결정 방식 차이"],
  "recommendations": [
    "공통 관심사인 독서와 영화 감상을 함께 즐겨보세요",
    "서로 다른 시간 관리 스타일을 존중하며 조율해보세요",
    "정기적인 대화 시간을 가져 소통을 늘려보세요"
  ],
  "calculated_at": "2025-06-14T15:00:00Z"
}
```

#### **3. 매칭 프로필 조회**
```http
GET /api/v1/matching/profile
```
**설명:** 사용자의 매칭용 프로필 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "display_name": "사용자 이름",
  "email": "user@example.com",
  "age_range": "20대",
  "location": "서울",
  "personality_summary": {
    "mbti": "ENFP",
    "traits": ["낙관적", "창의적", "사교적", "공감능력"],
    "communication_style": "감정적이고 표현적"
  },
  "interests": ["독서", "영화감상", "카페투어", "여행", "사진"],
  "lifestyle": {
    "activity_level": "활발함",
    "social_preference": "사교적",
    "work_life_balance": "균형 추구"
  },
  "matching_preferences": {
    "age_range": "20-30대",
    "distance_limit": "20km",
    "personality_types": ["ENFP", "INFP", "ENFJ"],
    "deal_breakers": ["흡연", "극도의 내향성"]
  },
  "recent_activity": {
    "last_diary": "2일 전",
    "mood_trend": "긍정적",
    "active_days": 15
  },
  "privacy_settings": {
    "show_real_name": false,
    "show_detailed_location": false,
    "allow_contact": true
  },
  "updated_at": "2025-06-14T15:00:00Z"
}
```

#### **4. 매칭 선호도 설정**
```http
PUT /api/v1/matching/preferences
```
**설명:** 매칭 선호도 설정 업데이트  
**인증:** Firebase 토큰 필요  
**요청 바디:**
```json
{
  "age_range": {"min": 22, "max": 32},
  "distance_limit": 20,
  "personality_preferences": ["ENFP", "INFP", "ENFJ"],
  "deal_breakers": ["흡연", "과도한 음주"]
}
```
**응답:**
```json
{
  "message": "Matching preferences updated successfully",
  "user_uid": "firebase_user_uid",
  "preferences": {
    "age_range": {"min": 22, "max": 32},
    "distance_limit": 20
  },
  "updated_at": "2025-06-14T15:00:00Z"
}
```

#### **5. 매칭 선호도 조회**
```http
GET /api/v1/matching/preferences
```
**설명:** 현재 매칭 선호도 설정 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "age_range": {"min": 22, "max": 32},
  "distance_limit": 20,
  "personality_preferences": ["ENFP", "INFP", "ENFJ", "INFJ"],
  "interest_priorities": ["독서", "영화", "여행", "음식"],
  "lifestyle_preferences": {
    "activity_level": "중간-높음",
    "social_frequency": "주 2-3회",
    "communication_style": "직접적이고 솔직한"
  },
  "deal_breakers": ["흡연", "과도한 음주", "불성실함"],
  "importance_weights": {
    "personality": 0.4,
    "interests": 0.3,
    "lifestyle": 0.2,
    "location": 0.1
  },
  "last_updated": "2025-06-14T15:00:00Z"
}
```

#### **6. 매칭 이력**
```http
GET /api/v1/matching/history?limit=20&offset=0
```
**설명:** 사용자의 매칭 이력 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "total_matches": 23,
  "successful_connections": 5,
  "limit": 20,
  "offset": 0,
  "matches": [
    {
      "match_id": "match_1",
      "partner_uid": "user_1",
      "partner_name": "매칭상대_1",
      "compatibility_score": 0.85,
      "matched_date": "2025-06-14T15:00:00Z",
      "status": "connected",
      "connection_duration": "7일",
      "feedback_given": true
    }
  ]
}
```

#### **7. 매칭 피드백**
```http
POST /api/v1/matching/feedback
```
**설명:** 매칭 결과에 대한 피드백 제출  
**인증:** Firebase 토큰 필요  
**요청 바디:**
```json
{
  "match_id": "match_12345",
  "rating": 4,
  "feedback": "좋은 매칭이었습니다",
  "liked_aspects": ["성격 매칭", "공통 관심사"],
  "suggestions": ["더 다양한 연령대 추천"]
}
```
**응답:**
```json
{
  "message": "Feedback submitted successfully",
  "user_uid": "firebase_user_uid",
  "feedback_id": "feedback_1735570800",
  "status": "received",
  "submitted_at": "2025-06-14T15:00:00Z"
}
```

#### **8. 매칭 분석**
```http
GET /api/v1/matching/analytics
```
**설명:** 사용자의 매칭 분석 데이터 조회  
**인증:** Firebase 토큰 필요  
**응답:**
```json
{
  "user_uid": "firebase_user_uid",
  "matching_stats": {
    "total_potential_matches": 156,
    "matches_generated": 23,
    "successful_connections": 5,
    "connection_rate": 0.22,
    "average_compatibility": 0.78
  },
  "preference_insights": {
    "most_compatible_types": ["ENFP", "INFP", "ENFJ"],
    "successful_traits": ["창의적", "공감능력", "사교적"],
    "improvement_areas": ["의사소통 스타일", "계획성"]
  },
  "activity_patterns": {
    "peak_matching_days": ["금요일", "토요일", "일요일"],
    "response_time_avg": "2.5시간",
    "profile_view_frequency": "높음"
  },
  "recommendations": [
    "프로필에 취미 정보를 더 상세히 추가해보세요",
    "매칭 선호도를 조금 더 넓게 설정해보세요",
    "정기적인 일기 작성으로 매칭 정확도를 높여보세요"
  ],
  "generated_at": "2025-06-14T15:00:00Z"
}
```

---

### **🔍 디버깅 및 모니터링 API**

#### **1. 환경 디버깅 (개발용)**
```http
GET /api/v1/debug/env
```
**설명:** 환경변수 및 서비스 상태 확인 (개발/테스트 모드에서만 접근 가능)  
**인증:** 불필요  
**응답:**
```json
{
  "debug_mode": true,
  "environment": "development",
  "authentication_method": "Firebase Admin SDK",
  "firebase": {
    "config_status": {
      "project_id": true,
      "private_key_id": true,
      "private_key": true,
      "client_email": true,
      "client_id": true,
      "use_firebase": true
    },
    "initialized": true,
    "project_id_value": "your-proj...",
    "client_email_value": "firebase-adminsdk..."
  },
  "services": {
    "gemini_api": true,
    "database": false,
    "redis": false
  },
  "railway": {
    "environment": "production",
    "port": "8000",
    "deployment": true
  },
  "removed_dependencies": [
    "python-jose - Firebase Admin SDK로 대체",
    "JWT 라이브러리 - Firebase 토큰 검증 사용"
  ],
  "message": "Firebase Admin SDK 기반 인증 시스템으로 완전 전환 완료"
}
```

---

## 🚨 **오류 응답**

### **인증 오류**
```json
{
  "error": "FIREBASE_AUTH_FAILED",
  "message": "Firebase token verification failed: Invalid token",
  "status_code": 401,
  "timestamp": "2025-06-14T15:00:00Z"
}
```

### **권한 부족**
```json
{
  "error": "INSUFFICIENT_PERMISSIONS",
  "message": "Not enough permissions",
  "status_code": 403,
  "timestamp": "2025-06-14T15:00:00Z"
}
```

### **리소스 없음**
```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Diary with ID 'diary_123' not found",
  "status_code": 404,
  "timestamp": "2025-06-14T15:00:00Z"
}
```

### **검증 오류**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": "diary_id field is required",
  "status_code": 422,
  "timestamp": "2025-06-14T15:00:00Z"
}
```

### **서비스 비활성화**
```json
{
  "error": "FIREBASE_SERVICE_UNAVAILABLE",
  "message": "Firebase authentication service is not available. Please contact administrator.",
  "status_code": 503,
  "timestamp": "2025-06-14T15:00:00Z"
}
```

### **서버 오류**
```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "status_code": 500,
  "timestamp": "2025-06-14T15:00:00Z"
}
```

---

## 📱 **Flutter 연동 가이드**

### **1. Firebase 설정**
```dart
// Firebase 초기화
await Firebase.initializeApp();

// 사용자 로그인
final UserCredential result = await FirebaseAuth.instance.signInWithEmailAndPassword(
  email: email,
  password: password,
);
```

### **2. 토큰 획득**
```dart
// Firebase ID 토큰 획득
User? user = FirebaseAuth.instance.currentUser;
String? idToken = await user?.getIdToken();
```

### **3. API 호출 헬퍼 클래스**
```dart
class ApiService {
  static const String baseUrl = 'https://ilgi-api-production.up.railway.app';
  
  static Future<Map<String, String>> getHeaders() async {
    User? user = FirebaseAuth.instance.currentUser;
    String? token = await user?.getIdToken();
    
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }
  
  // 일기 분석 API 호출
  static Future<Map<String, dynamic>> analyzeDiary({
    required String diaryId,
    required String content,
    Map<String, dynamic>? metadata,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/analysis/diary'),
      headers: await getHeaders(),
      body: jsonEncode({
        'diary_id': diaryId,
        'content': content,
        'metadata': metadata ?? {},
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to analyze diary: ${response.body}');
    }
  }
  
  // 매칭 후보 조회
  static Future<List<dynamic>> getMatchingCandidates({
    int limit = 10,
    double minCompatibility = 0.5,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/matching/candidates'),
      headers: await getHeaders(),
      body: jsonEncode({
        'limit': limit,
        'min_compatibility': minCompatibility,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['candidates'];
    } else {
      throw Exception('Failed to get matching candidates: ${response.body}');
    }
  }
}
```

### **4. 오류 처리**
```dart
try {
  final result = await ApiService.analyzeDiary(
    diaryId: 'diary_123',
    content: '오늘은 좋은 하루였다.',
  );
  print('분석 결과: $result');
} on FirebaseAuthException catch (e) {
  print('Firebase 인증 오류: ${e.message}');
} on Exception catch (e) {
  print('API 오류: $e');
}
```

---

## 🔧 **환경 설정**

### **필수 환경변수**
```bash
# Firebase 설정
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
USE_FIREBASE=true

# AI 분석
GEMINI_API_KEY=your-gemini-api-key

# 기본 설정
ENVIRONMENT=production
DEBUG=false
```

### **선택 환경변수**
```bash
# 데이터베이스 (선택사항)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis 캐시 (선택사항)
REDIS_URL=redis://host:port

# 보안 (필요시)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 📊 **응답 시간 및 제한사항**

### **일반적인 응답 시간**
- **인증 API:** 100-300ms
- **일기 분석:** 2-5초 (AI 처리 시간)
- **매칭 후보:** 500ms-1초
- **통계 조회:** 200-500ms

### **Rate Limiting**
- **일반 API:** 1000요청/시간
- **분석 API:** 100요청/시간
- **매칭 API:** 500요청/시간

### **데이터 제한**
- **일기 내용:** 최대 10,000자
- **매칭 후보:** 최대 50개
- **분석 이력:** 최대 1000개

---

## 🆘 **문제 해결**

### **Firebase 토큰 문제**
1. 토큰 만료 시: `getIdToken(true)` 호출하여 새 토큰 발급
2. 토큰 형식 오류: `Authorization: Bearer {token}` 형식 확인
3. 사용자 로그아웃 상태: Firebase 재로그인 필요

### **API 응답 오류**
1. **401 Unauthorized:** Firebase 토큰 확인
2. **403 Forbidden:** 권한 부족, 관리자 문의
3. **404 Not Found:** 리소스 ID 확인
4. **422 Validation Error:** 요청 데이터 형식 확인
5. **503 Service Unavailable:** 서비스 일시 중단, 잠시 후 재시도

### **서비스 상태 확인**
- **헬스체크:** `GET /health`
- **API 상태:** `GET /api/v1/status`
- **환경 디버깅:** `GET /api/v1/debug/env` (개발 모드)

---

## 📞 **지원 및 문의**

**API 문서:** https://ilgi-api-production.up.railway.app/docs  
**헬스체크:** https://ilgi-api-production.up.railway.app/health  
**Github Repository:** [Repository URL]  

**문의 시 포함할 정보:**
- Firebase UID (앞 10자리만)
- 요청 URL 및 메소드
- 요청 헤더 및 바디
- 오류 메시지 전문
- 발생 시간

---

**🎉 Firebase Admin SDK 기반의 완전한 AI 일기 분석 백엔드 API가 준비되었습니다!**
