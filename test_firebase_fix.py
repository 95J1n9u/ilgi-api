#!/usr/bin/env python3
"""
Firebase 중복 초기화 문제 해결 테스트
"""
import os
import sys
import logging

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_firebase_initialization():
    """Firebase 초기화 테스트"""
    print("🧪 Firebase 중복 초기화 문제 해결 테스트")
    print("=" * 50)
    
    try:
        # 1. 첫 번째 import - security.py 모듈 로드
        print("\n1️⃣ security.py 모듈 로드 테스트...")
        from app.core.security import firebase_initialized
        print(f"   └─ 첫 번째 로드 후 firebase_initialized: {firebase_initialized}")
        
        # 2. initialize_firebase 함수 import
        print("\n2️⃣ initialize_firebase 함수 import...")
        from app.core.security import initialize_firebase
        print("   └─ initialize_firebase 함수 import 성공")
        
        # 3. 명시적 초기화 호출
        print("\n3️⃣ 명시적 Firebase 초기화...")
        result1 = initialize_firebase()
        print(f"   └─ 첫 번째 초기화 결과: {result1}")
        
        # 4. 중복 호출 테스트
        print("\n4️⃣ 중복 초기화 호출 테스트...")
        result2 = initialize_firebase()
        print(f"   └─ 두 번째 초기화 결과: {result2}")
        
        # 5. 다른 모듈에서 import 테스트
        print("\n5️⃣ 다른 모듈에서 import 테스트...")
        from app.core.security import get_firebase_status
        status = get_firebase_status()
        print(f"   └─ Firebase 상태: {status}")
        
        print("\n✅ 모든 테스트 완료!")
        print(f"   최종 firebase_initialized 상태: {firebase_initialized}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        print(f"   오류 타입: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_app_startup():
    """앱 시작 시뮬레이션 테스트"""
    print("\n🚀 앱 시작 시뮬레이션 테스트")
    print("=" * 50)
    
    try:
        # main.py의 lifespan 함수와 유사한 로직 테스트
        print("\n1️⃣ main.py lifespan 시뮬레이션...")
        
        from app.core.security import initialize_firebase, firebase_initialized
        firebase_success = initialize_firebase()
        
        if firebase_success and firebase_initialized:
            print("   └─ ✅ Firebase 초기화 완료")
        else:
            print("   └─ ℹ️ Firebase 비활성화 모드 - 서버는 정상 구동")
        
        print("\n2️⃣ 환경 설정 확인...")
        from app.config.settings import get_settings
        settings = get_settings()
        
        print(f"   └─ DEBUG: {settings.DEBUG}")
        print(f"   └─ ENVIRONMENT: {settings.ENVIRONMENT}")
        print(f"   └─ USE_FIREBASE: {settings.USE_FIREBASE}")
        print(f"   └─ FIREBASE_PROJECT_ID: {'✅ 설정됨' if settings.FIREBASE_PROJECT_ID else '❌ 없음'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 앱 시작 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Firebase 중복 초기화 문제 해결 검증")
    print("=" * 60)
    
    # 테스트 실행
    test1_result = test_firebase_initialization()
    test2_result = test_app_startup()
    
    print("\n📊 테스트 결과 요약")
    print("=" * 30)
    print(f"Firebase 초기화 테스트: {'✅ 성공' if test1_result else '❌ 실패'}")
    print(f"앱 시작 테스트: {'✅ 성공' if test2_result else '❌ 실패'}")
    
    if test1_result and test2_result:
        print("\n🎉 모든 테스트 성공! Firebase 중복 초기화 문제 해결됨")
        sys.exit(0)
    else:
        print("\n⚠️ 일부 테스트 실패. 추가 확인 필요")
        sys.exit(1)
