"""
개선된 디버깅 페이지 - Firebase 토큰 에러 해결
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/debug-fixed", response_class=HTMLResponse)
async def debug_page_fixed():
    """
    개선된 API 디버깅 페이지 - Firebase 토큰 에러 해결
    """
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 AI Diary Backend - 개선된 디버깅 도구</title>
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
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
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
        
        .token-info {
            background: #e3f2fd;
            border: 1px solid #2196F3;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
        }
        
        .token-validation {
            background: #fff3e0;
            border: 1px solid #ff9800;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
        }
        
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 AI Diary Backend - 개선된 디버깅 도구</h1>
            <p>Firebase 토큰 에러 해결 및 실시간 API 테스트</p>
            <p>Base URL: <strong>https://ilgi-api-production.up.railway.app</strong></p>
        </div>
        
        <div class="content">
            <!-- 서버 상태 확인 -->
            <div class="section">
                <h2>🌍 서버 상태 확인</h2>
                <button class="btn" onclick="checkServerStatus()">서버 상태 확인</button>
                <div id="serverStatus" class="response info">서버 상태를 확인 중...</div>
            </div>
            
            <!-- Firebase 토큰 테스트 (개선됨) -->
            <div class="section">
                <h2>🔥 Firebase ID 토큰 테스트 (개선됨)</h2>
                <div class="input-group">
                    <label for="firebaseToken">Firebase ID 토큰 입력:</label>
                    <textarea id="firebaseToken" rows="4" placeholder="Firebase ID 토큰을 여기에 붙여넣으세요 (eyJ...로 시작)" 
                              oninput="validateFirebaseToken()"></textarea>
                    <div id="tokenValidation" class="token-validation" style="display: none;"></div>
                </div>
                
                <button class="btn" id="testFirebaseBtn" onclick="testFirebaseTokenSafe()" disabled>
                    🔒 Firebase 토큰 검증 및 JWT 발급
                </button>
                <button class="btn" onclick="clearFirebaseToken()">❌ 초기화</button>
                
                <div class="token-info">
                    <strong>💡 토큰 입력 가이드:</strong><br>
                    • Firebase ID 토큰은 'eyJ'로 시작해야 합니다<br>
                    • 공백이나 줄바꿈이 자동으로 제거됩니다<br>
                    • 토큰 형식이 올바르면 버튼이 활성화됩니다
                </div>
                
                <div id="firebaseResponse" class="response"></div>
            </div>
            
            <!-- JWT 토큰 테스트 -->
            <div class="section">
                <h2>🔑 JWT 토큰 테스트</h2>
                <div class="input-group">
                    <label for="jwtToken">JWT 토큰:</label>
                    <textarea id="jwtToken" rows="4" placeholder="JWT 토큰이 자동으로 입력됩니다" 
                              oninput="validateJWTToken()"></textarea>
                    <div id="jwtValidation" class="token-validation" style="display: none;"></div>
                </div>
                
                <button class="btn" id="refreshJWTBtn" onclick="refreshJWTToken()" disabled>🔄 JWT 토큰 갱신</button>
                <button class="btn" id="validateJWTBtn" onclick="validateJWTTokenAPI()" disabled>✅ JWT 토큰 검증</button>
                <button class="btn" id="userInfoBtn" onclick="getUserInfo()" disabled>👤 사용자 정보</button>
                
                <div id="jwtResponse" class="response"></div>
            </div>
            
            <!-- 일기 분석 테스트 -->
            <div class="section">
                <h2>📝 일기 분석 API 테스트</h2>
                <div class="input-group">
                    <label for="diaryContent">일기 내용:</label>
                    <textarea id="diaryContent" rows="3">오늘은 친구들과 카페에서 즐거운 시간을 보냈다. 새로운 프로젝트에 대해 이야기하면서 많은 아이디어를 얻었고, 앞으로의 계획에 대해 설레는 마음이 든다.</textarea>
                </div>
                
                <button class="btn" id="analyzeBtn" onclick="analyzeDiary()" disabled>📊 일기 분석 실행</button>
                
                <div id="analysisResponse" class="response"></div>
            </div>
            
            <!-- 통합 테스트 -->
            <div class="section">
                <h2>🚀 통합 인증 플로우 테스트</h2>
                <p>Firebase 토큰 → JWT 발급 → 토큰 갱신 → 일기 분석 전체 플로우를 자동으로 테스트합니다.</p>
                <button class="btn" id="fullTestBtn" onclick="runFullAuthFlow()" disabled>전체 플로우 테스트</button>
                <div id="fullTestResponse" class="response"></div>
            </div>
        </div>
    </div>

    <script>
        const BASE_URL = 'https://ilgi-api-production.up.railway.app';
        let currentJWTToken = '';
        let isLoading = false;
        
        // 토큰 검증 함수들
        function validateFirebaseToken() {
            const input = document.getElementById('firebaseToken');
            const validation = document.getElementById('tokenValidation');
            const button = document.getElementById('testFirebaseBtn');
            
            let token = input.value.trim();
            
            // 자동으로 공백과 줄바꿈 제거
            token = token.replace(/\\s+/g, '');
            input.value = token;
            
            if (!token) {
                validation.style.display = 'none';
                button.disabled = true;
                return;
            }
            
            validation.style.display = 'block';
            
            if (token.startsWith('eyJ')) {
                // JWT 형식 기본 검증
                const parts = token.split('.');
                if (parts.length === 3) {
                    validation.innerHTML = '✅ 올바른 토큰 형식입니다.';
                    validation.className = 'token-validation success';
                    button.disabled = false;
                } else {
                    validation.innerHTML = '❌ 토큰 형식이 올바르지 않습니다. (3개 부분으로 구성되어야 함)';
                    validation.className = 'token-validation error';
                    button.disabled = true;
                }
            } else {
                validation.innerHTML = '❌ Firebase ID 토큰은 "eyJ"로 시작해야 합니다.';
                validation.className = 'token-validation error';
                button.disabled = true;
            }
        }
        
        function validateJWTToken() {
            const input = document.getElementById('jwtToken');
            const validation = document.getElementById('jwtValidation');
            const buttons = ['refreshJWTBtn', 'validateJWTBtn', 'userInfoBtn', 'analyzeBtn', 'fullTestBtn'];
            
            const token = input.value.trim();
            
            if (!token) {
                validation.style.display = 'none';
                buttons.forEach(id => document.getElementById(id).disabled = true);
                return;
            }
            
            validation.style.display = 'block';
            
            if (token.startsWith('eyJ')) {
                validation.innerHTML = '✅ JWT 토큰이 감지되었습니다.';
                validation.className = 'token-validation success';
                buttons.forEach(id => document.getElementById(id).disabled = false);
                currentJWTToken = token;
            } else {
                validation.innerHTML = '❌ JWT 토큰 형식이 올바르지 않습니다.';
                validation.className = 'token-validation error';
                buttons.forEach(id => document.getElementById(id).disabled = true);
            }
        }
        
        function clearFirebaseToken() {
            document.getElementById('firebaseToken').value = '';
            document.getElementById('jwtToken').value = '';
            document.getElementById('tokenValidation').style.display = 'none';
            document.getElementById('jwtValidation').style.display = 'none';
            document.getElementById('firebaseResponse').innerHTML = '';
            document.getElementById('jwtResponse').innerHTML = '';
            validateFirebaseToken();
            validateJWTToken();
        }
        
        // 안전한 API 호출 함수
        async function safeApiCall(url, options = {}) {
            if (isLoading) {
                return { status: 0, data: { error: "이미 요청이 진행 중입니다." }, success: false };
            }
            
            isLoading = true;
            setLoadingState(true);
            
            try {
                // URL 검증
                if (!url || typeof url !== 'string') {
                    throw new Error('Invalid URL');
                }
                
                // 옵션 검증 및 정리
                const safeOptions = {
                    method: options.method || 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                };
                
                // Authorization 헤더 특별 처리
                if (options.headers && options.headers.Authorization) {
                    const authValue = options.headers.Authorization;
                    if (typeof authValue === 'string' && authValue.trim()) {
                        safeOptions.headers.Authorization = authValue.trim();
                    }
                }
                
                // body 추가 (있는 경우)
                if (options.body) {
                    if (typeof options.body === 'object') {
                        safeOptions.body = JSON.stringify(options.body);
                    } else {
                        safeOptions.body = options.body;
                    }
                }
                
                console.log('🔍 API 호출:', url, safeOptions);
                
                const response = await fetch(url, safeOptions);
                const data = await response.text();
                
                let jsonData;
                try {
                    jsonData = JSON.parse(data);
                } catch {
                    jsonData = { response: data };
                }
                
                return {
                    status: response.status,
                    data: jsonData,
                    success: response.ok,
                    url: url
                };
                
            } catch (error) {
                console.error('❌ API 호출 에러:', error);
                return {
                    status: 0,
                    data: { 
                        error: error.message,
                        type: error.name,
                        details: '네트워크 연결 또는 요청 형식에 문제가 있습니다.'
                    },
                    success: false,
                    url: url
                };
            } finally {
                isLoading = false;
                setLoadingState(false);
            }
        }
        
        function setLoadingState(loading) {
            const container = document.querySelector('.container');
            if (loading) {
                container.classList.add('loading');
            } else {
                container.classList.remove('loading');
            }
        }
        
        // 응답 표시 함수
        function displayResponse(elementId, response) {
            const element = document.getElementById(elementId);
            if (!element) return;
            
            const statusBadge = `<span class="status-badge status-${response.status}">HTTP ${response.status}</span>`;
            const timestamp = new Date().toLocaleTimeString();
            const urlInfo = response.url ? `URL: ${response.url}\\n` : '';
            
            let className = 'response ';
            if (response.success) {
                className += 'success';
            } else {
                className += 'error';
            }
            
            element.className = className;
            element.innerHTML = `${statusBadge} [${timestamp}]\\n${urlInfo}\\n` + 
                              JSON.stringify(response.data, null, 2);
        }
        
        // API 테스트 함수들
        async function checkServerStatus() {
            displayResponse('serverStatus', await safeApiCall(`${BASE_URL}/health`));
        }
        
        async function testFirebaseTokenSafe() {
            const token = document.getElementById('firebaseToken').value.trim().replace(/\\s+/g, '');
            
            if (!token) {
                alert('Firebase 토큰을 입력해주세요.');
                return;
            }
            
            const response = await safeApiCall(`${BASE_URL}/api/v1/auth/verify-token`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.success && response.data.access_token) {
                currentJWTToken = response.data.access_token;
                document.getElementById('jwtToken').value = currentJWTToken;
                validateJWTToken();
                
                // 성공 메시지 추가
                response.data._jwt_preview = currentJWTToken.substring(0, 100) + '...';
                response.data._success_message = 'JWT 토큰이 성공적으로 발급되었습니다!';
            }
            
            displayResponse('firebaseResponse', response);
        }
        
        async function refreshJWTToken() {
            const token = currentJWTToken || document.getElementById('jwtToken').value.trim();
            
            if (!token) {
                alert('JWT 토큰이 없습니다.');
                return;
            }
            
            const response = await safeApiCall(`${BASE_URL}/api/v1/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.success && response.data.access_token) {
                currentJWTToken = response.data.access_token;
                document.getElementById('jwtToken').value = currentJWTToken;
                response.data._new_jwt_preview = currentJWTToken.substring(0, 100) + '...';
            }
            
            displayResponse('jwtResponse', response);
        }
        
        async function validateJWTTokenAPI() {
            const token = currentJWTToken || document.getElementById('jwtToken').value.trim();
            
            const response = await safeApiCall(`${BASE_URL}/api/v1/auth/validate`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            displayResponse('jwtResponse', response);
        }
        
        async function getUserInfo() {
            const token = currentJWTToken || document.getElementById('jwtToken').value.trim();
            
            const response = await safeApiCall(`${BASE_URL}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            displayResponse('jwtResponse', response);
        }
        
        async function analyzeDiary() {
            const token = currentJWTToken || document.getElementById('jwtToken').value.trim();
            const content = document.getElementById('diaryContent').value.trim();
            
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
                    activities: ["디버깅"],
                    location: "디버깅 페이지"
                }
            };
            
            const response = await safeApiCall(`${BASE_URL}/api/v1/analysis/diary`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: requestData
            });
            
            displayResponse('analysisResponse', response);
        }
        
        async function runFullAuthFlow() {
            const firebaseToken = document.getElementById('firebaseToken').value.trim().replace(/\\s+/g, '');
            const element = document.getElementById('fullTestResponse');
            
            if (!firebaseToken) {
                alert('Firebase 토큰을 먼저 입력해주세요.');
                return;
            }
            
            element.className = 'response info';
            element.innerHTML = '🚀 통합 인증 플로우 테스트 시작...\\n\\n';
            
            let log = '';
            let successCount = 0;
            
            try {
                // Step 1: Firebase → JWT
                log += '📍 Step 1: Firebase ID 토큰 → JWT 토큰 교환\\n';
                const step1 = await safeApiCall(`${BASE_URL}/api/v1/auth/verify-token`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${firebaseToken}` }
                });
                
                log += `   Status: ${step1.status} ${step1.success ? '✅' : '❌'}\\n`;
                if (step1.success) {
                    successCount++;
                    currentJWTToken = step1.data.access_token;
                    document.getElementById('jwtToken').value = currentJWTToken;
                    validateJWTToken();
                    log += `   JWT 발급 성공: ${currentJWTToken.substring(0, 50)}...\\n`;
                } else {
                    log += `   에러: ${JSON.stringify(step1.data)}\\n`;
                }
                log += '\\n';
                
                if (!step1.success) throw new Error('JWT 발급 실패');
                
                // Step 2: JWT 갱신
                log += '📍 Step 2: JWT 토큰 갱신\\n';
                const step2 = await safeApiCall(`${BASE_URL}/api/v1/auth/refresh`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${currentJWTToken}` }
                });
                
                log += `   Status: ${step2.status} ${step2.success ? '✅' : '❌'}\\n`;
                if (step2.success) {
                    successCount++;
                    if (step2.data.access_token) {
                        currentJWTToken = step2.data.access_token;
                        log += `   새 JWT: ${currentJWTToken.substring(0, 50)}...\\n`;
                    }
                } else {
                    log += `   에러: ${JSON.stringify(step2.data)}\\n`;
                }
                log += '\\n';
                
                // Step 3: 사용자 정보
                log += '📍 Step 3: 사용자 정보 조회\\n';
                const step3 = await safeApiCall(`${BASE_URL}/api/v1/auth/me`, {
                    headers: { 'Authorization': `Bearer ${currentJWTToken}` }
                });
                
                log += `   Status: ${step3.status} ${step3.success ? '✅' : '❌'}\\n`;
                if (step3.success) {
                    successCount++;
                    log += `   사용자 정보 조회 성공\\n`;
                } else {
                    log += `   에러: ${JSON.stringify(step3.data)}\\n`;
                }
                log += '\\n';
                
                // Step 4: 일기 분석
                log += '📍 Step 4: 일기 분석 API\\n';
                const testDiary = {
                    diary_id: `full_test_${Date.now()}`,
                    content: '통합 테스트용 일기입니다. 오늘은 API 디버깅을 성공적으로 완료했습니다!',
                    metadata: {
                        date: new Date().toISOString().split('T')[0],
                        weather: '맑음',
                        activities: ['디버깅', '테스트'],
                        location: '디버깅 페이지'
                    }
                };
                
                const step4 = await safeApiCall(`${BASE_URL}/api/v1/analysis/diary`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${currentJWTToken}` },
                    body: testDiary
                });
                
                log += `   Status: ${step4.status} ${step4.success ? '✅' : '❌'}\\n`;
                if (step4.success) {
                    successCount++;
                    log += `   일기 분석 완료!\\n`;
                } else {
                    log += `   에러: ${JSON.stringify(step4.data)}\\n`;
                }
                
                // 최종 결과
                log += `\\n🎯 통합 테스트 완료! 성공: ${successCount}/4 단계\\n`;
                
                if (successCount === 4) {
                    element.className = 'response success';
                    log += '\\n🎉 모든 테스트 통과! 인증 시스템이 완벽하게 작동합니다.';
                } else if (successCount >= 2) {
                    element.className = 'response warning';
                    log += '\\n⚠️ 일부 테스트 실패. 기본 인증은 작동하지만 개선이 필요합니다.';
                } else {
                    element.className = 'response error';
                    log += '\\n❌ 테스트 실패. 인증 시스템에 문제가 있습니다.';
                }
                
            } catch (error) {
                element.className = 'response error';
                log += `\\n❌ 테스트 중 치명적 오류: ${error.message}`;
            }
            
            element.innerHTML = log;
        }
        
        // 페이지 로드 시 초기화
        window.onload = function() {
            checkServerStatus();
            validateFirebaseToken();
            validateJWTToken();
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)
