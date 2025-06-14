#!/bin/bash
# AI 일기 분석 백엔드 - 프로젝트 정리 스크립트 (Linux/Mac)
# 불필요한 테스트 파일들 및 임시 파일들 삭제

echo "========================================"
echo " AI 일기 분석 백엔드 프로젝트 정리"
echo "========================================"
echo

# 현재 디렉토리가 프로젝트 루트인지 확인
if [ ! -f "app/main.py" ]; then
    echo "[오류] 프로젝트 루트 디렉토리에서 실행해주세요."
    echo "app/main.py 파일이 없습니다."
    exit 1
fi

echo "[정보] 프로젝트 루트 디렉토리 확인됨: $(pwd)"
echo

# 삭제할 파일들 정의
declare -a test_servers=(
    "cors_test_server.py"
    "fixed_test_server.py"
    "gemini_test_server.py"
    "improved_test_server.py"
    "simple_test_server.py"
    "test_server.py"
)

declare -a temp_scripts=(
    "emergency_fix.py"
    "fix_metadata_issue.py"
    "main_gemini_only.py"
    "quick_start.py"
    "run_without_firebase.py"
    "simplified_main.py"
)

declare -a setup_scripts=(
    "setup_environment.py"
    "setup_main_py.py"
)

declare -a test_files=(
    "test_analysis_api.py"
    "test_db_connection.py"
    "test_railway_config.py"
)

declare -a railway_files=(
    ".env.railway"
    "deploy_to_railway.py"
    "railway.json"
    "RAILWAY_DEPLOYMENT_SUCCESS.md"
    "RAILWAY_DEPLOY_GUIDE.md"
)

declare -a dockerfile_variants=(
    "Dockerfile.optimized"
    "Dockerfile.original"
    "Dockerfile.railway"
)

declare -a requirements_variants=(
    "requirements-minimal.txt"
    "requirements-production.txt"
)

declare -a misc_files=(
    "build-optimized.sh"
    "install.bat"
    "testweb.html"
    "CORS_FIX_GUIDE.md"
    "QUICK_START.md"
    "cleanup_project.py"
    "PROJECT_CLEANUP_GUIDE.md"
)

declare -a app_files=(
    "app/main_railway.py"
    "app/config/settings_production.py"
)

# 삭제할 파일들 확인
echo "[1단계] 삭제할 파일들 확인 중..."
echo

delete_count=0

function check_files() {
    local category="$1"
    shift
    local files=("$@")
    
    echo "[$category]"
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✓ $file"
            ((delete_count++))
        else
            echo "  - $file (없음)"
        fi
    done
    echo
}

check_files "테스트 서버 파일들" "${test_servers[@]}"
check_files "임시/테스트 스크립트들" "${temp_scripts[@]}"
check_files "설정 스크립트들" "${setup_scripts[@]}"
check_files "테스트 파일들" "${test_files[@]}"
check_files "Railway 전용 파일들" "${railway_files[@]}"
check_files "Dockerfile 변형들" "${dockerfile_variants[@]}"
check_files "Requirements 변형들" "${requirements_variants[@]}"
check_files "기타 불필요한 파일들" "${misc_files[@]}"
check_files "app 디렉토리 내 파일들" "${app_files[@]}"

# app/tests 디렉토리 확인
if [ -d "app/tests" ]; then
    echo "[app/tests 디렉토리]"
    echo "  ✓ app/tests 디렉토리"
    ((delete_count++))
    echo
fi

echo "[정보] 삭제할 파일 총 $delete_count개 발견"
echo

if [ $delete_count -eq 0 ]; then
    echo "[정보] 삭제할 파일이 없습니다. 프로젝트가 이미 정리되어 있습니다."
    echo
    verify_project
    exit 0
fi

# 사용자 확인
echo "[확인] $delete_count개 파일을 삭제하시겠습니까?"
read -p "계속하려면 'y'를 입력하세요 (y/n): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "[취소] 파일 삭제가 취소되었습니다."
    exit 0
fi

echo
echo "[2단계] 파일 삭제 중..."
echo

# 실제 파일 삭제
deleted_count=0

function delete_files() {
    local files=("$@")
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            if rm "$file" 2>/dev/null; then
                echo "  ✓ 삭제됨: $file"
                ((deleted_count++))
            else
                echo "  ✗ 삭제 실패: $file"
            fi
        fi
    done
}

delete_files "${test_servers[@]}"
delete_files "${temp_scripts[@]}"
delete_files "${setup_scripts[@]}"
delete_files "${test_files[@]}"
delete_files "${railway_files[@]}"
delete_files "${dockerfile_variants[@]}"
delete_files "${requirements_variants[@]}"
delete_files "${misc_files[@]}"
delete_files "${app_files[@]}"

# app/tests 디렉토리 삭제 (신중히)
if [ -d "app/tests" ]; then
    echo
    echo "[주의] app/tests 디렉토리가 발견되었습니다."
    read -p "app/tests 디렉토리를 삭제하시겠습니까? (y/n): " confirm_tests
    if [[ "$confirm_tests" =~ ^[Yy]$ ]]; then
        if rm -rf "app/tests" 2>/dev/null; then
            echo "  ✓ 삭제됨: app/tests 디렉토리"
            ((deleted_count++))
        else
            echo "  ✗ 삭제 실패: app/tests 디렉토리"
        fi
    else
        echo "  - 건너뜀: app/tests 디렉토리"
    fi
fi

echo
echo "[완료] 총 $deleted_count개 파일이 삭제되었습니다."
echo

# 프로젝트 검증
function verify_project() {
    echo "[3단계] 프로젝트 검증 중..."
    echo
    
    # 필수 파일들 확인
    echo "[필수 파일 확인]"
    missing_files=0
    
    essential_files=(
        "app/main.py"
        "app/config/settings.py"
        "requirements.txt"
        "Dockerfile"
        ".env.example"
        "PROJECT_GUIDE.md"
        "README.md"
    )
    
    for file in "${essential_files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✓ $file"
        else
            echo "  ✗ $file (누락!)"
            ((missing_files++))
        fi
    done
    
    echo
    if [ $missing_files -eq 0 ]; then
        echo "[성공] 모든 필수 파일이 존재합니다!"
    else
        echo "[경고] $missing_files개 필수 파일이 누락되었습니다."
    fi
    
    echo
    echo "[4단계] 최종 프로젝트 구조"
    echo
    echo "남은 주요 파일들:"
    ls -la | grep -v __pycache__ | grep -v .git | grep -v venv
    
    echo
    echo "========================================"
    echo " 프로젝트 정리 완료!"
    echo "========================================"
    echo
    echo "다음 단계:"
    echo "1. 환경변수 설정 (.env 파일)"
    echo "2. 서버 실행 테스트: python app/main.py"
    echo "3. Flutter 앱 연결 테스트"
    echo "4. 필요시 배포"
    echo
}

verify_project
