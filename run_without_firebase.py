"""
Firebase 없이 main.py를 실행하기 위한 임시 스크립트
"""
import sys
import os

# security.py의 Firebase import를 우회하기 위한 mock
class MockFirebaseAdmin:
    _apps = []
    
    def initialize_app(self, cred):
        pass
    
    class auth:
        @staticmethod
        def verify_id_token(token):
            return {
                "uid": "test_user_123",
                "email": "test@example.com", 
                "name": "Test User",
                "email_verified": True
            }
    
    class credentials:
        @staticmethod
        def Certificate(config):
            return "mock_credential"

# Mock firebase_admin module
sys.modules['firebase_admin'] = MockFirebaseAdmin()
sys.modules['firebase_admin.auth'] = MockFirebaseAdmin.auth
sys.modules['firebase_admin.credentials'] = MockFirebaseAdmin.credentials

# Mock other missing modules
class MockJose:
    class JWTError(Exception):
        pass
    
    class jwt:
        @staticmethod
        def encode(payload, key, algorithm):
            return "mock_jwt_token"
        
        @staticmethod 
        def decode(token, key, algorithms):
            return {"sub": "test_user", "email": "test@example.com"}

sys.modules['jose'] = MockJose()

class MockPasslib:
    class CryptContext:
        def __init__(self, schemes, deprecated):
            pass
        
        def verify(self, password, hash):
            return True
        
        def hash(self, password):
            return "mock_hash"
    
    class context:
        CryptContext = CryptContext

sys.modules['passlib'] = MockPasslib()
sys.modules['passlib.context'] = MockPasslib.context

class MockStructlog:
    @staticmethod
    def get_logger():
        class MockLogger:
            def info(self, *args, **kwargs):
                print(f"INFO: {args} {kwargs}")
            def error(self, *args, **kwargs):
                print(f"ERROR: {args} {kwargs}")
        return MockLogger()

sys.modules['structlog'] = MockStructlog()

# 이제 main.py import 시도
try:
    from app.main import app
    import uvicorn
    
    print("🚀 Firebase 없이 서버 실행 중...")
    print("📝 Mock 인증을 사용합니다 (개발용)")
    print("🌐 http://localhost:8000/docs 에서 API 테스트 가능")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
    
except Exception as e:
    print(f"❌ 서버 실행 실패: {e}")
    print("💡 전체 패키지 설치를 권장합니다:")
    print("   pip install -r requirements.txt")
