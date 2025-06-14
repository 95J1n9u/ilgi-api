# AI 일기 분석 백엔드 API 명세서

## 📋 **기본 정보**

- **API 이름**: AI Diary Analysis Backend
- **버전**: 1.0.0
- **Base URL**: `https://ilgi-api-production.up.railway.app/`
- **인증 방식**: Firebase Authentication + JWT Bearer Token
- **Content-Type**: `application/json`

## 🔗 **Base Endpoints**

### 🏠 **Root Endpoint**
```http
GET /
```
서버 기본 정보 및 Flutter 앱 연동 상태 확인

**응답 예시:**
```json
{
  "message": "🤖 AI Diary Analysis Backend",
  "version": "1.0.0",
  "environment": "production",
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

### 🔍 **Health Check**
```http
GET /health
```
서버 상태 및 서비스 점검

**응답 예시:**
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
    "database": true,
    "redis": true
  },
  "ready_for_flutter": true,
  "deployment": {
    "platform": "Railway",
    "port": 8000,
    "environment": "production"
  }
}
```

### 📱 **Flutter 연결 테스트**
```http
GET /api/v1/flutter/test
```
Flutter 앱과의 연결 상태 확인

**응답:**
```json
{
  "status": "success",
  "message": "Flutter 앱과 백엔드 연결 성공!",
  "timestamp": "2025-06-14T15:00:00Z",
  "server_info": {
    "name": "AI Diary Analysis Backend",
    "version": "1.0.0",
    "environment": "production"
  }
}
```

### 📊 **API 상태**
```http
GET /api/v1/status
```
API 서비스별 상태 확인

**응답:**
```json
{
  "api_status": "operational",
  "services": {
    "gemini_ai": "operational",
    "firebase_auth": "operational", 
    "database": "operational",
    "redis_cache": "operational"
  },
  "last_check": "2025-06-14T15:00:00Z"
}
```

---

## 🔐 **인증 API** (`/api/v1/auth`)

### 🔑 **Firebase 토큰 검증**
```http
POST /api/v1/auth/verify-token
```
Firebase ID 토큰을 검증하고 내부 JWT 토큰 발급

**Headers:**
```
Authorization: Bearer <firebase_id_token>
```

**응답:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_info": {
    "uid": "firebase_user_id",
    "email": "user@example.com",
    "name": "사용자 이름",
    "email_verified": true
  }
}
```

### 🔄 **토큰 갱신**
```http
POST /api/v1/auth/refresh
```
기존 토큰으로 새로운 액세스 토큰 발급

**Headers:**
```
Authorization: Bearer <current_token>
```

**응답:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_info": {
    "uid": "firebase_user_id",
    "email": "user@example.com",
    "name": "사용자 이름"
  }
}
```

### 👤 **현재 사용자 정보**
```http
GET /api/v1/auth/me
```
현재 로그인된 사용자 정보 조회

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "uid": "firebase_user_id",
  "email": "user@example.com",
  "name": "사용자 이름",
  "picture": "https://example.com/photo.jpg",
  "email_verified": true
}
```

### 🚪 **로그아웃**
```http
POST /api/v1/auth/logout
```
로그아웃 (클라이언트에서 토큰 제거)

**응답:**
```json
{
  "message": "Successfully logged out",
  "detail": "Please remove the token from client storage"
}
```

### ✅ **토큰 유효성 검증**
```http
GET /api/v1/auth/validate
```
토큰 유효성 검증

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "valid": true,
  "user_id": "firebase_user_id",
  "email": "user@example.com"
}
```

---

## 🧠 **AI 분석 API** (`/api/v1/analysis`)

### 📝 **일기 분석**
```http
POST /api/v1/analysis/diary
```
일기 텍스트의 종합 AI 분석

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 Body:**
```json
{
  "diary_id": "diary_20241214_001",
  "content": "오늘은 친구들과 카페에서 즐거운 시간을 보냈다. 새로운 프로젝트에 대해 이야기하면서 많은 아이디어를 얻었고, 앞으로의 계획에 대해 설레는 마음이 든다.",
  "metadata": {
    "date": "2024-12-14",
    "weather": "맑음",
    "mood": "기쁨",
    "location": "카페",
    "activities": ["친구 만남", "프로젝트 회의"],
    "tags": ["사회활동", "계획"]
  }
}
```

**응답:**
```json
{
  "diary_id": "diary_20241214_001",
  "analysis_id": "analysis_abc123",
  "user_id": "firebase_user_id",
  "status": "completed",
  "emotion_analysis": {
    "primary_emotion": "joy",
    "secondary_emotions": ["excitement", "hope"],
    "emotion_scores": [
      {
        "emotion": "joy",
        "score": 0.85,
        "confidence": 0.9
      },
      {
        "emotion": "excitement", 
        "score": 0.72,
        "confidence": 0.8
      }
    ],
    "sentiment_score": 0.78,
    "emotional_intensity": 0.75,
    "emotional_stability": 0.82
  },
  "personality_analysis": {
    "mbti_indicators": {
      "E": 0.75, "I": 0.25,
      "S": 0.45, "N": 0.55,
      "T": 0.35, "F": 0.65,
      "J": 0.60, "P": 0.40
    },
    "big5_traits": {
      "openness": 0.78,
      "conscientiousness": 0.68,
      "extraversion": 0.75,
      "agreeableness": 0.72,
      "neuroticism": 0.25
    },
    "predicted_mbti": "ENFJ",
    "personality_summary": [
      "사회적 상호작용을 즐기는 외향적 성향",
      "미래 가능성을 추구하는 직관적 사고",
      "인간관계를 중시하는 감정형 의사결정",
      "계획적이고 체계적인 판단형 성향"
    ],
    "confidence_level": 0.82
  },
  "keyword_extraction": {
    "keywords": ["친구", "카페", "프로젝트", "아이디어", "계획"],
    "topics": ["사회활동", "업무", "미래계획"],
    "entities": ["카페"],
    "themes": ["인간관계", "성장", "협업"]
  },
  "lifestyle_patterns": {
    "activity_patterns": {
      "사회활동": 0.8,
      "업무관련": 0.7,
      "학습": 0.6
    },
    "social_patterns": {
      "친구만남": 0.9,
      "협업": 0.8
    },
    "time_patterns": {
      "오후활동": 0.8
    },
    "interest_areas": ["프로젝트", "아이디어", "계획"],
    "values_orientation": {
      "성장": 0.8,
      "관계": 0.9
    }
  },
  "insights": [
    "사회적 상호작용을 통해 에너지를 얻는 성향이 강합니다",
    "미래 지향적 사고와 계획 수립에 적극적입니다",
    "협업과 아이디어 교류를 중시하는 특성을 보입니다"
  ],
  "recommendations": [
    "현재의 긍정적 에너지를 유지하며 프로젝트를 진행하세요",
    "친구들과의 정기적인 만남을 통해 지속적인 영감을 얻으세요",
    "구체적인 실행 계획을 세워 아이디어를 현실화해보세요"
  ],
  "analysis_version": "1.0",
  "processing_time": 2.34,
  "confidence_score": 0.82,
  "processed_at": "2024-12-14T15:30:00Z"
}
```

### 📄 **분석 결과 조회**
```http
GET /api/v1/analysis/diary/{diary_id}
```
특정 일기의 분석 결과 조회

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:** 위 일기 분석 응답과 동일

### 📊 **일괄 분석** (관리자 전용)
```http
POST /api/v1/analysis/batch
```
여러 일기를 한 번에 분석 (백그라운드 처리)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 Body:**
```json
{
  "diary_entries": [
    {
      "diary_id": "diary_001",
      "content": "일기 내용 1...",
      "metadata": {}
    },
    {
      "diary_id": "diary_002", 
      "content": "일기 내용 2...",
      "metadata": {}
    }
  ],
  "batch_options": {
    "priority": "normal"
  }
}
```

**응답:**
```json
{
  "message": "Batch analysis started",
  "total_entries": 2,
  "status": "processing"
}
```

### 😊 **사용자 감정 패턴 조회**
```http
GET /api/v1/analysis/emotions/{user_id}
```
사용자의 감정 패턴 분석 결과

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "dominant_emotions": ["joy", "hope", "excitement"],
  "emotion_trends": {
    "joy": [0.6, 0.7, 0.8, 0.75],
    "sadness": [0.3, 0.2, 0.1, 0.15]
  },
  "weekly_patterns": {
    "Monday": {"joy": 0.6, "stress": 0.4},
    "Friday": {"joy": 0.8, "excitement": 0.7}
  },
  "monthly_patterns": {
    "2024-12": {"avg_sentiment": 0.72, "stability": 0.8}
  }
}
```

### 🧑‍🎓 **사용자 성격 분석 조회**
```http
GET /api/v1/analysis/personality/{user_id}
```
사용자의 종합 성격 분석 결과

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "overall_mbti": "ENFJ",
  "overall_big5": {
    "openness": 0.75,
    "conscientiousness": 0.68,
    "extraversion": 0.72,
    "agreeableness": 0.78,
    "neuroticism": 0.28
  },
  "personality_traits": [
    "사교적이고 활동적인 성향",
    "창의적이고 혁신적인 아이디어를 추구",
    "인간관계와 가치를 중시하는 감정적 판단"
  ],
  "mbti_consistency": 0.85,
  "confidence_level": 0.82,
  "analysis_count": 15,
  "last_updated": "2024-12-14T15:30:00Z"
}
```

### 💡 **사용자 종합 인사이트**
```http
GET /api/v1/analysis/insights/{user_id}
```
사용자의 종합 분석 인사이트

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "analysis_period": {
    "start_date": "2024-11-01",
    "end_date": "2024-12-14"
  },
  "total_entries": 25,
  "overall_emotion_pattern": {
    "primary_emotion": "joy",
    "average_sentiment": 0.68,
    "emotional_stability": 0.75
  },
  "personality_profile": {
    "mbti_type": "ENFJ",
    "consistency": 0.85,
    "dominant_traits": ["외향적", "직관적", "감정형"]
  },
  "lifestyle_summary": {
    "activity_level": "high",
    "social_engagement": 0.8,
    "interest_diversity": 0.7
  },
  "emotion_trends": {
    "joy": [0.6, 0.65, 0.7, 0.75],
    "stress": [0.4, 0.35, 0.3, 0.25]
  },
  "personality_evolution": {
    "extraversion_change": 0.05,
    "openness_change": 0.02
  },
  "key_insights": [
    "지속적으로 긍정적인 감정 상태를 유지하고 있습니다",
    "사회적 활동을 통한 에너지 충전이 잘 이루어지고 있습니다",
    "새로운 도전과 성장에 대한 의지가 강합니다"
  ],
  "growth_areas": [
    "스트레스 관리 능력 향상",
    "혼자만의 시간을 통한 내적 성찰"
  ],
  "recommendations": [
    "현재의 긍정적 패턴을 유지하세요",
    "정기적인 사회활동을 계속하되 적절한 휴식도 취하세요",
    "새로운 관심사 탐구를 통해 개방성을 더욱 발전시키세요"
  ],
  "last_updated": "2024-12-14T15:30:00Z",
  "reliability_score": 0.88
}
```

### 📚 **분석 이력 조회**
```http
GET /api/v1/analysis/history/{user_id}?limit=20&offset=0
```
사용자의 분석 이력 조회

**Parameters:**
- `limit`: 조회할 항목 수 (기본값: 20)
- `offset`: 시작 위치 (기본값: 0)

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "history": [
    {
      "analysis_id": "analysis_abc123",
      "diary_id": "diary_20241214_001",
      "analysis_date": "2024-12-14T15:30:00Z",
      "primary_emotion": "joy",
      "sentiment_score": 0.78,
      "confidence_score": 0.82,
      "insights_count": 3
    }
  ],
  "total_count": 25,
  "page": 1,
  "has_next": true
}
```

### ❌ **분석 결과 삭제**
```http
DELETE /api/v1/analysis/diary/{diary_id}
```
특정 일기의 분석 결과 삭제

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "message": "Analysis deleted successfully"
}
```

### 📈 **분석 통계**
```http
GET /api/v1/analysis/stats/{user_id}
```
사용자의 분석 통계 조회

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "total_analyses": 25,
  "analysis_period_days": 45,
  "emotion_distribution": {
    "joy": 8,
    "excitement": 5,
    "calm": 4,
    "sadness": 3,
    "stress": 5
  },
  "avg_sentiment_score": 0.68,
  "sentiment_trend": [0.6, 0.65, 0.7, 0.68],
  "personality_consistency": 0.85,
  "dominant_traits": ["외향적", "직관적", "감정형"],
  "analysis_frequency": {
    "daily": 15,
    "weekly": 8,
    "irregular": 2
  },
  "most_active_periods": ["저녁", "주말"],
  "total_insights": 75,
  "insight_categories": {
    "emotion": 25,
    "personality": 20,
    "lifestyle": 18,
    "growth": 12
  }
}
```

---

## 💕 **매칭 API** (`/api/v1/matching`)

### 🔍 **매칭 후보 추천**
```http
POST /api/v1/matching/candidates
```
사용자에게 호환성 높은 매칭 후보 추천

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 Body:**
```json
{
  "limit": 10,
  "min_compatibility": 0.6,
  "filters": {
    "age_range": [25, 35],
    "location": "서울",
    "interests": ["독서", "영화"],
    "personality_types": ["ENFJ", "INFP"],
    "exclude_users": ["user123", "user456"]
  },
  "include_analysis": true
}
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "candidates": [
    {
      "user_id": "candidate_001",
      "compatibility_score": 0.85,
      "compatibility_level": "excellent",
      "age_range": "20대 후반",
      "location": "서울 강남",
      "interests": ["독서", "카페", "여행"],
      "personality_type": "INFP",
      "personality_traits": [
        "깊이 있는 사고를 선호하는 내향적 성향",
        "창의적이고 혁신적인 아이디어를 추구",
        "인간관계와 가치를 중시하는 감정적 판단"
      ],
      "match_reasons": [
        "성격적으로 잘 어울리는 조합",
        "감정적으로 안정적인 관계 형성 가능",
        "매우 높은 전체 호환성"
      ],
      "common_traits": [
        "창의적 사고",
        "인간관계 중시"
      ],
      "complementary_traits": [
        "내향성과 외향성의 균형"
      ],
      "last_active": "2024-12-14T10:00:00Z",
      "match_rank": 1
    }
  ],
  "total_count": 8,
  "filters_applied": {
    "age_range": [25, 35],
    "location": "서울"
  },
  "algorithm_version": "1.0",
  "generated_at": "2024-12-14T15:30:00Z",
  "expires_at": "2024-12-15T15:30:00Z"
}
```

### 🎯 **호환성 점수 계산**
```http
POST /api/v1/matching/compatibility
```
두 사용자 간의 상세 호환성 분석

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 Body:**
```json
{
  "target_user_id": "target_user_123",
  "include_details": true
}
```

**응답:**
```json
{
  "user_id_1": "firebase_user_id",
  "user_id_2": "target_user_123",
  "overall_compatibility": 0.82,
  "compatibility_level": "excellent",
  "breakdown": {
    "personality_compatibility": 0.85,
    "emotion_compatibility": 0.78,
    "lifestyle_compatibility": 0.80,
    "interest_compatibility": 0.75,
    "communication_compatibility": 0.83
  },
  "strengths": [
    "성격적으로 잘 맞는 조합으로 서로를 이해하기 쉬울 것",
    "감정적으로 안정된 관계를 유지할 수 있을 것",
    "생활 패턴이 비슷하여 함께 시간을 보내기 편할 것"
  ],
  "potential_challenges": [
    "관심사 차이로 인해 서로의 취미를 이해하려는 노력 필요"
  ],
  "recommendations": [
    "서로의 장점을 인정하고 꾸준한 소통으로 관계 발전시키기",
    "서로의 관심사에 대해 배우고 새로운 공통분모 찾기"
  ],
  "calculated_at": "2024-12-14T15:30:00Z",
  "confidence_level": 0.88
}
```

### 👤 **매칭 프로필 조회**
```http
GET /api/v1/matching/profile/{user_id}
```
매칭용 사용자 프로필 조회

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "user_123",
  "display_name": "김철수",
  "age_range": "20대 후반",
  "location": "서울 강남",
  "bio": "책을 좋아하고 새로운 사람들과의 만남을 즐깁니다.",
  "personality_type": "ENFJ",
  "personality_summary": [
    "사교적이고 활동적인 성향",
    "인간관계와 가치를 중시하는 감정적 판단"
  ],
  "interests": ["독서", "영화감상", "카페탐방"],
  "hobbies": ["사진촬영", "요리"],
  "lifestyle_tags": ["활동적", "사교적", "문화생활"],
  "activity_level": "high",
  "looking_for": ["진지한 관계", "장기적 파트너"],
  "profile_completeness": 0.85,
  "last_active": "2024-12-14T10:00:00Z",
  "verified": true
}
```

### ⚙️ **매칭 선호도 설정**
```http
PUT /api/v1/matching/preferences
```
매칭 선호도 업데이트

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 Body:**
```json
{
  "enabled": true,
  "visibility": "public",
  "preferred_age_range": [25, 35],
  "preferred_location_radius": 30,
  "preferred_personality_types": ["ENFJ", "INFP", "ENFP"],
  "personality_weight": 0.35,
  "emotion_weight": 0.25,
  "lifestyle_weight": 0.25,
  "interest_weight": 0.15,
  "min_compatibility_threshold": 0.6,
  "diversity_factor": 0.2
}
```

**응답:**
```json
{
  "message": "Matching preferences updated successfully",
  "preferences": {
    "enabled": true,
    "visibility": "public",
    "preferred_age_range": [25, 35],
    "personality_weight": 0.35,
    "emotion_weight": 0.25,
    "lifestyle_weight": 0.25,
    "interest_weight": 0.15
  }
}
```

### ⚙️ **매칭 선호도 조회**
```http
GET /api/v1/matching/preferences
```
현재 매칭 선호도 설정 조회

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "preferences": {
    "enabled": true,
    "visibility": "public",
    "preferred_age_range": [25, 35],
    "preferred_location_radius": 30,
    "personality_weight": 0.35,
    "emotion_weight": 0.25,
    "lifestyle_weight": 0.25,
    "interest_weight": 0.15,
    "min_compatibility_threshold": 0.6
  }
}
```

### 📚 **매칭 이력**
```http
GET /api/v1/matching/history?limit=20&offset=0
```
매칭 이력 조회

**Parameters:**
- `limit`: 조회할 항목 수 (기본값: 20)
- `offset`: 시작 위치 (기본값: 0)

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "history": [
    {
      "target_user_id": "user_123",
      "compatibility_score": 0.85,
      "interaction_type": "like",
      "matched_at": "2024-12-14T15:00:00Z",
      "interaction_date": "2024-12-14T15:30:00Z",
      "status": "pending"
    }
  ],
  "total_count": 15
}
```

### 💬 **매칭 피드백**
```http
POST /api/v1/matching/feedback
```
매칭 결과에 대한 피드백 제출

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**요청 Body:**
```json
{
  "target_user_id": "user_123",
  "interaction_type": "like",
  "feedback_reason": "personality_match",
  "rating": 5,
  "comment": "성격이 잘 맞는 것 같아요"
}
```

**응답:**
```json
{
  "message": "Feedback submitted successfully",
  "status": "received"
}
```

### 📊 **매칭 분석**
```http
GET /api/v1/matching/analytics/{user_id}
```
사용자의 매칭 성과 분석

**Headers:**
```
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "user_id": "firebase_user_id",
  "analysis_period": {
    "start_date": "2024-11-01",
    "end_date": "2024-12-14"
  },
  "total_matches_found": 45,
  "avg_compatibility_score": 0.72,
  "match_success_rate": 0.35,
  "profile_views": 120,
  "profile_likes": 25,
  "profile_completeness": 0.85,
  "personality_match_rate": 0.68,
  "interest_overlap_avg": 0.45,
  "profile_improvement_tips": [
    "프로필 사진 추가로 완성도 향상",
    "관심사를 더 구체적으로 작성"
  ],
  "matching_strategy_tips": [
    "선호하는 성격 유형을 다양화해보세요",
    "지역 범위를 조금 더 넓혀보는 것을 고려해보세요"
  ],
  "compatibility_trends": {
    "personality": [0.65, 0.68, 0.70, 0.72],
    "lifestyle": [0.60, 0.62, 0.65, 0.63]
  },
  "popular_traits": ["외향적", "창의적", "친화적"]
}
```

---

## 📋 **공통 응답 코드**

### ✅ **성공 응답**
- `200 OK`: 요청 성공
- `201 Created`: 리소스 생성 성공
- `204 No Content`: 성공 (응답 본문 없음)

### ❌ **오류 응답**

#### 클라이언트 오류 (4xx)
```json
{
  "detail": "오류 메시지",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-12-14T15:30:00Z"
}
```

- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `429 Too Many Requests`: 요청 한도 초과

#### 서버 오류 (5xx)
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "timestamp": "2024-12-14T15:30:00Z"
}
```

- `500 Internal Server Error`: 서버 내부 오류
- `502 Bad Gateway`: 외부 서비스 오류
- `503 Service Unavailable`: 서비스 일시 중단

---

## 🔧 **인증 및 보안**

### 🔑 **인증 방식**
1. **Firebase Authentication**: 사용자 인증
2. **JWT Bearer Token**: API 요청 인증

### 📋 **Header 예시**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### 🛡️ **보안 기능**
- **CORS**: Flutter 앱 및 웹 클라이언트 지원
- **Rate Limiting**: API 요청 제한
- **Input Validation**: 입력 데이터 검증
- **Error Handling**: 안전한 오류 메시지

---

## 🚀 **Flutter 앱 연동 가이드**

### 📱 **기본 설정**
```dart
class APIService {
  static const String baseUrl = 'https://ilgi-api-production.up.railway.app/';
  
  static Map<String, String> getHeaders(String token) {
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }
}
```

### 🔐 **인증 플로우**
1. Firebase Auth로 사용자 로그인
2. Firebase ID Token 획득
3. `/api/v1/auth/verify-token`으로 JWT 토큰 발급
4. 이후 모든 API 요청에 JWT 토큰 사용

### 📝 **일기 분석 예시**
```dart
Future<DiaryAnalysisResponse> analyzeDiary({
  required String diaryId,
  required String content,
  Map<String, dynamic>? metadata,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/v1/analysis/diary'),
    headers: getHeaders(accessToken),
    body: jsonEncode({
      'diary_id': diaryId,
      'content': content,
      'metadata': metadata,
    }),
  );
  
  if (response.statusCode == 200) {
    return DiaryAnalysisResponse.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to analyze diary');
  }
}
```

---

## 📊 **성능 및 제한사항**

### ⚡ **성능 지표**
- **응답 시간**: 일기 분석 2-5초, 기타 API 100-500ms
- **동시 사용자**: 최대 1000명
- **일일 요청 한도**: 사용자당 1000회

### 📏 **데이터 제한**
- **일기 내용**: 최대 5000자
- **이미지 업로드**: 최대 10MB
- **분석 이력**: 최대 1000건 보관

### 🔄 **Rate Limiting**
- **일반 API**: 분당 60회
- **AI 분석**: 분당 10회
- **매칭 API**: 분당 30회

---

## 🐛 **문제 해결**

### 🔍 **일반적인 오류**

**401 Unauthorized**
```json
{
  "detail": "Token verification failed: Invalid token"
}
```
→ Firebase 토큰을 다시 발급받거나 JWT 토큰을 갱신하세요

**429 Too Many Requests**
```json
{
  "detail": "Rate limit exceeded"
}
```
→ 요청 빈도를 줄이고 잠시 후 다시 시도하세요

**500 Internal Server Error**
```json
{
  "detail": "Analysis failed: Gemini API error"
}
```
→ 잠시 후 다시 시도하거나 지원팀에 문의하세요

### 📞 **지원**
- **문서**: `/docs` (Swagger UI)
- **상태 확인**: `/health`
- **연결 테스트**: `/api/v1/flutter/test`

---

**🎉 API 명세서 작성 완료!** 

이 명세서를 참고하여 Flutter 앱과 완벽하게 연동하세요!