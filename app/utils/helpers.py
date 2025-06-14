"""
유틸리티 헬퍼 함수들
"""
import hashlib
import secrets
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import re
import json

import structlog

logger = structlog.get_logger()


def generate_analysis_id() -> str:
    """분석 ID 생성"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(4)
    return f"analysis_{timestamp}_{random_suffix}"


def generate_unique_id(prefix: str = "") -> str:
    """고유 ID 생성"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_secure_token(length: int = 32) -> str:
    """보안 토큰 생성"""
    return secrets.token_urlsafe(length)


def generate_random_string(length: int = 8, include_numbers: bool = True) -> str:
    """랜덤 문자열 생성"""
    letters = string.ascii_letters
    if include_numbers:
        letters += string.digits
    return ''.join(secrets.choice(letters) for _ in range(length))


def hash_string(text: str, salt: str = "") -> str:
    """문자열 해싱"""
    combined = f"{text}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


def validate_uuid(uuid_string: str) -> bool:
    """UUID 형식 검증"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def clean_text(text: str) -> str:
    """텍스트 정제"""
    if not text:
        return ""
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    # 연속된 공백을 하나로 줄임
    text = re.sub(r'\s+', ' ', text)
    
    # 특수 문자 제거 (선택적)
    # text = re.sub(r'[^\w\s가-힣]', '', text)
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트 길이 제한"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, min_length: int = 2, max_keywords: int = 10) -> List[str]:
    """간단한 키워드 추출"""
    if not text:
        return []
    
    # 한글, 영문, 숫자만 추출
    words = re.findall(r'[가-힣a-zA-Z0-9]+', text.lower())
    
    # 길이 필터링
    words = [word for word in words if len(word) >= min_length]
    
    # 빈도수 계산
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # 빈도수 순으로 정렬하여 상위 키워드 반환
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_words[:max_keywords]]


def calculate_text_statistics(text: str) -> Dict[str, Any]:
    """텍스트 통계 계산"""
    if not text:
        return {
            "character_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "avg_sentence_length": 0,
            "avg_word_length": 0
        }
    
    # 문자 수
    character_count = len(text)
    
    # 단어 수 (한글, 영문 기준)
    words = re.findall(r'[가-힣a-zA-Z]+', text)
    word_count = len(words)
    
    # 문장 수
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # 문단 수
    paragraphs = text.split('\n\n')
    paragraph_count = len([p for p in paragraphs if p.strip()])
    
    # 평균 계산
    avg_sentence_length = character_count / sentence_count if sentence_count > 0 else 0
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    return {
        "character_count": character_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "avg_word_length": round(avg_word_length, 2)
    }


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """날짜 시간 포맷팅"""
    if not dt:
        return ""
    return dt.strftime(format_str)


def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """문자열을 datetime으로 파싱"""
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None


def get_time_ago(dt: datetime) -> str:
    """상대적 시간 표현 (예: 2시간 전)"""
    if not dt:
        return "알 수 없음"
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}일 전"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}시간 전"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"


def calculate_age_from_birthdate(birthdate: datetime) -> int:
    """생년월일로부터 나이 계산"""
    today = datetime.now()
    age = today.year - birthdate.year
    
    # 생일이 지나지 않았으면 1살 빼기
    if today.month < birthdate.month or \
       (today.month == birthdate.month and today.day < birthdate.day):
        age -= 1
    
    return age


def mask_email(email: str) -> str:
    """이메일 마스킹"""
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked_local = local
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone_number(phone: str) -> str:
    """전화번호 마스킹"""
    if not phone:
        return phone
    
    # 숫자만 추출
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) >= 8:
        # 뒤 4자리 제외하고 마스킹
        masked = digits[:-4] + '****'
        return masked
    
    return phone


def sanitize_filename(filename: str) -> str:
    """파일명 정제"""
    if not filename:
        return "untitled"
    
    # 위험한 문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 연속된 점 제거
    filename = re.sub(r'\.+', '.', filename)
    
    # 앞뒤 점과 공백 제거
    filename = filename.strip('. ')
    
    # 최대 길이 제한
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename or "untitled"


def format_file_size(size_bytes: int) -> str:
    """파일 크기 포맷팅"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def calculate_similarity(text1: str, text2: str) -> float:
    """간단한 텍스트 유사도 계산 (Jaccard similarity)"""
    if not text1 or not text2:
        return 0.0
    
    # 단어 집합 생성
    words1 = set(re.findall(r'[가-힣a-zA-Z0-9]+', text1.lower()))
    words2 = set(re.findall(r'[가-힣a-zA-Z0-9]+', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard 유사도
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """점수 정규화"""
    return max(min_val, min(max_val, score))


def calculate_confidence_interval(values: List[float], confidence: float = 0.95) -> tuple:
    """신뢰구간 계산"""
    if not values:
        return (0.0, 0.0)
    
    import statistics
    
    mean = statistics.mean(values)
    
    if len(values) == 1:
        return (mean, mean)
    
    std_dev = statistics.stdev(values)
    n = len(values)
    
    # t-분포 대신 정규분포 근사 사용 (간단화)
    z_score = 1.96 if confidence == 0.95 else 2.58  # 95% 또는 99%
    margin_of_error = z_score * (std_dev / (n ** 0.5))
    
    return (mean - margin_of_error, mean + margin_of_error)


def create_slug(text: str, max_length: int = 50) -> str:
    """URL 슬러그 생성"""
    if not text:
        return ""
    
    # 소문자 변환
    slug = text.lower()
    
    # 한글은 그대로, 영문숫자는 유지, 나머지는 하이픈으로
    slug = re.sub(r'[^\w가-힣-]', '-', slug)
    
    # 연속된 하이픈을 하나로
    slug = re.sub(r'-+', '-', slug)
    
    # 앞뒤 하이픈 제거
    slug = slug.strip('-')
    
    # 길이 제한
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug or "untitled"


def deep_merge_dict(dict1: Dict, dict2: Dict) -> Dict:
    """딕셔너리 깊은 병합"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """안전한 JSON 로드"""
    try:
        return json.loads(json_string) if json_string else default
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """안전한 JSON 덤프"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


def batch_process(items: List[Any], batch_size: int = 100):
    """배치 처리 제너레이터"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
    """지수 백오프를 사용한 재시도 데코레이터"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = backoff_factor * (2 ** attempt)
                logger.warning(
                    f"Function {func.__name__} failed, retrying in {wait_time}s",
                    attempt=attempt + 1,
                    error=str(e)
                )
                time.sleep(wait_time)
    
    return wrapper


def get_korean_age_group(age: int) -> str:
    """나이대 그룹 반환"""
    if age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    elif age < 50:
        return "40대"
    elif age < 60:
        return "50대"
    else:
        return "60대 이상"


def is_business_hours(dt: Optional[datetime] = None) -> bool:
    """업무 시간 확인 (한국 시간 기준)"""
    if dt is None:
        dt = datetime.now()
    
    # 주말 확인
    if dt.weekday() >= 5:  # 토, 일
        return False
    
    # 업무 시간 확인 (9시-18시)
    return 9 <= dt.hour < 18


def calculate_business_days(start_date: datetime, end_date: datetime) -> int:
    """업무일 계산"""
    current_date = start_date.date()
    end_date = end_date.date()
    business_days = 0
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 월-금
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days


def generate_color_from_string(text: str) -> str:
    """문자열에서 일관된 색상 생성"""
    hash_object = hashlib.md5(text.encode())
    hex_dig = hash_object.hexdigest()
    return f"#{hex_dig[:6]}"


def anonymize_data(data: Dict, sensitive_fields: List[str]) -> Dict:
    """데이터 익명화"""
    anonymized = data.copy()
    
    for field in sensitive_fields:
        if field in anonymized:
            if isinstance(anonymized[field], str):
                if '@' in anonymized[field]:  # 이메일로 추정
                    anonymized[field] = mask_email(anonymized[field])
                elif re.match(r'^\d+$', anonymized[field]):  # 전화번호로 추정
                    anonymized[field] = mask_phone_number(anonymized[field])
                else:
                    # 일반 문자열은 앞뒤만 보여주기
                    value = anonymized[field]
                    if len(value) > 2:
                        anonymized[field] = value[0] + '*' * (len(value) - 2) + value[-1]
            else:
                anonymized[field] = "[HIDDEN]"
    
    return anonymized
