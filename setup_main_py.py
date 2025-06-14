"""
main.py 실행을 위한 전체 설정 스크립트
PostgreSQL 설치 후 실행하는 완전한 가이드
"""
import subprocess
import sys
import os
import asyncio
from pathlib import Path

def run_command(command, description):
    """명령어 실행 및 결과 표시"""
    print(f"\n🔄 {description}")
    print(f"💻 실행 명령: {command}")
    
    try:
        if isinstance(command, list):
            result = subprocess.run(command, capture_output=True, text=True, cwd=Path.cwd())
        else:
            result = subprocess.run(command, capture_output=True, text=True, shell=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print(f"✅ 성공: {description}")
            if result.stdout:
                print(f"📤 출력: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 실패: {description}")
            if result.stderr:
                print(f"🚨 오류: {result.stderr.strip()}")
            if result.stdout:
                print(f"📤 출력: {result.stdout.strip()}")
            return False
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False

async def main():
    """main.py 실행을 위한 전체 설정 프로세스"""
    print("🚀 AI Diary Backend main.py 실행 준비")
    print("=" * 60)
    
    # 1. PostgreSQL 데이터베이스 설정
    print("\n📋 1단계: PostgreSQL 데이터베이스 설정")
    print("다음 명령어를 수동으로 실행하세요:")
    print("psql -U postgres -f setup_db.sql")
    
    input("위 명령어를 실행한 후 Enter를 눌러주세요...")
    
    # 2. 데이터베이스 연결 테스트
    print("\n📋 2단계: 데이터베이스 연결 테스트")
    if run_command([sys.executable, "test_db_connection.py"], "데이터베이스 연결 테스트"):
        print("✅ 데이터베이스 연결 성공!")
    else:
        print("❌ 데이터베이스 연결 실패. setup_db.sql을 다시 실행해주세요.")
        return
    
    # 3. 필요한 패키지 설치 확인
    print("\n📋 3단계: 필요한 패키지 확인")
    required_packages = ["asyncpg", "alembic", "fastapi", "google-generativeai"]
    
    for package in required_packages:
        if run_command([sys.executable, "-c", f"import {package}"], f"{package} 패키지 확인"):
            print(f"✅ {package} 설치됨")
        else:
            print(f"❌ {package} 미설치. 설치 중...")
            if not run_command([sys.executable, "-m", "pip", "install", package], f"{package} 설치"):
                print(f"❌ {package} 설치 실패")
                return
    
    # 4. Alembic 마이그레이션 실행
    print("\n📋 4단계: Alembic 마이그레이션 실행")
    if run_command(["alembic", "upgrade", "head"], "데이터베이스 테이블 생성"):
        print("✅ 마이그레이션 완료!")
    else:
        print("❌ 마이그레이션 실패")
        print("💡 다음을 확인해주세요:")
        print("   - PostgreSQL 서버가 실행 중인가?")
        print("   - 데이터베이스와 사용자가 올바르게 생성되었는가?")
        return
    
    # 5. Redis 확인 (선택사항)
    print("\n📋 5단계: Redis 확인 (선택사항)")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis 연결 성공")
    except Exception as e:
        print(f"⚠️ Redis 연결 실패: {e}")
        print("💡 Redis는 선택사항입니다. main.py 실행에는 필수가 아닙니다.")
    
    # 6. 환경변수 확인
    print("\n📋 6단계: 환경변수 확인")
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY 설정됨: {gemini_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        print("💡 .env 파일을 확인해주세요.")
    
    # 7. main.py 실행
    print("\n📋 7단계: main.py 실행")
    print("🚀 이제 main.py를 실행할 준비가 완료되었습니다!")
    print("\n다음 명령어로 실행하세요:")
    print("python -m app.main")
    print("\n또는:")
    print("cd app && python main.py")
    
    # 자동 실행 옵션
    auto_run = input("\n지금 바로 main.py를 실행하시겠습니까? (y/N): ")
    if auto_run.lower() == 'y':
        print("\n🚀 main.py 실행 중...")
        run_command([sys.executable, "-m", "app.main"], "main.py 실행")

if __name__ == "__main__":
    asyncio.run(main())
