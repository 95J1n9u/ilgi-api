#!/usr/bin/env python3
"""
Firebase 토큰 검증 문제 해결 스크립트
서비스 계정 키 재생성 및 검증 테스트
"""

import json
import base64
import requests
from datetime import datetime


def validate_service_account_key(private_key: str, project_id: str, client_email: str):
    """서비스 계정 키 유효성 검증"""
    print("🔍 서비스 계정 키 검증 중...")
    
    # Private Key 형식 검증
    if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
        print("❌ Private Key 형식 오류: BEGIN 태그 없음")
        return False
        
    if not private_key.endswith("-----END PRIVATE KEY-----\n"):
        print("❌ Private Key 형식 오류: END 태그 없음")
        return False
    
    # 개행 문자 확인
    if "\\n" in private_key:
        print("⚠️ Private Key에 이스케이프된 개행문자(\\n) 발견")
        print("💡 실제 개행문자로 변환 필요")
        
    # 프로젝트 ID 형식 검증
    if not project_id or project_id != "ai-diary-matching":
        print(f"❌ 프로젝트 ID 오류: {project_id}")
        return False
        
    # 클라이언트 이메일 형식 검증
    if not client_email.endswith(f"@{project_id}.iam.gserviceaccount.com"):
        print(f"❌ 클라이언트 이메일 형식 오류: {client_email}")
        return False
    
    print("✅ 서비스 계정 키 기본 형식 검증 완료")
    return True


def test_firebase_admin_connection(service_account_data: dict):
    """Firebase Admin SDK 연결 테스트"""
    print("🔥 Firebase Admin SDK 연결 테스트...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, auth
        
        # 기존 앱 정리
        try:
            firebase_admin.delete_app(firebase_admin.get_app())
        except:
            pass
            
        # 서비스 계정으로 초기화
        cred = credentials.Certificate(service_account_data)
        app = firebase_admin.initialize_app(cred)
        
        print("✅ Firebase Admin SDK 초기화 성공")
        
        # 더미 토큰으로 서비스 테스트
        try:
            auth.verify_id_token("dummy_token")
        except Exception as e:
            if "Could not parse" in str(e) or "Invalid" in str(e):
                print("✅ Firebase Auth 서비스 응답 확인")
                return True
            else:
                print(f"❌ Firebase Auth 서비스 문제: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Firebase Admin SDK 초기화 실패: {e}")
        return False


def create_new_service_account_guide():
    """새 서비스 계정 생성 가이드"""
    print("\n" + "="*60)
    print("🔧 새 Firebase 서비스 계정 생성 방법")
    print("="*60)
    
    print("""
1. 📱 Firebase Console 접속
   👉 https://console.firebase.google.com/

2. 🏗️ 프로젝트 선택
   👉 ai-diary-matching 프로젝트 클릭

3. ⚙️ 설정 → 서비스 계정
   👉 프로젝트 설정 → 서비스 계정 탭

4. 🔑 새 비공개 키 생성
   👉 "새 비공개 키 생성" 버튼 클릭
   👉 JSON 파일 다운로드

5. 📋 Railway 환경변수 업데이트
   다운로드된 JSON 파일에서 다음 값들을 복사:
   
   FIREBASE_PROJECT_ID=ai-diary-matching
   FIREBASE_PRIVATE_KEY_ID=<private_key_id>
   FIREBASE_PRIVATE_KEY="<private_key 전체>"
   FIREBASE_CLIENT_EMAIL=<client_email>
   FIREBASE_CLIENT_ID=<client_id>

⚠️ 중요 사항:
- Private Key는 따옴표로 감싸기
- 개행문자는 실제 \\n으로 유지
- 모든 값에 공백이나 특수문자 없는지 확인
""")


def check_token_expiry(token: str):
    """토큰 만료 시간 확인"""
    print("⏰ 토큰 만료 시간 확인...")
    
    try:
        # JWT 토큰 디코딩 (검증 없이)
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ 잘못된 토큰 형식")
            return False
            
        # 페이로드 디코딩
        payload_data = parts[1]
        while len(payload_data) % 4 != 0:
            payload_data += '='
            
        payload = json.loads(base64.b64decode(payload_data))
        
        exp_time = payload.get('exp')
        iat_time = payload.get('iat')
        current_time = datetime.now().timestamp()
        
        if exp_time:
            exp_datetime = datetime.fromtimestamp(exp_time)
            print(f"📅 토큰 만료 시간: {exp_datetime}")
            
            if exp_time < current_time:
                print("❌ 토큰이 만료됨")
                print("💡 Flutter 앱에서 새 토큰 발급 필요")
                return False
            else:
                remaining = exp_time - current_time
                print(f"✅ 토큰 유효 (남은 시간: {remaining/60:.1f}분)")
                return True
        else:
            print("⚠️ 토큰에 만료 시간 정보 없음")
            return False
            
    except Exception as e:
        print(f"❌ 토큰 디코딩 실패: {e}")
        return False


def main():
    """메인 실행 함수"""
    print("🔧 Firebase 토큰 검증 문제 해결 도구")
    print("="*50)
    
    # 1. 현재 환경변수 확인
    from app.config.settings import get_settings
    settings = get_settings()
    
    print("\n📊 현재 Firebase 설정:")
    print(f"   Project ID: {settings.FIREBASE_PROJECT_ID}")
    print(f"   Client Email: {settings.FIREBASE_CLIENT_EMAIL}")
    print(f"   Private Key ID: {settings.FIREBASE_PRIVATE_KEY_ID}")
    print(f"   Private Key Length: {len(settings.FIREBASE_PRIVATE_KEY) if settings.FIREBASE_PRIVATE_KEY else 0}")
    
    # 2. 서비스 계정 키 검증
    if not validate_service_account_key(
        settings.FIREBASE_PRIVATE_KEY,
        settings.FIREBASE_PROJECT_ID,
        settings.FIREBASE_CLIENT_EMAIL
    ):
        print("\n❌ 서비스 계정 키 문제 발견!")
        create_new_service_account_guide()
        return
    
    # 3. Firebase Admin SDK 연결 테스트
    service_account_data = {
        "type": "service_account",
        "project_id": settings.FIREBASE_PROJECT_ID,
        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
        "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
        "client_email": settings.FIREBASE_CLIENT_EMAIL,
        "client_id": settings.FIREBASE_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}",
    }
    
    if not test_firebase_admin_connection(service_account_data):
        print("\n❌ Firebase Admin SDK 연결 실패!")
        create_new_service_account_guide()
        return
    
    print("\n✅ Firebase 설정 검증 완료!")
    print("\n🔥 실제 토큰으로 테스트하려면:")
    print("   1. Flutter 앱에서 Firebase ID 토큰 복사")
    print("   2. check_token_expiry('YOUR_TOKEN') 함수 실행")


if __name__ == "__main__":
    main()
