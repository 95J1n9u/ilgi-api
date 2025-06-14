#!/usr/bin/env python3
"""
Docker 환경에서 데이터베이스 연결 문제 진단 스크립트
"""
import os
import sys
import asyncio
from urllib.parse import urlparse

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_environment():
    """환경변수 확인"""
    print_section("환경변수 확인")
    
    # .env 파일 존재 확인
    env_file_exists = os.path.exists('.env')
    print(f"📁 .env 파일 존재: {env_file_exists}")
    
    if env_file_exists:
        try:
            with open('.env', 'r') as f:
                content = f.read()
                print(f"📄 .env 파일 크기: {len(content)} 문자")
                if 'DATABASE_URL' in content:
                    print("✅ .env 파일에 DATABASE_URL 발견")
                else:
                    print("❌ .env 파일에 DATABASE_URL 없음")
        except Exception as e:
            print(f"❌ .env 파일 읽기 실패: {e}")
    
    # 환경변수 직접 확인
    print(f"\n🔍 환경변수 직접 확인:")
    for var in ['DATABASE_URL', 'REDIS_URL', 'GEMINI_API_KEY', 'SECRET_KEY', 'DEBUG', 'ENVIRONMENT']:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var.upper() or 'KEY' in var.upper() or 'SECRET' in var.upper():
                print(f"  {var}: {'*' * min(len(value), 20)}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: ❌ 설정되지 않음")

def check_database_url():
    """DATABASE_URL 파싱 확인"""
    print_section("DATABASE_URL 분석")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않음")
        return False
    
    print(f"📍 원본 DATABASE_URL: {database_url}")
    
    try:
        parsed = urlparse(database_url)
        print(f"🔍 파싱 결과:")
        print(f"  스킴: {parsed.scheme}")
        print(f"  사용자명: {parsed.username}")
        print(f"  비밀번호: {'***' if parsed.password else 'None'}")
        print(f"  호스트: {parsed.hostname}")
        print(f"  포트: {parsed.port}")
        print(f"  데이터베이스: {parsed.path}")
        
        # Docker 환경 감지
        if parsed.hostname == 'localhost':
            print("⚠️ WARNING: Docker 환경에서 localhost 사용 중!")
            print("   Docker Compose에서는 서비스명(postgres)을 사용해야 합니다.")
        
        if not parsed.port:
            print("⚠️ WARNING: 포트가 명시되지 않음!")
            print("   PostgreSQL 기본 포트 5432를 명시하는 것을 권장합니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ URL 파싱 실패: {e}")
        return False

async def test_settings_loading():
    """설정 로딩 테스트"""
    print_section("설정 로딩 테스트")
    
    try:
        # python-dotenv로 .env 로드 확인
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ python-dotenv로 .env 로드 성공")
        except ImportError:
            print("⚠️ python-dotenv가 설치되지 않음")
        except Exception as e:
            print(f"❌ .env 로드 실패: {e}")
        
        # 설정 객체 생성 테스트
        from app.config.settings import get_settings
        settings = get_settings()
        
        print(f"✅ 설정 객체 생성 성공")
        print(f"  Environment: {settings.ENVIRONMENT}")
        print(f"  Debug: {settings.DEBUG}")
        print(f"  Database URL 설정됨: {bool(settings.DATABASE_URL)}")
        
        if settings.DATABASE_URL:
            # URL 마스킹해서 출력
            url = settings.DATABASE_URL
            if '@' in url:
                parts = url.split('@')
                masked_url = parts[0].split(':')[:-1] + ['***@'] + parts[1:]
                print(f"  Database URL: {''.join(masked_url)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 로딩 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connection():
    """데이터베이스 연결 테스트"""
    print_section("데이터베이스 연결 테스트")
    
    try:
        from app.config.database import test_database_connection, print_database_info
        
        # 설정 정보 출력
        print_database_info()
        
        # 연결 테스트
        print("\n🔍 비동기 연결 테스트 중...")
        result = await test_database_connection()
        
        if result:
            print("✅ 데이터베이스 연결 성공!")
        else:
            print("❌ 데이터베이스 연결 실패!")
        
        return result
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_docker_environment():
    """Docker 환경 확인"""
    print_section("Docker 환경 확인")
    
    # Docker 컨테이너 내부인지 확인
    docker_indicators = [
        os.path.exists('/.dockerenv'),
        os.path.exists('/proc/self/cgroup') and 'docker' in open('/proc/self/cgroup').read(),
        os.getenv('DOCKER_CONTAINER') == 'true'
    ]
    
    in_docker = any(docker_indicators)
    print(f"🐳 Docker 컨테이너 내부: {in_docker}")
    
    if in_docker:
        print("📋 Docker 환경에서 고려사항:")
        print("  - 데이터베이스 호스트는 'postgres' (서비스명) 사용")
        print("  - localhost 대신 Docker Compose 서비스명 사용")
        print("  - 포트는 내부 포트(5432) 사용")
    
    # 네트워크 연결 확인
    try:
        import socket
        
        # postgres 호스트 확인
        try:
            socket.gethostbyname('postgres')
            print("✅ 'postgres' 호스트명 해석 가능")
        except socket.gaierror:
            print("❌ 'postgres' 호스트명 해석 불가")
        
        # localhost 확인
        try:
            socket.gethostbyname('localhost')
            print("✅ 'localhost' 호스트명 해석 가능")
        except socket.gaierror:
            print("❌ 'localhost' 호스트명 해석 불가")
            
    except Exception as e:
        print(f"⚠️ 네트워크 확인 실패: {e}")

async def main():
    """메인 진단 함수"""
    print("🔍 AI Diary Backend - Docker 데이터베이스 연결 진단")
    print("=" * 60)
    
    # 순차적으로 진단 실행
    check_environment()
    check_database_url()
    check_docker_environment()
    
    settings_ok = await test_settings_loading()
    
    if settings_ok:
        db_ok = await test_database_connection()
    else:
        print("\n❌ 설정 로딩에 실패하여 데이터베이스 테스트를 건너뜁니다.")
        db_ok = False
    
    print_section("진단 결과 요약")
    
    if settings_ok and db_ok:
        print("🎉 모든 테스트 통과! 데이터베이스 연결이 정상입니다.")
        print("\n다음 단계:")
        print("1. Docker Compose 실행: docker-compose up -d")
        print("2. 서버 시작: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print("\n문제 해결 방법:")
        if not settings_ok:
            print("1. .env 파일이 올바르게 설정되었는지 확인")
            print("2. 필요한 환경변수가 모두 설정되었는지 확인")
        if not db_ok:
            print("3. Docker Compose가 실행 중인지 확인")
            print("4. postgres 서비스가 정상 실행 중인지 확인")
            print("5. DATABASE_URL의 호스트명이 'postgres'인지 확인")

if __name__ == "__main__":
    asyncio.run(main())
