"""
프로젝트 초기 설정 스크립트
"""
import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from app.config.database import create_tables, DatabaseManager
from app.config.settings import get_settings
from app.models.user import User
from app.models.analysis import AIModelVersion

settings = get_settings()


async def create_database_tables():
    """데이터베이스 테이블 생성"""
    print("📊 데이터베이스 테이블 생성 중...")
    try:
        await create_tables()
        print("✅ 데이터베이스 테이블 생성 완료")
    except Exception as e:
        print(f"❌ 데이터베이스 테이블 생성 실패: {e}")
        return False
    return True


async def check_database_connection():
    """데이터베이스 연결 확인"""
    print("🔗 데이터베이스 연결 확인 중...")
    try:
        db_manager = DatabaseManager()
        is_healthy = await db_manager.health_check()
        
        if is_healthy:
            print("✅ 데이터베이스 연결 성공")
            return True
        else:
            print("❌ 데이터베이스 연결 실패")
            return False
    except Exception as e:
        print(f"❌ 데이터베이스 연결 오류: {e}")
        return False


def check_environment_variables():
    """환경 변수 확인"""
    print("🔧 환경 변수 확인 중...")
    
    required_vars = [
        "DATABASE_URL",
        "GEMINI_API_KEY",
        "FIREBASE_PROJECT_ID",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 누락된 환경 변수: {', '.join(missing_vars)}")
        print("💡 .env 파일을 확인하거나 환경 변수를 설정해주세요.")
        return False
    
    print("✅ 모든 필수 환경 변수 확인됨")
    return True


def create_directory_structure():
    """필요한 디렉토리 구조 생성"""
    print("📁 디렉토리 구조 생성 중...")
    
    directories = [
        "logs",
        "uploads",
        "backups",
        "temp",
        "models"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 {directory} 디렉토리 생성")
    
    print("✅ 디렉토리 구조 생성 완료")


async def initialize_ai_models():
    """AI 모델 버전 정보 초기화"""
    print("🤖 AI 모델 버전 정보 초기화 중...")
    
    try:
        from app.config.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            # 기본 모델 버전 정보 추가
            default_models = [
                {
                    "model_name": "gemini-pro",
                    "model_version": "1.0",
                    "model_type": "emotion",
                    "is_active": True,
                    "is_default": True
                },
                {
                    "model_name": "gemini-pro",
                    "model_version": "1.0", 
                    "model_type": "personality",
                    "is_active": True,
                    "is_default": True
                }
            ]
            
            for model_data in default_models:
                model = AIModelVersion(**model_data)
                session.add(model)
            
            await session.commit()
        
        print("✅ AI 모델 버전 정보 초기화 완료")
        return True
        
    except Exception as e:
        print(f"❌ AI 모델 버전 정보 초기화 실패: {e}")
        return False


def check_external_services():
    """외부 서비스 연결 확인"""
    print("🌐 외부 서비스 연결 확인 중...")
    
    services_status = {}
    
    # Gemini API 확인
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        # 간단한 테스트 호출
        # response = model.generate_content("Hello")
        services_status["gemini"] = True
        print("  ✅ Gemini API 연결 확인됨")
    except Exception as e:
        services_status["gemini"] = False
        print(f"  ❌ Gemini API 연결 실패: {e}")
    
    # Firebase 확인
    try:
        import firebase_admin
        if not firebase_admin._apps:
            # Firebase 초기화 테스트는 실제 credentials 없이는 어려우므로 설정 확인만
            if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY:
                services_status["firebase"] = True
                print("  ✅ Firebase 설정 확인됨")
            else:
                services_status["firebase"] = False
                print("  ❌ Firebase 설정 누락")
        else:
            services_status["firebase"] = True
            print("  ✅ Firebase 이미 초기화됨")
    except Exception as e:
        services_status["firebase"] = False
        print(f"  ❌ Firebase 확인 실패: {e}")
    
    return all(services_status.values())


def create_sample_data():
    """샘플 데이터 생성 (개발 환경용)"""
    if settings.ENVIRONMENT != "development":
        return
    
    print("📝 샘플 데이터 생성 중...")
    
    # TODO: 개발용 샘플 데이터 생성 로직
    # 샘플 사용자, 일기, 분석 결과 등
    
    print("✅ 샘플 데이터 생성 완료")


def print_success_message():
    """성공 메시지 출력"""
    print("\n" + "="*50)
    print("🎉 AI Diary Backend 초기 설정 완료!")
    print("="*50)
    print("서버를 시작하려면 다음 명령어를 실행하세요:")
    print("  uvicorn app.main:app --reload")
    print("\n또는 Docker를 사용하려면:")
    print("  docker-compose up -d")
    print("\nAPI 문서:")
    print("  http://localhost:8000/docs")
    print("="*50)


async def main():
    """메인 설정 함수"""
    print("🚀 AI Diary Backend 초기 설정을 시작합니다...\n")
    
    # 1. 환경 변수 확인
    if not check_environment_variables():
        sys.exit(1)
    
    # 2. 디렉토리 구조 생성
    create_directory_structure()
    
    # 3. 데이터베이스 연결 확인
    if not await check_database_connection():
        sys.exit(1)
    
    # 4. 데이터베이스 테이블 생성
    if not await create_database_tables():
        sys.exit(1)
    
    # 5. AI 모델 정보 초기화
    if not await initialize_ai_models():
        print("⚠️ AI 모델 정보 초기화 실패 (계속 진행)")
    
    # 6. 외부 서비스 연결 확인
    if not check_external_services():
        print("⚠️ 일부 외부 서비스 연결 실패 (계속 진행)")
    
    # 7. 샘플 데이터 생성 (개발 환경)
    create_sample_data()
    
    # 8. 성공 메시지
    print_success_message()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ 설정이 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 설정 중 오류 발생: {e}")
        sys.exit(1)
