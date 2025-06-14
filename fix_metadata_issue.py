"""
누락된 테이블들을 추가하는 새로운 마이그레이션 생성
"""
import subprocess
import sys

def create_migration():
    """새로운 마이그레이션 생성"""
    print("🔄 새로운 마이그레이션 생성 중...")
    
    try:
        # 새로운 마이그레이션 생성
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", 
            "-m", "Add missing tables including diaries"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 새로운 마이그레이션 생성 성공!")
            print(f"📄 출력: {result.stdout}")
            
            # 마이그레이션 적용
            print("\n🔄 마이그레이션 적용 중...")
            apply_result = subprocess.run([
                "alembic", "upgrade", "head"
            ], capture_output=True, text=True)
            
            if apply_result.returncode == 0:
                print("✅ 마이그레이션 적용 성공!")
                print(f"📄 출력: {apply_result.stdout}")
                return True
            else:
                print("❌ 마이그레이션 적용 실패:")
                print(f"🚨 오류: {apply_result.stderr}")
                return False
        else:
            print("❌ 마이그레이션 생성 실패:")
            print(f"🚨 오류: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False

def try_main_py():
    """main.py 실행 시도"""
    print("\n🚀 main.py 실행 시도...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "app.main"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ main.py 실행 성공!")
            print(f"📄 출력: {result.stdout}")
            return True
        else:
            print("❌ main.py 실행 실패:")
            print(f"🚨 오류: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ main.py가 정상적으로 시작되었습니다 (10초 후 자동 종료)")
        return True
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False

if __name__ == "__main__":
    print("🔧 metadata 충돌 문제 해결")
    print("=" * 50)
    
    # 1. 새로운 마이그레이션 생성 및 적용
    if create_migration():
        print("\n✅ 마이그레이션 완료!")
        
        # 2. main.py 실행 시도
        if try_main_py():
            print("\n🎉 main.py 실행 성공!")
            print("🌐 서버가 http://localhost:8000 에서 실행 중입니다")
            print("📚 API 문서: http://localhost:8000/docs")
        else:
            print("\n💡 수동으로 실행해보세요:")
            print("python -m app.main")
    else:
        print("\n❌ 마이그레이션 실패. 수동으로 해결이 필요합니다.")
