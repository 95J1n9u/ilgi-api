# AI Diary Backend API 문서

## 개요

AI 일기 분석 백엔드 API는 Flutter 앱에서 일기 데이터를 받아 AI로 분석하여 감정, 성격, 행동 패턴을 추출하고 매칭을 위한 데이터를 제공합니다.

## Base URL

- **개발환경**: `http://localhost:8000`
- **프로덕션**: `https://your-domain.com`

## 인증

모든 API 엔드포인트는 Firebase Authentication을 사용합니다.

### 인증 헤더
```
Authorization: Bearer <firebase_id_token>
```

## API 엔드포인트

### 1. 인증 (Authentication)

#### 1.1 토큰 검증
Firebase ID 토큰을 검증하고 내부 JWT 토큰을 발급합니다.

**Endpoint**: `POST /api/v1/auth/verify-token`

**Headers**:
```
Authorization: Bearer <firebase_id_token>
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_info": {
    "uid": "user_123",
    "email": "user@example.com",
    "name": "User Name",
    "email_verified": true
  }
}
```

#### 1.2 현재 사용자 정보
**Endpoint**: `GET /api/v1/auth/me`

**Response**:
```json
{
  "uid": "user_123",
  "email": "user@example.com",
  "name": "User Name",
  "picture": "https://example.com/avatar.jpg",
  "email_verified": true
}
```

#### 1.3 토큰 갱신
**Endpoint**: `POST /api/v1/auth/refresh`

#### 1.4 토큰 검증
**Endpoint**: `GET /api/v1/auth/validate`

#### 1.5 로그아웃
**Endpoint**: `POST /api/v1/auth/logout`

---

### 2. AI 분석 (Analysis)

#### 2.1 일기 분석
일기 텍스트를 AI로 분석하여 감정, 성격, 키워드 등을 추출합니다.

**Endpoint**: `POST /api/v1/analysis/diary`

**Request Body**:
```json
{
  "diary_id": "diary_123",
  "content": "오늘은 정말 즐거운 하루였다. 친구들과 만나서 맛있는 음식도 먹고...",
  "metadata": {
    "date": "2024-12-12",
    "weather": "sunny",
    "mood": "happy",
    "activities": ["friends", "meal", "movie"],
    "location": "Seoul"
  }
}
```

**Response**:
```json
{
  "diary_id": "diary_123",
  "analysis_id": "analysis_456",
  "user_id": "user_123",
  "status": "completed",
  "emotion_analysis": {
    "primary_emotion": "joy",
    "secondary_emotions": ["excitement", "contentment"],
    "emotion_scores": [
      {
        "emotion": "joy",
        "score": 0.85,
        "confidence": 0.9
      }
    ],
    "sentiment_score": 0.78,
    "emotional_intensity": 0.8,
    "emotional_stability": 0.6
  },
  "personality_analysis": {
    "mbti_indicators": {
      "E": 0.7, "I": 0.3,
      "S": 0.4, "N": 0.6,
      "T": 0.3, "F": 0.7,
      "J": 0.6, "P": 0.4
    },
    "big5_traits": {
      "openness": 0.75,
      "conscientiousness": 0.68,
      "extraversion": 0.82,
      "agreeableness": 0.79,
      "neuroticism": 0.23
    },
    "predicted_mbti": "ENFJ",
    "personality_summary": [
      "강한 외향성과 사회적 성향을 보임",
      "감정적 결정을 선호하는 경향"
    ],
    "confidence_level": 0.8
  },
  "keyword_extraction": {
    "keywords": ["friends", "happiness", "social", "positive"],
    "topics": ["social_life", "leisure", "relationships"],
    "entities": ["Seoul"],
    "themes": ["friendship", "enjoyment"]
  },
  "lifestyle_patterns": {
    "activity_patterns": {
      "social_activities": 0.9,
      "outdoor_activities": 0.6
    },
    "social_patterns": {
      "friend_meetings": 0.8,
      "family_time": 0.5
    },
    "interest_areas": ["social", "food", "entertainment"],
    "values_orientation": {
      "relationships": 0.9,
      "enjoyment": 0.8
    }
  },
  "insights": [
    "사회적 상호작용을 통해 에너지를 얻는 성향이 강함",
    "긍정적 감정을 유지하는 능력이 뛰어남"
  ],
  "recommendations": [
    "꾸준한 사교 활동을 통해 정신적 웰빙 유지",
    "새로운 사람들과의 만남을 통한 성장 기회 모색"
  ],
  "analysis_version": "1.0",
  "processing_time": 2.45,
  "confidence_score": 0.85,
  "processed_at": "2024-12-12T10:30:00Z"
}
```

#### 2.2 분석 결과 조회
**Endpoint**: `GET /api/v1/analysis/diary/{diary_id}`

#### 2.3 일괄 분석
**Endpoint**: `POST /api/v1/analysis/batch`

**Request Body**:
```json
{
  "diary_entries": [
    {
      "diary_id": "diary_1",
      "content": "오늘은 즐거운 하루였다.",
      "metadata": {}
    },
    {
      "diary_id": "diary_2",
      "content": "조금 우울한 기분이다.",
      "metadata": {}
    }
  ]
}
```

#### 2.4 사용자 감정 패턴
**Endpoint**: `GET /api/v1/analysis/emotions/{user_id}`

**Response**:
```json
{
  "user_id": "user_123",
  "dominant_emotions": ["happiness", "contentment", "excitement"],
  "emotion_distribution": {
    "happiness": 35,
    "contentment": 25,
    "excitement": 20,
    "sadness": 10,
    "anxiety": 10
  },
  "avg_sentiment_score": 0.65,
  "emotion_trends": {
    "weekly_pattern": {
      "monday": 0.5,
      "tuesday": 0.6,
      "wednesday": 0.7,
      "thursday": 0.6,
      "friday": 0.8,
      "saturday": 0.9,
      "sunday": 0.7
    },
    "monthly_trend": [0.6, 0.65, 0.7, 0.68]
  }
}
```

#### 2.5 사용자 성격 분석
**Endpoint**: `GET /api/v1/analysis/personality/{user_id}`

#### 2.6 종합 인사이트
**Endpoint**: `GET /api/v1/analysis/insights/{user_id}`

#### 2.7 분석 이력
**Endpoint**: `GET /api/v1/analysis/history/{user_id}`

**Query Parameters**:
- `limit`: 조회할 항목 수 (기본값: 20)
- `offset`: 시작 위치 (기본값: 0)

#### 2.8 분석 통계
**Endpoint**: `GET /api/v1/analysis/stats/{user_id}`

#### 2.9 분석 결과 삭제
**Endpoint**: `DELETE /api/v1/analysis/diary/{diary_id}`

---

### 3. 매칭 (Matching)

#### 3.1 매칭 후보 추천
**Endpoint**: `POST /api/v1/matching/candidates`

**Request Body**:
```json
{
  "limit": 10,
  "min_compatibility": 0.6,
  "filters": {
    "age_range": [20, 30],
    "location": "Seoul",
    "interests": ["music", "travel"],
    "personality_types": ["ENFJ", "INFP"]
  }
}
```

**Response**:
```json
{
  "user_id": "user_123",
  "candidates": [
    {
      "user_id": "user_456",
      "compatibility_score": 0.85,
      "compatibility_level": "excellent",
      "age_range": "20대",
      "location": "서울",
      "personality_type": "INFP",
      "personality_traits": [
        "창의적이고 이상주의적",
        "깊이 있는 대화를 선호"
      ],
      "match_reasons": [
        "성격적으로 잘 어울리는 조합",
        "감정적 교감 가능"
      ],
      "common_traits": ["창의성", "감수성"],
      "complementary_traits": ["내향성과 외향성의 균형"],
      "match_rank": 1
    }
  ],
  "total_count": 5,
  "filters_applied": {
    "age_range": [20, 30],
    "location": "Seoul"
  }
}
```

#### 3.2 호환성 계산
**Endpoint**: `POST /api/v1/matching/compatibility`

**Request Body**:
```json
{
  "target_user_id": "user_456",
  "include_details": true
}
```

**Response**:
```json
{
  "user_id_1": "user_123",
  "user_id_2": "user_456",
  "overall_compatibility": 0.85,
  "compatibility_level": "excellent",
  "breakdown": {
    "personality_compatibility": 0.88,
    "emotion_compatibility": 0.82,
    "lifestyle_compatibility": 0.79,
    "interest_compatibility": 0.91,
    "communication_compatibility": 0.85
  },
  "strengths": [
    "성격적으로 잘 맞는 조합",
    "공통 관심사가 많음",
    "소통 스타일이 유사"
  ],
  "potential_challenges": [
    "생활 패턴 차이 조율 필요"
  ],
  "recommendations": [
    "서로의 차이점을 존중하는 대화",
    "공통 활동을 통한 유대감 강화"
  ],
  "calculated_at": "2024-12-12T11:00:00Z",
  "confidence_level": 0.9
}
```

#### 3.3 매칭 프로필 조회
**Endpoint**: `GET /api/v1/matching/profile/{user_id}`

#### 3.4 매칭 선호도 설정
**Endpoint**: `PUT /api/v1/matching/preferences`

**Request Body**:
```json
{
  "enabled": true,
  "visibility": "public",
  "preferred_age_range": [25, 35],
  "preferred_location_radius": 50,
  "personality_weight": 35,
  "emotion_weight": 25,
  "lifestyle_weight": 25,
  "interest_weight": 15,
  "min_compatibility_threshold": 60
}
```

#### 3.5 매칭 선호도 조회
**Endpoint**: `GET /api/v1/matching/preferences`

#### 3.6 매칭 이력
**Endpoint**: `GET /api/v1/matching/history`

#### 3.7 매칭 피드백
**Endpoint**: `POST /api/v1/matching/feedback`

#### 3.8 매칭 분석
**Endpoint**: `GET /api/v1/matching/analytics/{user_id}`

---

## 에러 코드

### HTTP 상태 코드

- `200`: 성공
- `201`: 생성됨
- `400`: 잘못된 요청
- `401`: 인증 실패
- `403`: 권한 없음
- `404`: 리소스 없음
- `422`: 유효성 검사 실패
- `429`: 요청 한도 초과
- `500`: 서버 오류
- `503`: 서비스 이용 불가

### 에러 응답 형식

```json
{
  "error": "ERROR_CODE",
  "message": "Error description",
  "status_code": 400,
  "details": {
    "field": "validation error details"
  }
}
```

### 주요 에러 코드

- `AUTH_FAILED`: 인증 실패
- `INSUFFICIENT_PERMISSIONS`: 권한 부족
- `RESOURCE_NOT_FOUND`: 리소스 없음
- `VALIDATION_ERROR`: 유효성 검사 실패
- `RATE_LIMIT_EXCEEDED`: 요청 한도 초과
- `AI_ANALYSIS_FAILED`: AI 분석 실패
- `DATABASE_ERROR`: 데이터베이스 오류

---

## Rate Limiting

API 호출은 사용자당 분당 100회로 제한됩니다.

Rate limit 헤더:
- `X-RateLimit-Limit`: 제한 횟수
- `X-RateLimit-Remaining`: 남은 횟수
- `X-RateLimit-Reset`: 리셋 시간

---

## 버전 관리

API 버전은 URL 경로에 포함됩니다: `/api/v1/`

현재 버전: **v1**

---

## SDK 및 예제

### cURL 예제

```bash
# 토큰 검증
curl -X POST "https://api.example.com/api/v1/auth/verify-token" \
  -H "Authorization: Bearer <firebase_token>"

# 일기 분석
curl -X POST "https://api.example.com/api/v1/analysis/diary" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "diary_id": "diary_123",
    "content": "오늘은 즐거운 하루였다.",
    "metadata": {"mood": "happy"}
  }'
```

### Flutter/Dart 예제

```dart
// API 클라이언트 설정
class DiaryApiClient {
  final String baseUrl;
  final String accessToken;
  
  DiaryApiClient(this.baseUrl, this.accessToken);
  
  Future<AnalysisResult> analyzeDiary(DiaryRequest request) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/analysis/diary'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(request.toJson()),
    );
    
    if (response.statusCode == 200) {
      return AnalysisResult.fromJson(jsonDecode(response.body));
    } else {
      throw ApiException(response.statusCode, response.body);
    }
  }
}
```

---

## 지원 및 문의

- **이메일**: support@example.com
- **문서**: https://docs.example.com
- **GitHub**: https://github.com/example/ai-diary-backend

---

## 변경 이력

### v1.0.0 (2024-12-12)
- 초기 API 릴리스
- 감정 분석 기능
- 성격 분석 기능
- 매칭 시스템
- Firebase 인증 통합
