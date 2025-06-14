"""
배포 스크립트
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent


class DeploymentManager:
    """배포 관리 클래스"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_root = PROJECT_ROOT
        self.project_id = "ai-diary-backend"  # Google Cloud Project ID
        self.service_name = "ai-diary-api"
        
    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """명령어 실행"""
        print(f"🔧 실행 중: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if check and result.returncode != 0:
            print(f"❌ 명령어 실행 실패: {command}")
            print(f"Error: {result.stderr}")
            sys.exit(1)
        
        return result
    
    def check_prerequisites(self) -> bool:
        """배포 전 필수 조건 확인"""
        print("📋 배포 전 필수 조건 확인 중...")
        
        # Docker 설치 확인
        try:
            self.run_command("docker --version")
            print("  ✅ Docker 설치 확인됨")
        except:
            print("  ❌ Docker가 설치되지 않았습니다")
            return False
        
        # Google Cloud CLI 확인 (Cloud Run 배포 시)
        if self.environment == "production":
            try:
                self.run_command("gcloud --version")
                print("  ✅ Google Cloud CLI 설치 확인됨")
            except:
                print("  ❌ Google Cloud CLI가 설치되지 않았습니다")
                return False
        
        # 환경 변수 파일 확인
        env_file = self.project_root / f".env.{self.environment}"
        if not env_file.exists():
            print(f"  ❌ 환경 변수 파일 없음: {env_file}")
            return False
        
        print("  ✅ .env 파일 확인됨")
        
        # 필수 파일들 확인
        required_files = ["Dockerfile", "requirements.txt", "app/main.py"]
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                print(f"  ❌ 필수 파일 없음: {file_path}")
                return False
        
        print("  ✅ 필수 파일들 확인됨")
        
        return True
    
    def run_tests(self) -> bool:
        """테스트 실행"""
        print("🧪 테스트 실행 중...")
        
        try:
            # 의존성 설치
            self.run_command("pip install -r requirements.txt")
            
            # 테스트 실행
            result = self.run_command("python -m pytest app/tests/ -v", check=False)
            
            if result.returncode == 0:
                print("✅ 모든 테스트 통과")
                return True
            else:
                print("❌ 테스트 실패")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            return False
    
    def build_docker_image(self) -> bool:
        """Docker 이미지 빌드"""
        print("🐳 Docker 이미지 빌드 중...")
        
        image_tag = f"{self.service_name}:{self.environment}"
        
        try:
            # Docker 이미지 빌드
            self.run_command(f"docker build -t {image_tag} .")
            print(f"✅ Docker 이미지 빌드 완료: {image_tag}")
            
            # 이미지 크기 확인
            result = self.run_command(f"docker images {image_tag} --format 'table {{.Size}}'")
            print(f"📦 이미지 크기: {result.stdout.strip()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Docker 이미지 빌드 실패: {e}")
            return False
    
    def deploy_to_local(self) -> bool:
        """로컬 배포 (Docker Compose)"""
        print("🏠 로컬 환경에 배포 중...")
        
        try:
            # 기존 컨테이너 중지
            self.run_command("docker-compose down", check=False)
            
            # 새로운 컨테이너 시작
            self.run_command("docker-compose up -d --build")
            
            print("✅ 로컬 배포 완료")
            print("🌐 서비스 URL: http://localhost:8000")
            print("📚 API 문서: http://localhost:8000/docs")
            
            return True
            
        except Exception as e:
            print(f"❌ 로컬 배포 실패: {e}")
            return False
    
    def deploy_to_cloud_run(self) -> bool:
        """Google Cloud Run에 배포"""
        print("☁️ Google Cloud Run에 배포 중...")
        
        try:
            # Google Cloud 프로젝트 설정
            self.run_command(f"gcloud config set project {self.project_id}")
            
            # Container Registry에 이미지 태그
            registry_url = f"gcr.io/{self.project_id}/{self.service_name}"
            self.run_command(f"docker tag {self.service_name}:{self.environment} {registry_url}")
            
            # 이미지 푸시
            self.run_command(f"docker push {registry_url}")
            
            # Cloud Run 서비스 배포
            deploy_command = f"""
            gcloud run deploy {self.service_name} \
                --image {registry_url} \
                --platform managed \
                --region asia-northeast1 \
                --allow-unauthenticated \
                --memory 2Gi \
                --cpu 2 \
                --max-instances 10 \
                --set-env-vars ENVIRONMENT={self.environment}
            """
            
            self.run_command(deploy_command)
            
            # 서비스 URL 확인
            result = self.run_command(
                f"gcloud run services describe {self.service_name} "
                f"--region=asia-northeast1 --format='value(status.url)'"
            )
            
            service_url = result.stdout.strip()
            
            print("✅ Cloud Run 배포 완료")
            print(f"🌐 서비스 URL: {service_url}")
            print(f"📚 API 문서: {service_url}/docs")
            
            return True
            
        except Exception as e:
            print(f"❌ Cloud Run 배포 실패: {e}")
            return False
    
    def setup_database(self) -> bool:
        """데이터베이스 설정"""
        print("🗄️ 데이터베이스 설정 중...")
        
        try:
            # Alembic 마이그레이션 실행
            self.run_command("alembic upgrade head")
            print("✅ 데이터베이스 마이그레이션 완료")
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 설정 실패: {e}")
            return False
    
    def create_secrets(self) -> bool:
        """시크릿 생성 (Cloud Run 배포 시)"""
        if self.environment != "production":
            return True
        
        print("🔐 시크릿 생성 중...")
        
        try:
            # 환경 변수 파일 읽기
            env_file = self.project_root / f".env.{self.environment}"
            
            with open(env_file, 'r') as f:
                env_vars = {}
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
            
            # Google Secret Manager에 시크릿 생성
            for key, value in env_vars.items():
                if key in ['DATABASE_URL', 'GEMINI_API_KEY', 'SECRET_KEY']:
                    secret_name = f"{self.service_name}-{key.lower().replace('_', '-')}"
                    
                    # 시크릿 생성 또는 업데이트
                    create_cmd = f"gcloud secrets create {secret_name} --data-file=-"
                    result = self.run_command(f"echo '{value}' | {create_cmd}", check=False)
                    
                    if result.returncode != 0:
                        # 이미 존재하면 업데이트
                        update_cmd = f"gcloud secrets versions add {secret_name} --data-file=-"
                        self.run_command(f"echo '{value}' | {update_cmd}")
            
            print("✅ 시크릿 생성 완료")
            return True
            
        except Exception as e:
            print(f"❌ 시크릿 생성 실패: {e}")
            return False
    
    def health_check(self, url: str) -> bool:
        """배포된 서비스 헬스 체크"""
        print("🏥 서비스 헬스 체크 중...")
        
        try:
            import requests
            
            # 헬스 체크 엔드포인트 호출
            response = requests.get(f"{url}/health", timeout=30)
            
            if response.status_code == 200:
                print("✅ 서비스 정상 동작 확인")
                return True
            else:
                print(f"❌ 서비스 상태 이상: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 헬스 체크 실패: {e}")
            return False
    
    def rollback(self) -> bool:
        """이전 버전으로 롤백"""
        print("🔄 이전 버전으로 롤백 중...")
        
        if self.environment == "production":
            try:
                # Cloud Run 이전 리비전으로 롤백
                self.run_command(
                    f"gcloud run services update-traffic {self.service_name} "
                    f"--to-revisions=LATEST=0 --region=asia-northeast1"
                )
                print("✅ 롤백 완료")
                return True
            except Exception as e:
                print(f"❌ 롤백 실패: {e}")
                return False
        else:
            # 로컬 환경은 이전 이미지로 재배포
            try:
                self.run_command("docker-compose down")
                self.run_command("docker-compose up -d")
                print("✅ 로컬 환경 재시작 완료")
                return True
            except Exception as e:
                print(f"❌ 로컬 환경 재시작 실패: {e}")
                return False
    
    def deploy(self, skip_tests: bool = False) -> bool:
        """전체 배포 프로세스"""
        print(f"🚀 {self.environment} 환경 배포 시작")
        print("="*50)
        
        # 1. 필수 조건 확인
        if not self.check_prerequisites():
            return False
        
        # 2. 테스트 실행 (선택적)
        if not skip_tests:
            if not self.run_tests():
                print("❌ 테스트 실패로 배포 중단")
                return False
        
        # 3. Docker 이미지 빌드
        if not self.build_docker_image():
            return False
        
        # 4. 환경별 배포
        if self.environment == "production":
            # 프로덕션 배포
            if not self.create_secrets():
                return False
            
            if not self.deploy_to_cloud_run():
                return False
            
            # 헬스 체크
            # service_url을 실제로 가져와야 함
            # if not self.health_check(service_url):
            #     self.rollback()
            #     return False
            
        else:
            # 로컬/개발 환경 배포
            if not self.deploy_to_local():
                return False
        
        # 5. 데이터베이스 설정
        if not self.setup_database():
            print("⚠️ 데이터베이스 설정 실패 (수동 확인 필요)")
        
        print("="*50)
        print("🎉 배포 완료!")
        print("="*50)
        
        return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="AI Diary Backend 배포 스크립트")
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="배포 환경"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="테스트 건너뛰기"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="이전 버전으로 롤백"
    )
    
    args = parser.parse_args()
    
    deployment_manager = DeploymentManager(args.env)
    
    try:
        if args.rollback:
            success = deployment_manager.rollback()
        else:
            success = deployment_manager.deploy(skip_tests=args.skip_tests)
        
        if success:
            print("✅ 작업 완료")
            sys.exit(0)
        else:
            print("❌ 작업 실패")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ 배포가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 배포 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
