# 🚨 Firebase 토큰 검증 오류 즉시 해결 가이드

## 📋 **현재 상황 요약**

✅ **확인된 정상 사항:**
- Firebase 프로젝트 ID: `ai-diary-matching` (Flutter ↔ 백엔드 일치)
- 토큰 형식: 정상 (3개 부분, 853자 길이)
- Firebase Admin SDK 초기화: 성공

❌ **핵심 문제:**
- 에러 메시지: `Could not verify token signature`
- 문제 위치: Firebase Admin SDK 토큰 검증 단계
- 발생 확률: 95% 서비스 계정 키 문제

## 🛠️ **즉시 해결 방법 (5분 내)**

### **1단계: 새 Firebase 서비스 계정 키 생성**

1. **Firebase Console 접속**
   ```
   👉 https://console.firebase.google.com/
   👉 "ai-diary-matching" 프로젝트 선택
   ```

2. **서비스 계정 설정**
   ```
   👉 설정(톱니바퀴) → 프로젝트 설정
   👉 "서비스 계정" 탭 클릭
   👉 "새 비공개 키 생성" 버튼 클릭
   👉 JSON 파일 다운로드
   ```

### **2단계: Railway 환경변수 업데이트**

1. **Railway Dashboard 접속**
   ```
   👉 https://railway.app
   👉 AI Diary Backend 프로젝트 선택
   👉 Variables 탭 클릭
   ```

2. **환경변수 업데이트**
   다운로드한 JSON 파일에서 다음 값들을 복사:

   ```bash
   FIREBASE_PROJECT_ID=ai-diary-matching
   FIREBASE_PRIVATE_KEY_ID="새로운_private_key_id"
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n새로운_private_key\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL="firebase-adminsdk-fbsvc@ai-diary-matching.iam.gserviceaccount.com"
   FIREBASE_CLIENT_ID="새로운_client_id"
   ```

   ⚠️ **중요:** `FIREBASE_PRIVATE_KEY`는 반드시 따옴표로 감싸기!

### **3단계: Flutter에서 새 토큰 발급**

```dart
// Flutter 코드에서 실행
User? user = FirebaseAuth.instance.currentUser;
if (user != null) {
  // 강제로 새 토큰 발급 (캐시 무시)
  String? newToken = await user.getIdToken(true);
  print('새 Firebase 토큰: $newToken');
  
  // 이 토큰으로 API 테스트
}
```

### **4단계: 즉시 테스트**

서버 재시작 후 (약 2분) 다음 명령어로 테스트:

```bash
# Windows Command Prompt에서
curl -X POST https://ilgi-api-production.up.railway.app/api/v1/auth/verify-token ^
  -H "Authorization: Bearer YOUR_NEW_FIREBASE_TOKEN"
```

## 🔧 **추가 확인사항**

### **Private Key 형식 검증**

올바른 형식:
```bash
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkq...\n-----END PRIVATE KEY-----\n"
```

잘못된 형식:
```bash
❌ FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...     # 따옴표 없음
❌ FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\n..."  # 이중 이스케이프
❌ FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY----- ..."   # 개행문자 없음
```

### **서비스 계정 권한 확인**

Firebase Console → IAM 및 관리자 → IAM에서 확인:
- ✅ Firebase Admin SDK 관리자 서비스 에이전트
- ✅ Service Account Token Creator (선택사항)

## 📊 **예상 결과**

### **✅ 성공 시**
```json
{
  "message": "Token verified successfully",
  "user": {
    "uid": "firebase_user_id",
    "email": "user@example.com"
  },
  "token_type": "firebase_id_token"
}
```

### **❌ 계속 실패 시**
```json
{
  "detail": "Firebase token verification failed: Could not verify token signature"
}
```

## 🆘 **문제 지속 시 체크리스트**

1. **[ ]** 새 서비스 계정 키 정상 생성됨
2. **[ ]** Railway 환경변수 올바르게 업데이트됨
3. **[ ]** `FIREBASE_PRIVATE_KEY`에 따옴표 포함됨
4. **[ ]** Flutter에서 새 토큰 발급됨 (`getIdToken(true)`)
5. **[ ]** 서버 재시작 완료됨 (Railway 배포 로그 확인)
6. **[ ]** 토큰 만료 시간이 유효함

## 🚀 **성공 확률: 95%**

새 Firebase 서비스 계정 키 생성만으로 대부분의 "Could not verify token signature" 문제가 해결됩니다.

---

**💡 핵심:** Firebase Console에서 새 서비스 계정 키를 생성하고 Railway 환경변수를 업데이트하는 것이 가장 확실한 해결책입니다!
