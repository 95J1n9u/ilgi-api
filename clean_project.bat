@echo off
chcp 65001 >nul
echo ========================================
echo  AI Diary Backend Project Cleanup
echo ========================================
echo.

REM Check if we're in the project root
if not exist "app\main.py" (
    echo [ERROR] Please run from project root directory.
    echo app\main.py file not found.
    pause
    exit /b 1
)

echo [INFO] Project root directory confirmed: %CD%
echo.

set /a "delete_count=0"
set /a "deleted_count=0"

echo [STEP 1] Checking files to delete...
echo.

REM Count files to delete first
echo [Test Server Files]
if exist "cors_test_server.py" (
    echo   + cors_test_server.py
    set /a delete_count+=1
)
if exist "fixed_test_server.py" (
    echo   + fixed_test_server.py
    set /a delete_count+=1
)
if exist "gemini_test_server.py" (
    echo   + gemini_test_server.py
    set /a delete_count+=1
)
if exist "improved_test_server.py" (
    echo   + improved_test_server.py
    set /a delete_count+=1
)
if exist "simple_test_server.py" (
    echo   + simple_test_server.py
    set /a delete_count+=1
)
if exist "test_server.py" (
    echo   + test_server.py
    set /a delete_count+=1
)

echo.
echo [Temp Scripts]
if exist "emergency_fix.py" (
    echo   + emergency_fix.py
    set /a delete_count+=1
)
if exist "fix_metadata_issue.py" (
    echo   + fix_metadata_issue.py
    set /a delete_count+=1
)
if exist "main_gemini_only.py" (
    echo   + main_gemini_only.py
    set /a delete_count+=1
)
if exist "quick_start.py" (
    echo   + quick_start.py
    set /a delete_count+=1
)
if exist "run_without_firebase.py" (
    echo   + run_without_firebase.py
    set /a delete_count+=1
)
if exist "simplified_main.py" (
    echo   + simplified_main.py
    set /a delete_count+=1
)

echo.
echo [Setup Scripts]
if exist "setup_environment.py" (
    echo   + setup_environment.py
    set /a delete_count+=1
)
if exist "setup_main_py.py" (
    echo   + setup_main_py.py
    set /a delete_count+=1
)

echo.
echo [Test Files]
if exist "test_analysis_api.py" (
    echo   + test_analysis_api.py
    set /a delete_count+=1
)
if exist "test_db_connection.py" (
    echo   + test_db_connection.py
    set /a delete_count+=1
)
if exist "test_railway_config.py" (
    echo   + test_railway_config.py
    set /a delete_count+=1
)

echo.
echo [Railway Files]
if exist ".env.railway" (
    echo   + .env.railway
    set /a delete_count+=1
)
if exist "deploy_to_railway.py" (
    echo   + deploy_to_railway.py
    set /a delete_count+=1
)
if exist "railway.json" (
    echo   + railway.json
    set /a delete_count+=1
)
if exist "RAILWAY_DEPLOYMENT_SUCCESS.md" (
    echo   + RAILWAY_DEPLOYMENT_SUCCESS.md
    set /a delete_count+=1
)
if exist "RAILWAY_DEPLOY_GUIDE.md" (
    echo   + RAILWAY_DEPLOY_GUIDE.md
    set /a delete_count+=1
)

echo.
echo [Dockerfile Variants]
if exist "Dockerfile.optimized" (
    echo   + Dockerfile.optimized
    set /a delete_count+=1
)
if exist "Dockerfile.original" (
    echo   + Dockerfile.original
    set /a delete_count+=1
)
if exist "Dockerfile.railway" (
    echo   + Dockerfile.railway
    set /a delete_count+=1
)

echo.
echo [Requirements Variants]
if exist "requirements-minimal.txt" (
    echo   + requirements-minimal.txt
    set /a delete_count+=1
)
if exist "requirements-production.txt" (
    echo   + requirements-production.txt
    set /a delete_count+=1
)

echo.
echo [Misc Files]
if exist "build-optimized.sh" (
    echo   + build-optimized.sh
    set /a delete_count+=1
)
if exist "install.bat" (
    echo   + install.bat
    set /a delete_count+=1
)
if exist "testweb.html" (
    echo   + testweb.html
    set /a delete_count+=1
)
if exist "CORS_FIX_GUIDE.md" (
    echo   + CORS_FIX_GUIDE.md
    set /a delete_count+=1
)
if exist "QUICK_START.md" (
    echo   + QUICK_START.md
    set /a delete_count+=1
)
if exist "cleanup_project.py" (
    echo   + cleanup_project.py
    set /a delete_count+=1
)
if exist "PROJECT_CLEANUP_GUIDE.md" (
    echo   + PROJECT_CLEANUP_GUIDE.md
    set /a delete_count+=1
)

echo.
echo [App Directory Files]
if exist "app\main_railway.py" (
    echo   + app\main_railway.py
    set /a delete_count+=1
)
if exist "app\config\settings_production.py" (
    echo   + app\config\settings_production.py
    set /a delete_count+=1
)
if exist "app\tests" (
    echo   + app\tests directory
    set /a delete_count+=1
)

echo.
echo [INFO] Found %delete_count% files to delete
echo.

if %delete_count%==0 (
    echo [INFO] No files to delete. Project is already clean.
    goto :verify_project
)

set /p confirm="Delete %delete_count% files? Type 'y' to continue: "
if /i not "%confirm%"=="y" (
    echo [CANCELLED] File deletion cancelled.
    pause
    exit /b 0
)

echo.
echo [STEP 2] Deleting files...
echo.

REM Delete files one by one
if exist "cors_test_server.py" (
    del "cors_test_server.py" 2>nul
    if not exist "cors_test_server.py" (
        echo   - Deleted: cors_test_server.py
        set /a deleted_count+=1
    )
)

if exist "fixed_test_server.py" (
    del "fixed_test_server.py" 2>nul
    if not exist "fixed_test_server.py" (
        echo   - Deleted: fixed_test_server.py
        set /a deleted_count+=1
    )
)

if exist "gemini_test_server.py" (
    del "gemini_test_server.py" 2>nul
    if not exist "gemini_test_server.py" (
        echo   - Deleted: gemini_test_server.py
        set /a deleted_count+=1
    )
)

if exist "improved_test_server.py" (
    del "improved_test_server.py" 2>nul
    if not exist "improved_test_server.py" (
        echo   - Deleted: improved_test_server.py
        set /a deleted_count+=1
    )
)

if exist "simple_test_server.py" (
    del "simple_test_server.py" 2>nul
    if not exist "simple_test_server.py" (
        echo   - Deleted: simple_test_server.py
        set /a deleted_count+=1
    )
)

if exist "test_server.py" (
    del "test_server.py" 2>nul
    if not exist "test_server.py" (
        echo   - Deleted: test_server.py
        set /a deleted_count+=1
    )
)

if exist "emergency_fix.py" (
    del "emergency_fix.py" 2>nul
    if not exist "emergency_fix.py" (
        echo   - Deleted: emergency_fix.py
        set /a deleted_count+=1
    )
)

if exist "fix_metadata_issue.py" (
    del "fix_metadata_issue.py" 2>nul
    if not exist "fix_metadata_issue.py" (
        echo   - Deleted: fix_metadata_issue.py
        set /a deleted_count+=1
    )
)

if exist "main_gemini_only.py" (
    del "main_gemini_only.py" 2>nul
    if not exist "main_gemini_only.py" (
        echo   - Deleted: main_gemini_only.py
        set /a deleted_count+=1
    )
)

if exist "quick_start.py" (
    del "quick_start.py" 2>nul
    if not exist "quick_start.py" (
        echo   - Deleted: quick_start.py
        set /a deleted_count+=1
    )
)

if exist "run_without_firebase.py" (
    del "run_without_firebase.py" 2>nul
    if not exist "run_without_firebase.py" (
        echo   - Deleted: run_without_firebase.py
        set /a deleted_count+=1
    )
)

if exist "simplified_main.py" (
    del "simplified_main.py" 2>nul
    if not exist "simplified_main.py" (
        echo   - Deleted: simplified_main.py
        set /a deleted_count+=1
    )
)

if exist "setup_environment.py" (
    del "setup_environment.py" 2>nul
    if not exist "setup_environment.py" (
        echo   - Deleted: setup_environment.py
        set /a deleted_count+=1
    )
)

if exist "setup_main_py.py" (
    del "setup_main_py.py" 2>nul
    if not exist "setup_main_py.py" (
        echo   - Deleted: setup_main_py.py
        set /a deleted_count+=1
    )
)

if exist "test_analysis_api.py" (
    del "test_analysis_api.py" 2>nul
    if not exist "test_analysis_api.py" (
        echo   - Deleted: test_analysis_api.py
        set /a deleted_count+=1
    )
)

if exist "test_db_connection.py" (
    del "test_db_connection.py" 2>nul
    if not exist "test_db_connection.py" (
        echo   - Deleted: test_db_connection.py
        set /a deleted_count+=1
    )
)

if exist "test_railway_config.py" (
    del "test_railway_config.py" 2>nul
    if not exist "test_railway_config.py" (
        echo   - Deleted: test_railway_config.py
        set /a deleted_count+=1
    )
)

if exist ".env.railway" (
    del ".env.railway" 2>nul
    if not exist ".env.railway" (
        echo   - Deleted: .env.railway
        set /a deleted_count+=1
    )
)

if exist "deploy_to_railway.py" (
    del "deploy_to_railway.py" 2>nul
    if not exist "deploy_to_railway.py" (
        echo   - Deleted: deploy_to_railway.py
        set /a deleted_count+=1
    )
)

if exist "railway.json" (
    del "railway.json" 2>nul
    if not exist "railway.json" (
        echo   - Deleted: railway.json
        set /a deleted_count+=1
    )
)

if exist "RAILWAY_DEPLOYMENT_SUCCESS.md" (
    del "RAILWAY_DEPLOYMENT_SUCCESS.md" 2>nul
    if not exist "RAILWAY_DEPLOYMENT_SUCCESS.md" (
        echo   - Deleted: RAILWAY_DEPLOYMENT_SUCCESS.md
        set /a deleted_count+=1
    )
)

if exist "RAILWAY_DEPLOY_GUIDE.md" (
    del "RAILWAY_DEPLOY_GUIDE.md" 2>nul
    if not exist "RAILWAY_DEPLOY_GUIDE.md" (
        echo   - Deleted: RAILWAY_DEPLOY_GUIDE.md
        set /a deleted_count+=1
    )
)

if exist "Dockerfile.optimized" (
    del "Dockerfile.optimized" 2>nul
    if not exist "Dockerfile.optimized" (
        echo   - Deleted: Dockerfile.optimized
        set /a deleted_count+=1
    )
)

if exist "Dockerfile.original" (
    del "Dockerfile.original" 2>nul
    if not exist "Dockerfile.original" (
        echo   - Deleted: Dockerfile.original
        set /a deleted_count+=1
    )
)

if exist "Dockerfile.railway" (
    del "Dockerfile.railway" 2>nul
    if not exist "Dockerfile.railway" (
        echo   - Deleted: Dockerfile.railway
        set /a deleted_count+=1
    )
)

if exist "requirements-minimal.txt" (
    del "requirements-minimal.txt" 2>nul
    if not exist "requirements-minimal.txt" (
        echo   - Deleted: requirements-minimal.txt
        set /a deleted_count+=1
    )
)

if exist "requirements-production.txt" (
    del "requirements-production.txt" 2>nul
    if not exist "requirements-production.txt" (
        echo   - Deleted: requirements-production.txt
        set /a deleted_count+=1
    )
)

if exist "build-optimized.sh" (
    del "build-optimized.sh" 2>nul
    if not exist "build-optimized.sh" (
        echo   - Deleted: build-optimized.sh
        set /a deleted_count+=1
    )
)

if exist "install.bat" (
    del "install.bat" 2>nul
    if not exist "install.bat" (
        echo   - Deleted: install.bat
        set /a deleted_count+=1
    )
)

if exist "testweb.html" (
    del "testweb.html" 2>nul
    if not exist "testweb.html" (
        echo   - Deleted: testweb.html
        set /a deleted_count+=1
    )
)

if exist "CORS_FIX_GUIDE.md" (
    del "CORS_FIX_GUIDE.md" 2>nul
    if not exist "CORS_FIX_GUIDE.md" (
        echo   - Deleted: CORS_FIX_GUIDE.md
        set /a deleted_count+=1
    )
)

if exist "QUICK_START.md" (
    del "QUICK_START.md" 2>nul
    if not exist "QUICK_START.md" (
        echo   - Deleted: QUICK_START.md
        set /a deleted_count+=1
    )
)

if exist "cleanup_project.py" (
    del "cleanup_project.py" 2>nul
    if not exist "cleanup_project.py" (
        echo   - Deleted: cleanup_project.py
        set /a deleted_count+=1
    )
)

if exist "PROJECT_CLEANUP_GUIDE.md" (
    del "PROJECT_CLEANUP_GUIDE.md" 2>nul
    if not exist "PROJECT_CLEANUP_GUIDE.md" (
        echo   - Deleted: PROJECT_CLEANUP_GUIDE.md
        set /a deleted_count+=1
    )
)

if exist "app\main_railway.py" (
    del "app\main_railway.py" 2>nul
    if not exist "app\main_railway.py" (
        echo   - Deleted: app\main_railway.py
        set /a deleted_count+=1
    )
)

if exist "app\config\settings_production.py" (
    del "app\config\settings_production.py" 2>nul
    if not exist "app\config\settings_production.py" (
        echo   - Deleted: app\config\settings_production.py
        set /a deleted_count+=1
    )
)

if exist "app\tests" (
    set /p confirm_tests="Delete app\tests directory? (y/n): "
    if /i "%confirm_tests%"=="y" (
        rmdir /s /q "app\tests" 2>nul
        if not exist "app\tests" (
            echo   - Deleted: app\tests directory
            set /a deleted_count+=1
        )
    ) else (
        echo   - Skipped: app\tests directory
    )
)

echo.
echo [COMPLETED] %deleted_count% files deleted.
echo.

:verify_project
echo [STEP 3] Verifying project...
echo.

echo [Essential Files Check]
set /a "missing_files=0"

if exist "app\main.py" (
    echo   + app\main.py
) else (
    echo   - app\main.py ^(MISSING!^)
    set /a missing_files+=1
)

if exist "app\config\settings.py" (
    echo   + app\config\settings.py
) else (
    echo   - app\config\settings.py ^(MISSING!^)
    set /a missing_files+=1
)

if exist "requirements.txt" (
    echo   + requirements.txt
) else (
    echo   - requirements.txt ^(MISSING!^)
    set /a missing_files+=1
)

if exist "Dockerfile" (
    echo   + Dockerfile
) else (
    echo   - Dockerfile ^(MISSING!^)
    set /a missing_files+=1
)

if exist ".env.example" (
    echo   + .env.example
) else (
    echo   - .env.example ^(MISSING!^)
    set /a missing_files+=1
)

if exist "README.md" (
    echo   + README.md
) else (
    echo   - README.md ^(MISSING!^)
    set /a missing_files+=1
)

echo.
if %missing_files%==0 (
    echo [SUCCESS] All essential files exist!
) else (
    echo [WARNING] %missing_files% essential files are missing.
)

echo.
echo ========================================
echo  Project Cleanup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Setup environment variables ^(.env file^)
echo 2. Test server: python app/main.py
echo 3. Test Flutter connection
echo 4. Deploy if needed
echo.

pause
