"""
디버깅 및 테스트용 HTML 페이지 제공
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

@router.get("/debug", response_class=HTMLResponse)
async def debug_page():
    """
    API 디버깅 및 테스트용 HTML 페이지
    """
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 AI Diary Backend API 디버깅 도구</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 40px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 25px;
            background: #f9f9f9;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        
        .input-group input, .input-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .input-group input:focus, .input-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .response {
            background: #f5f5f5;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-top: 15px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .success {
            border-color: #4CAF50;
            background-color: #e8f5e8;
            color: #2e7d32;
        }
        
        .error {
            border-color: #f44336;
            background-color: #ffebee;
            color: #c62828;
        }
        
        .info {
            border-color: #2196F3;
            background-color: #e3f2fd;
            color: #1565c0;
        }
        
        .warning {
            border-color: #ff9800;
            background-color: #fff3e0;
            color: #ef6c00;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .status-200 { background: #4CAF50; color: white; }
        .status-401 { background: #f44336; color: white; }
        .status-500 { background: #9c27b0; color: white; }
        .status-503 { background: #ff9800; color: white; }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                margin: 10px;
                border-radius: 10px;
            }
            
            .header, .content {
                padding: 20px;
            }
        }
        
        .token-display {
            font-family: 'Courier New', monospace;
            font-size: 11px;
            background: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            word-break: break-all;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 AI Diary Backend API 디버깅 도구</h1>
            <p>실시간 API 테스트 및 디버깅 페이지</p>
            <p>Base URL: <strong>https://ilgi-api-production.up.railway.app</strong></p>
        </div>
        
        <div class="content">
            <!-- 환경 상태 확인 -->
            <div class="section">
                <h2>🌍 환경 상태 확인</h2>
                <button class="btn" onclick="checkHealth()">헬스체크</button>
                <button class="btn" onclick="checkStatus()">API 상태</button>
                <button class="btn" onclick="checkEnvironment()">환경변수 디버깅</button>
                <div id="envResponse" class="response info"></div>
            </div>
            
            <!-- Firebase 토큰 테스트 -->
            <div class="section">
                <h2>🔥 Firebase ID 토큰 테스트</h2>
                <div class="input-group">
                    <label for="firebaseToken">Firebase ID 토큰 입력:</label>
                    <textarea id="firebaseToken" rows="4" placeholder="Firebase ID 토큰을 여기에 붙여넣으세요 (eyJ...로 시작)"></textarea>
                </div>
                <button class="btn" onclick="testFirebaseToken()">Firebase 토큰 검증 및 JWT 발급</button>
                <div id="firebaseResponse" class="response"></div>
            </div>
            
            <!-- JWT 토큰 테스트 -->
            <div class="section">
                <h2>🔑 JWT 토큰 테스트</h2>
                <div class="input-group">
                    <label for="jwtToken">JWT 토큰:</label>
                    <textarea id="jwtToken" rows="4" placeholder="JWT 토큰을 여기에 붙여넣거나 위에서 발급받은 토큰이 자동으로 입력됩니다"></textarea>
                </div>
                <button class="btn" onclick="testJWTRefresh()">🔄 JWT 토큰 갱신</button>
                <button class="btn" onclick="testJWTValidate()">✅ JWT 토큰 검증</button>
                <button class="btn" onclick="testUserInfo()">👤 사용자 정보 조회</button>
                <button class="btn" onclick="decodeJWTToken()">🔍 JWT 토큰 디코딩</button>
                <div id="jwtResponse" class="response"></div>
            </div>
            
            <!-- 서버 설정 디버깅 -->
            <div class="section">
                <h2>🛠️ 서버 설정 디버깅</h2>
                <button class="btn" onclick="checkServerConfig()">📊 서버 설정 확인</button>
                <button class="btn" onclick="checkJWTConfig()">🔑 JWT 설정 확인</button>
                <div id="serverConfigResponse" class="response"></div>
            </div>
            
            <!-- 일기 분석 API 테스트 -->
            <div class="section">
                <h2>📝 일기 분석 API 테스트</h2>
                <div class="input-group">
                    <label for="diaryContent">일기 내용:</label>
                    <textarea id="diaryContent" rows="4" placeholder="분석할 일기 내용을 입력하세요">오늘은 친구들과 카페에서 즐거운 시간을 보냈다. 새로운 프로젝트에 대해 이야기하면서 많은 아이디어를 얻었고, 앞으로의 계획에 대해 설레는 마음이 든다.</textarea>
                </div>
                <button class="btn" onclick="testDiaryAnalysis()">일기 분석 실행</button>
                <div id="analysisResponse" class="response"></div>
            </div>
            
            <!-- 통합 테스트 -->
            <div class="section">
                <h2>🚀 통합 인증 플로우 테스트</h2>
                <p>Firebase 토큰 → JWT 발급 → 토큰 갱신 → 일기 분석 전체 플로우를 자동으로 테스트합니다.</p>
                <button class="btn" onclick="runFullTest()">전체 플로우 테스트 실행</button>
                <div id="fullTestResponse" class="response"></div>
            </div>
        </div>
    </div>

    <script>
        const BASE_URL = 'https://ilgi-api-production.up.railway.app';
        
        // 현재 JWT 토큰 저장
        let currentJWTToken = '';
        
        // API 호출 헬퍼 함수
        async function apiCall(url, options = {}) {
            try {
                const response = await fetch(url, {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                });
                
                const data = await response.text();
                let jsonData;
                try {
                    jsonData = JSON.parse(data);
                } catch {
                    jsonData = data;
                }
                
                return {
                    status: response.status,
                    data: jsonData,
                    success: response.ok
                };
            } catch (error) {
                return {
                    status: 0,
                    data: { error: error.message },
                    success: false
                };
            }
        }
        
        // 응답 표시 헬퍼 함수
        function displayResponse(elementId, response) {
            const element = document.getElementById(elementId);
            const statusBadge = `<span class="status-badge status-${response.status}">HTTP ${response.status}</span>`;
            const timestamp = new Date().toLocaleTimeString();
            
            let className = 'response ';
            if (response.success) {
                className += 'success';
            } else {
                className += 'error';
            }
            
            element.className = className;
            element.innerHTML = `${statusBadge} [${timestamp}]\\n\\n` + 
                              JSON.stringify(response.data, null, 2);
        }
        
        // 환경 상태 확인 함수들
        async function checkHealth() {
            const response = await apiCall(`${BASE_URL}/health`);
            displayResponse('envResponse', response);
        }
        
        async function checkStatus() {
            const response = await apiCall(`${BASE_URL}/api/v1/status`);
            displayResponse('envResponse', response);
        }
        
        async function checkEnvironment() {
            const response = await apiCall(`${BASE_URL}/api/v1/debug/env`);
            displayResponse('envResponse', response);
        }
        
        // Firebase 토큰 테스트
        async function testFirebaseToken() {
            const token = document.getElementById('firebaseToken').value.trim();
            if (!token) {
                alert('Firebase 토큰을 입력해주세요');
                return;
            }
            
            const response = await apiCall(`${BASE_URL}/api/v1/auth/verify-token`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.success && response.data.access_token) {
                currentJWTToken = response.data.access_token;
                document.getElementById('jwtToken').value = currentJWTToken;
                
                // JWT 토큰 표시
                response.data._jwt_token_preview = currentJWTToken.substring(0, 100) + '...';
            }
            
            displayResponse('firebaseResponse', response);
        }
        
        // JWT 토큰 테스트 함수들
        async function testJWTRefresh() {
            const token = document.getElementById('jwtToken').value.trim() || currentJWTToken;
            if (!token) {
                alert('JWT 토큰이 없습니다. 먼저 Firebase 토큰으로 JWT를 발급받아주세요.');
                return;
            }
            
            const response = await apiCall(`${BASE_URL}/api/v1/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.success && response.data.access_token) {
                currentJWTToken = response.data.access_token;
                document.getElementById('jwtToken').value = currentJWTToken;
                response.data._new_jwt_token_preview = currentJWTToken.substring(0, 100) + '...';
            }
            
            displayResponse('jwtResponse', response);
        }
        
        async function testJWTValidate() {
            const token = document.getElementById('jwtToken').value.trim() || currentJWTToken;
            if (!token) {
                alert('JWT 토큰이 없습니다.');
                return;
            }
            
            const response = await apiCall(`${BASE_URL}/api/v1/auth/validate`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            displayResponse('jwtResponse', response);
        }
        
        async function testUserInfo() {
            const token = document.getElementById('jwtToken').value.trim() || currentJWTToken;
            if (!token) {
                alert('JWT 토큰이 없습니다.');
                return;
            }
            
            const response = await apiCall(`${BASE_URL}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            displayResponse('jwtResponse', response);
        }
        
        // JWT 토큰 디코딩
        async function decodeJWTToken() {
            const token = document.getElementById('jwtToken').value.trim() || currentJWTToken;
            if (!token) {
                alert('JWT 토큰이 없습니다.');
                return;
            }
            
            const response = await apiCall(`${BASE_URL}/api/v1/debug/token-decode?token=${encodeURIComponent(token)}`);
            displayResponse('jwtResponse', response);
        }
        
        // 서버 설정 확인
        async function checkServerConfig() {
            const response = await apiCall(`${BASE_URL}/api/v1/debug/server-config`);
            displayResponse('serverConfigResponse', response);
        }
        
        async function checkJWTConfig() {
            const response = await apiCall(`${BASE_URL}/api/v1/debug/server-config`);
            
            // JWT 설정만 추출
            if (response.success && response.data.jwt_config) {
                const jwtConfigResponse = {
                    status: response.status,
                    data: {
                        jwt_config: response.data.jwt_config,
                        timestamp: response.data.timestamp
                    },
                    success: response.success
                };
                displayResponse('serverConfigResponse', jwtConfigResponse);
            } else {
                displayResponse('serverConfigResponse', response);
            }
        }
        
        // 일기 분석 테스트
        async function testDiaryAnalysis() {
            const token = document.getElementById('jwtToken').value.trim() || currentJWTToken;
            const content = document.getElementById('diaryContent').value.trim();
            
            if (!token) {
                alert('JWT 토큰이 없습니다. 먼저 인증을 완료해주세요.');
                return;
            }
            
            if (!content) {
                alert('일기 내용을 입력해주세요.');
                return;
            }
            
            const requestData = {
                diary_id: `test_diary_${Date.now()}`,
                content: content,
                metadata: {
                    date: new Date().toISOString().split('T')[0],
                    weather: "맑음",
                    activities: ["테스트"],
                    location: "디버깅 페이지"
                }
            };
            
            const response = await apiCall(`${BASE_URL}/api/v1/analysis/diary`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(requestData)
            });
            
            displayResponse('analysisResponse', response);
        }
        
        // 통합 테스트
        async function runFullTest() {
            const firebaseToken = document.getElementById('firebaseToken').value.trim();
            const element = document.getElementById('fullTestResponse');
            
            if (!firebaseToken) {
                alert('Firebase 토큰을 먼저 입력해주세요.');
                return;
            }
            
            element.className = 'response info';
            element.innerHTML = '🚀 통합 테스트 시작...\\n\\n';
            
            let log = '';
            
            try {
                // Step 1: Firebase 토큰으로 JWT 발급
                log += '📍 Step 1: Firebase ID 토큰 → JWT 토큰 교환\\n';
                const step1 = await apiCall(`${BASE_URL}/api/v1/auth/verify-token`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${firebaseToken}` }
                });
                
                log += `   Status: ${step1.status} ${step1.success ? '✅' : '❌'}\\n`;
                if (!step1.success) {
                    throw new Error('Firebase 토큰 검증 실패');
                }
                
                const jwtToken = step1.data.access_token;
                currentJWTToken = jwtToken;
                document.getElementById('jwtToken').value = jwtToken;
                log += `   JWT 토큰 발급 성공: ${jwtToken.substring(0, 50)}...\\n\\n`;
                
                // Step 2: JWT 토큰 갱신
                log += '📍 Step 2: JWT 토큰 갱신 테스트\\n';
                const step2 = await apiCall(`${BASE_URL}/api/v1/auth/refresh`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${jwtToken}` }
                });
                
                log += `   Status: ${step2.status} ${step2.success ? '✅' : '❌'}\\n`;
                if (step2.success) {
                    log += `   새 JWT 토큰: ${step2.data.access_token.substring(0, 50)}...\\n`;
                    currentJWTToken = step2.data.access_token;
                } else {
                    log += `   오류: ${JSON.stringify(step2.data)}\\n`;
                }
                log += '\\n';
                
                // Step 3: 사용자 정보 조회
                log += '📍 Step 3: 사용자 정보 조회\\n';
                const step3 = await apiCall(`${BASE_URL}/api/v1/auth/me`, {
                    headers: { 'Authorization': `Bearer ${currentJWTToken}` }
                });
                
                log += `   Status: ${step3.status} ${step3.success ? '✅' : '❌'}\\n`;
                if (step3.success) {
                    log += `   사용자 ID: ${step3.data.uid}\\n`;
                } else {
                    log += `   오류: ${JSON.stringify(step3.data)}\\n`;
                }
                log += '\\n';
                
                // Step 4: 일기 분석 API
                log += '📍 Step 4: 일기 분석 API 테스트\\n';
                const testDiary = {
                    diary_id: `full_test_${Date.now()}`,
                    content: '통합 테스트용 일기입니다. 오늘은 API 디버깅을 했습니다.',
                    metadata: {
                        date: new Date().toISOString().split('T')[0],
                        weather: '맑음',
                        activities: ['디버깅'],
                        location: '디버깅 페이지'
                    }
                };
                
                const step4 = await apiCall(`${BASE_URL}/api/v1/analysis/diary`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${currentJWTToken}` },
                    body: JSON.stringify(testDiary)
                });
                
                log += `   Status: ${step4.status} ${step4.success ? '✅' : '❌'}\\n`;
                if (step4.success) {
                    log += `   분석 완료! 감정: ${step4.data.emotions || 'N/A'}\\n`;
                } else {
                    log += `   오류: ${JSON.stringify(step4.data)}\\n`;
                }
                
                // 최종 결과
                log += '\\n🎯 통합 테스트 완료!\\n';
                const successCount = [step1, step2, step3, step4].filter(s => s.success).length;
                log += `성공: ${successCount}/4 단계\\n`;
                
                if (successCount === 4) {
                    element.className = 'response success';
                    log += '\\n🎉 모든 테스트 통과! 인증 시스템이 정상 작동합니다.';
                } else {
                    element.className = 'response warning';
                    log += '\\n⚠️ 일부 테스트 실패. 위 로그를 확인해주세요.';
                }
                
            } catch (error) {
                element.className = 'response error';
                log += `\\n❌ 테스트 중 오류 발생: ${error.message}`;
            }
            
            element.innerHTML = log;
        }
        
        // 페이지 로드 시 기본 환경 체크
        window.onload = function() {
            checkHealth();
            checkServerConfig();
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@router.get("/token-decode")
async def decode_token(token: str):
    """
    JWT 토큰 디코딩 디버깅 API
    """
    try:
        import time
        from jose import jwt
        from app.config.settings import get_settings
        
        settings = get_settings()
        
        # 토큰을 디코딩하지 말고 헤더만 파싱
        try:
            header = jwt.get_unverified_header(token)
        except Exception:
            # jose에서 지원하지 않으면 수동으로 파싱
            import base64
            import json
            header_data = token.split('.')[0]
            # Base64 디코딩
            header_data += '=' * (4 - len(header_data) % 4)
            header = json.loads(base64.b64decode(header_data))
        
        # 토큰을 검증 없이 디코딩
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
        except Exception:
            # 수동 파싱
            import base64
            import json
            payload_data = token.split('.')[1]
            payload_data += '=' * (4 - len(payload_data) % 4)
            unverified_payload = json.loads(base64.b64decode(payload_data))
        
        # 실제 검증 시도
        try:
            verified_payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            verification_status = "VALID"
            verification_error = None
        except jwt.ExpiredSignatureError:
            verification_status = "EXPIRED"
            verification_error = "Token has expired"
            verified_payload = None
        except jwt.InvalidTokenError as e:
            verification_status = "INVALID"
            verification_error = str(e)
            verified_payload = None
        except Exception as e:
            verification_status = "ERROR"
            verification_error = str(e)
            verified_payload = None
        
        return {
            "token_preview": token[:50] + "...",
            "header": header,
            "unverified_payload": unverified_payload,
            "time_info": {
                "current_timestamp": int(time.time()),
                "token_issued_at": unverified_payload.get("iat"),
                "token_expires_at": unverified_payload.get("exp"),
                "token_subject": unverified_payload.get("sub"),
                "time_until_expiry_seconds": unverified_payload.get("exp", 0) - int(time.time()) if unverified_payload.get("exp") else None,
                "is_expired": unverified_payload.get("exp", 0) < int(time.time()) if unverified_payload.get("exp") else None
            },
            "verification": {
                "status": verification_status,
                "error": verification_error,
                "verified_payload": verified_payload
            },
            "server_config": {
                "algorithm": settings.ALGORITHM,
                "secret_key_present": bool(settings.SECRET_KEY),
                "secret_key_length": len(settings.SECRET_KEY) if settings.SECRET_KEY else 0,
                "secret_key_preview": settings.SECRET_KEY[:10] + "..." if settings.SECRET_KEY else None
            },
            "timestamp": "2025-06-15T02:31:31Z"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "token_preview": token[:50] + "...",
            "message": "토큰 디코딩 중 오류 발생"
        }


@router.get("/server-config")
async def get_server_config():
    """
    서버 설정 상태 확인 API
    """
    from app.config.settings import get_settings
    from app.core.security import firebase_initialized
    import os
    
    settings = get_settings()
    
    return {
        "jwt_config": {
            "algorithm": settings.ALGORITHM,
            "secret_key_present": bool(settings.SECRET_KEY),
            "secret_key_length": len(settings.SECRET_KEY) if settings.SECRET_KEY else 0,
            "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        },
        "firebase_config": {
            "initialized": firebase_initialized,
            "project_id_present": bool(settings.FIREBASE_PROJECT_ID),
            "use_firebase": settings.USE_FIREBASE
        },
        "environment": {
            "debug": settings.DEBUG,
            "environment": settings.ENVIRONMENT,
            "railway_env": os.getenv("RAILWAY_ENVIRONMENT"),
            "port": os.getenv("PORT")
        },
        "api_keys": {
            "gemini_api_present": bool(settings.GEMINI_API_KEY)
        },
        "timestamp": "2025-06-15T02:31:31Z"
    }
