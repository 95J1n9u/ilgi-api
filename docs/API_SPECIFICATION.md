# AI 일기 분석 백엔드 API 명세서

## 📋 개요

**AI 일기 분석 백엔드**는 사용자 일기 데이터를 AI로 분석하여 감정, 성격, 생활 패턴을 추출하고, 이를 바탕으로 매칭 추천 데이터를 제공하는 REST API 서버입니다.

- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **Authentication**: Firebase ID Token + Bearer Token

---

## 🔐 인증

모든 보호된 엔드포인트는 다음 헤더가 필요합니다:

```http
Authorization: Bearer <firebase_id_token>
```

---

## 📚 API 엔드포인트

### 1. 인증 API (`/api/v1/auth`)

#### 1.1 Firebase 토큰 검증 및 내부 JWT 발급

```http
POST /api/v1/auth/verify-token
```

**설명**: Firebase ID 토큰을 검증하고 내부 JWT 토큰을 발급합니다.

**Request Headers**:
```http
Authorization: Bearer <firebase_id_token>
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_info": {
    "uid": "firebase_user_id",
    "email": "user@example.com",
    "name": "사용자 이름",
    "email_verified": true
  }
}
```

**Status Codes**:
- `200`: 성공
- `401`: 토큰 검증 실패

---

#### 1.2 토큰 갱신

```http
POST /api/v1/auth/refresh
```

**설명**: 기존 토큰으로 새로운 액세스 토큰을 발급받습니다.

**Request Headers**:
```http
Authorization: Bearer <current_token>
```

**Response**:
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer",
  "user_info": {
    "uid": "firebase_user_id",
    "email": "user@example.com",
    "name": "사용자 이름"
  }
}
```

---

#### 1.3 현재 사용자 정보 조회

```http
GET /api/v1/auth/me
```

**설명**: 현재 로그인된 사용자의 정보를 조회합니다.

**Request Headers**:
```http
Authorization: Bearer <token>
```

**Response**:
```json
{
  "uid": "firebase_user_id",
  "email": "user@example.com",
  "name": "사용자 이름",
  "picture": "profile_image_url",
  "email_verified": true
}
```

---

#### 1.4 로그아웃

```http
POST /api/v1/auth/logout
```

**설명**: 로그아웃 처리 (클라이언트에서 토큰 제거 필요)

**Response**:
```json
{
  "message": "Successfully logged out",
  "detail": "Please remove the token from client storage"
}
```

---

#### 1.5 토큰 유효성 검증

```http
GET /api/v1/auth/validate
```

**설명**: 현재 토큰의 유효성을 검증합니다.

**Request Headers**:
```http
Authorization: Bearer <token>
```

**Response**:
```json
{
  "valid": true,
  "user_id": "firebase_user_id",
  "email": "user@example.com"
}
```

---

### 2. AI 분석 API (`/api/v1/analysis`)

#### 2.1 일기 텍스트 AI 분석

```http
POST /api/v1/analysis/diary
```

**설명**: 일기 텍스트를 AI로 분석하여 감정, 성격, 키워드 등을 추출합니다.

**Request Headers**:
```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "diary_id": "unique_diary_id",
  "content": "오늘은 정말 행복한 하루였다. 친구들과 함께 영화를 보고...",
  "metadata": {
    "date": "2025-06-14",
    "weather": "맑음",
    "mood_before": "보통",
    "activities": ["영화감상", "친구만남"],
    "location": "서울"
  }
}
```

**Response**:
```json
{
  "diary_id": "unique_diary_id",
  "analysis_id": "analysis_uuid",
  "user_id": "firebase_user_id",
  "status": "completed",
  "emotion_analysis": {
    "primary_emotion": "행복",
    "secondary_emotions": ["만족", "평온"],
    "sentiment_score": 0.8,
    "emotional_intensity": 0.7,
    "emotional_stability": 0.85,
    "emotion_timeline": {
      "beginning": "중립",
      "middle": "행복",
      "end": "만족"
    }
  },
  "personality_analysis": {
    "mbti_indicators": {
      "extraversion": 0.7,
      "sensing": 0.6,
      "thinking": 0.4,
      "judging": 0.5
    },
    "big5_traits": {
      "openness": 0.8,
      "conscientiousness": 0.7,
      "extraversion": 0.6,
      "agreeableness": 0.8,
      "neuroticism": 0.3
    },
    "predicted_mbti": "ESFJ",
    "confidence_level": 0.75,
    "personality_insights": [
      "사교적이고 타인과의 관계를 중시하는 경향",
      "감정 표현이 풍부하고 공감 능력이 높음"
    ]
  },
  "keyword_extraction": {
    "keywords": ["행복", "친구", "영화", "함께"],
    "topics": ["여가활동", "인간관계", "감정"],
    "entities": ["서울", "영화관"],
    "themes": ["사회적 활동", "긍정적 경험"]
  },
  "lifestyle_patterns": {
    "activity_patterns": {
      "사회활동": 0.8,
      "문화활동": 0.7,
      "실내활동": 0.6
    },
    "social_patterns": {
      "친구와의_시간": 0.9,
      "혼자만의_시간": 0.3
    },
    "time_patterns": {
      "오후활동": 0.8,
      "저녁활동": 0.7
    },
    "interest_areas": ["영화", "친구관계", "여가활동"],
    "values_orientation": {
      "관계": 0.9,
      "즐거움": 0.8,
      "소통": 0.7
    }
  },
  "insights": [
    "사회적 활동을 통해 에너지를 얻는 외향적 성향이 강합니다",
    "친구들과의 관계에서 큰 만족감을 느끼고 있습니다",
    "문화 활동에 대한 관심이 높고 새로운 경험을 즐깁니다"
  ],
  "recommendations": [
    "정기적인 친구들과의 모임을 계획해보세요",
    "다양한 문화 활동을 탐색해보는 것을 추천합니다",
    "긍정적인 감정을 유지할 수 있는 활동들을 늘려보세요"
  ],
  "analysis_version": "1.0",
  "processing_time": 2.34,
  "confidence_score": 0.85,
  "processed_at": "2025-06-14T10:30:00Z"
}
```

**Status Codes**:
- `200`: 분석 성공
- `400`: 잘못된 요청 데이터
- `401`: 인증 실패
- `500`: 분석 처리 실패

---

#### 2.2 분석 결과 조회

```http
GET /api/v1/analysis/diary/{diary_id}
```

**설명**: 특정 일기의 분석 결과를 조회합니다.

**Path Parameters**:
- `diary_id`: 일기 고유 ID

**Request Headers**:
```http
Authorization: Bearer <token>
```

**Response**: 일기 분석과 동일한 형식

**Status Codes**:
- `200`: 조회 성공
- `404`: 분석 결과를 찾을 수 없음
- `401`: 인증 실패
- `403`: 권한 없음

---

#### 2.3 일괄 분석 (관리자 전용)

```http
POST /api/v1/analysis/batch
```

**설명**: 여러 일기를 일괄로 분석합니다.

**Request Body**:
```json
{
  "diary_entries": [
    {
      "diary_id": "diary_1",
      "content": "첫 번째 일기 내용...",
      "metadata": {}
    },
    {
      "diary_id": "diary_2", 
      "content": "두 번째 일기 내용...",
      "metadata": {}
    }
  ]
}
```

**Response**:
```json
{
  "message": "Batch analysis started",
  "total_entries": 2,
  "status": "processing"
}
```

---

#### 2.4 사용자 감정 패턴 조회

```http
GET /api/v1/analysis/emotions/{user_id}
```

**설명**: 사용자의 감정 패턴을 조회합니다.

**Path Parameters**:
- `user_id`: 사용자 ID (본인만 조회 가능)

**Request Headers**:
```http
Authorization: Bearer <token>
```

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "emotion_patterns": {
    "dominant_emotions": ["행복", "만족", "평온"],
    "emotion_frequency": {
      "행복": 0.4,
      "만족": 0.3,
      "평온": 0.2,
      "슬픔": 0.1
    },
    "emotional_stability": 0.75,
    "mood_trends": {
      "weekly_average": 0.7,
      "monthly_trend": "상승",
      "seasonal_pattern": "봄에 더 긍정적"
    }
  }
}
```

---

#### 2.5 사용자 성격 분석 결과 조회

```http
GET /api/v1/analysis/personality/{user_id}
```

**설명**: 사용자의 성격 분석 결과를 조회합니다.

**Path Parameters**:
- `user_id`: 사용자 ID (본인만 조회 가능)

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "personality_summary": {
    "predicted_mbti": "ESFJ",
    "confidence_level": 0.85,
    "big5_profile": {
      "openness": 0.8,
      "conscientiousness": 0.7,
      "extraversion": 0.6,
      "agreeableness": 0.8,
      "neuroticism": 0.3
    },
    "personality_strengths": [
      "높은 공감 능력",
      "뛰어난 사회적 기술",
      "책임감 있는 태도"
    ],
    "growth_areas": [
      "스트레스 관리 기술",
      "혼자만의 시간 활용"
    ]
  }
}
```

---

#### 2.6 사용자 종합 인사이트 조회

```http
GET /api/v1/analysis/insights/{user_id}
```

**설명**: 사용자의 모든 분석을 종합한 인사이트를 제공합니다.

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "overall_insights": {
    "personality_summary": "외향적이고 공감능력이 높은 성향",
    "emotional_patterns": "전반적으로 안정적이고 긍정적인 감정 상태",
    "lifestyle_preferences": ["사회적 활동", "문화활동", "친구관계"],
    "growth_recommendations": [
      "개인적인 취미 개발",
      "스트레스 관리 기술 습득"
    ],
    "compatibility_factors": {
      "ideal_partner_traits": ["공감능력", "사회성", "안정성"],
      "communication_style": "감정 표현이 풍부하고 직접적",
      "relationship_values": ["신뢰", "소통", "함께하는 시간"]
    }
  }
}
```

---

#### 2.7 분석 이력 조회

```http
GET /api/v1/analysis/history/{user_id}?limit=20&offset=0
```

**설명**: 사용자의 분석 이력을 조회합니다.

**Query Parameters**:
- `limit`: 조회할 개수 (기본값: 20)
- `offset`: 시작 위치 (기본값: 0)

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "history": [
    {
      "analysis_id": "analysis_uuid",
      "diary_id": "diary_id",
      "primary_emotion": "행복",
      "sentiment_score": 0.8,
      "processed_at": "2025-06-14T10:30:00Z"
    }
  ],
  "total_count": 150,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

---

#### 2.8 분석 결과 삭제

```http
DELETE /api/v1/analysis/diary/{diary_id}
```

**설명**: 특정 일기의 분석 결과를 삭제합니다.

**Response**:
```json
{
  "message": "Analysis deleted successfully"
}
```

---

#### 2.9 분석 통계 조회

```http
GET /api/v1/analysis/stats/{user_id}
```

**설명**: 사용자의 분석 통계를 조회합니다.

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "statistics": {
    "total_analyses": 150,
    "average_sentiment": 0.7,
    "most_common_emotion": "행복",
    "analysis_frequency": {
      "daily": 1.2,
      "weekly": 8.4,
      "monthly": 36.2
    },
    "personality_consistency": 0.85
  }
}
```

---

### 3. 매칭 API (`/api/v1/matching`)

#### 3.1 매칭 후보 추천

```http
POST /api/v1/matching/candidates
```

**설명**: 사용자와 호환성이 높은 매칭 후보를 추천합니다.

**Request Body**:
```json
{
  "limit": 10,
  "min_compatibility": 0.7,
  "filters": {
    "age_range": [25, 35],
    "location": "서울",
    "interests": ["영화", "독서"],
    "mbti_types": ["ENFJ", "INFJ"]
  }
}
```

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "candidates": [
    {
      "candidate_id": "candidate_uuid",
      "compatibility_score": 0.85,
      "shared_traits": ["외향성", "공감능력", "문화활동선호"],
      "personality_match": {
        "mbti_compatibility": 0.9,
        "big5_similarity": 0.8,
        "communication_style": "높은호환성"
      },
      "lifestyle_match": {
        "activity_overlap": 0.7,
        "value_alignment": 0.8,
        "social_pattern_fit": 0.85
      },
      "profile_preview": {
        "age": 28,
        "location": "서울",
        "interests": ["영화", "여행", "독서"],
        "personality_summary": "따뜻하고 공감능력이 뛰어난 성향"
      }
    }
  ],
  "total_count": 15,
  "filters_applied": {
    "age_range": [25, 35],
    "location": "서울"
  }
}
```

---

#### 3.2 호환성 점수 계산

```http
POST /api/v1/matching/compatibility
```

**설명**: 두 사용자 간의 호환성 점수를 계산합니다.

**Request Body**:
```json
{
  "target_user_id": "target_firebase_user_id"
}
```

**Response**:
```json
{
  "user_id_1": "firebase_user_id",
  "user_id_2": "target_firebase_user_id",
  "overall_compatibility": 0.85,
  "compatibility_breakdown": {
    "personality_compatibility": 0.9,
    "emotional_compatibility": 0.8,
    "lifestyle_compatibility": 0.85,
    "communication_compatibility": 0.88
  },
  "strengths": [
    "비슷한 가치관과 생활패턴",
    "높은 감정적 이해도",
    "상호 보완적인 성격 특성"
  ],
  "potential_challenges": [
    "의사결정 스타일의 차이",
    "사회활동 선호도 차이"
  ],
  "recommendations": [
    "공통 관심사를 중심으로 대화 시작",
    "서로의 차이점을 이해하고 존중하는 자세"
  ]
}
```

---

#### 3.3 매칭용 사용자 프로필 조회

```http
GET /api/v1/matching/profile/{user_id}
```

**설명**: 매칭용 사용자 프로필을 조회합니다.

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "profile": {
    "basic_info": {
      "age": 28,
      "location": "서울",
      "occupation": "개발자"
    },
    "personality_profile": {
      "mbti": "ESFJ",
      "big5_summary": "개방적이고 사교적인 성향",
      "key_traits": ["공감능력", "책임감", "사교성"]
    },
    "lifestyle_profile": {
      "interests": ["영화", "독서", "여행"],
      "values": ["가족", "성장", "관계"],
      "activity_preferences": ["문화활동", "사회활동"],
      "communication_style": "직접적이고 감정표현이 풍부"
    },
    "matching_preferences": {
      "preferred_age_range": [25, 35],
      "preferred_mbti": ["ENFJ", "INFJ", "ESFJ"],
      "important_values": ["신뢰", "소통", "성장"]
    }
  }
}
```

---

#### 3.4 매칭 선호도 설정 업데이트

```http
PUT /api/v1/matching/preferences
```

**설명**: 사용자의 매칭 선호도 설정을 업데이트합니다.

**Request Body**:
```json
{
  "age_range": [25, 35],
  "location_preference": ["서울", "경기"],
  "mbti_preferences": ["ENFJ", "INFJ"],
  "value_priorities": ["신뢰", "소통", "성장"],
  "lifestyle_preferences": {
    "activity_types": ["문화활동", "야외활동"],
    "social_frequency": "주 2-3회",
    "communication_style": "직접적"
  }
}
```

**Response**:
```json
{
  "message": "Matching preferences updated successfully",
  "preferences": {
    "age_range": [25, 35],
    "location_preference": ["서울", "경기"],
    "mbti_preferences": ["ENFJ", "INFJ"]
  }
}
```

---

#### 3.5 매칭 선호도 설정 조회

```http
GET /api/v1/matching/preferences
```

**설명**: 사용자의 현재 매칭 선호도 설정을 조회합니다.

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "preferences": {
    "age_range": [25, 35],
    "location_preference": ["서울", "경기"],
    "mbti_preferences": ["ENFJ", "INFJ"],
    "value_priorities": ["신뢰", "소통", "성장"]
  }
}
```

---

#### 3.6 매칭 이력 조회

```http
GET /api/v1/matching/history?limit=20&offset=0
```

**설명**: 사용자의 매칭 이력을 조회합니다.

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "history": [
    {
      "match_id": "match_uuid",
      "candidate_id": "candidate_uuid",
      "compatibility_score": 0.85,
      "matched_at": "2025-06-14T10:30:00Z",
      "status": "active",
      "interaction_summary": {
        "messages_exchanged": 15,
        "last_interaction": "2025-06-14T15:30:00Z"
      }
    }
  ],
  "total_count": 25
}
```

---

#### 3.7 매칭 피드백 제출

```http
POST /api/v1/matching/feedback
```

**설명**: 매칭에 대한 피드백을 제출합니다.

**Request Body**:
```json
{
  "match_id": "match_uuid",
  "feedback_type": "positive",
  "rating": 4,
  "comments": "성격이 잘 맞아서 좋았습니다",
  "interaction_quality": {
    "communication": 5,
    "compatibility": 4,
    "interest_level": 4
  }
}
```

**Response**:
```json
{
  "message": "Feedback submitted successfully",
  "status": "received"
}
```

---

#### 3.8 매칭 분석 데이터 조회

```http
GET /api/v1/matching/analytics/{user_id}
```

**설명**: 사용자의 매칭 분석 데이터를 조회합니다.

**Response**:
```json
{
  "user_id": "firebase_user_id",
  "analytics": {
    "matching_success_rate": 0.75,
    "average_compatibility_score": 0.72,
    "preferred_partner_traits": ["공감능력", "사교성", "안정성"],
    "matching_patterns": {
      "most_compatible_mbti": "ENFJ",
      "successful_age_range": [26, 32],
      "preferred_communication_style": "직접적"
    },
    "improvement_suggestions": [
      "프로필 사진 업데이트 권장",
      "관심사 정보 추가 필요"
    ]
  }
}
```

---

## 🚀 기타 엔드포인트

### 헬스체크

```http
GET /health
```

**설명**: 서버 상태를 확인합니다.

**Response**:
```json
{
  "status": "healthy",
  "app_name": "AI Diary Analysis Backend",
  "version": "1.0.0",
  "environment": "development"
}
```

### 루트 엔드포인트

```http
GET /
```

**설명**: API 서버 정보를 제공합니다.

**Response**:
```json
{
  "message": "🤖 AI Diary Analysis Backend",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 📊 HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 |
| 401 | Unauthorized | 인증 실패 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 422 | Unprocessable Entity | 데이터 검증 실패 |
| 429 | Too Many Requests | Rate Limit 초과 |
| 500 | Internal Server Error | 서버 내부 오류 |
| 503 | Service Unavailable | 서비스 이용 불가 |

---

## 🔧 에러 응답 형식

모든 에러 응답은 다음 형식을 따릅니다:

```json
{
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "status_code": 400,
  "details": "Additional error details (optional)"
}
```

**예시**:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "status_code": 422,
  "details": [
    {
      "field": "content",
      "message": "Content is required"
    }
  ]
}
```

---

## 📝 개발 참고사항

1. **Rate Limiting**: 기본적으로 분당 100회 요청 제한
2. **파일 크기 제한**: 최대 10MB
3. **일기 최대 길이**: 5,000자
4. **Cache TTL**: 분석 결과는 24시간 캐시됨
5. **Batch Size**: 일괄 분석 시 최대 10개 항목

---

## 🛠️ 개발 도구

- **API 문서**: `/docs` (Swagger UI)
- **ReDoc 문서**: `/redoc`
- **OpenAPI 스펙**: `/api/v1/openapi.json`

---

## 📞 지원

문의사항이나 버그 리포트는 다음을 통해 제출해주세요:
- GitHub Issues
- 개발팀 이메일