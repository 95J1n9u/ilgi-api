#!/usr/bin/env python3
"""
Firebase 토큰 검증 문제 디버깅 스크립트
현재 서비스 계정 설정 상태를 확인하고 문제점을 찾습니다.
"""

import json
import base64
import requests
import os
from datetime import datetime, timezone


def check_firebase_env_vars():
    """Firebase 환경변수 확인"""
    print("🔍 Firebase 환경변수 확인")
    print("="*50)
    
    required_vars = [
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY_ID', 
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'FIREBASE_PRIVATE_KEY':
                print(f"✅ {var}: 설정됨 (길이: {len(value)})")
                # Private Key 형식 검증
                if not value.startswith("-----BEGIN PRIVATE KEY-----"):
                    print(f"❌ {var}: BEGIN 태그 없음")
                if not value.endswith("-----END PRIVATE KEY-----\