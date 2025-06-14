"""
데이터 검증 함수들
"""
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from email_validator import validate_email, EmailNotValidError

import structlog

logger = structlog.get_logger()


def validate_email_address(email: str) -> tuple[bool, str]:
    """이메일 주소 검증"""
    if not email:
        return False, "이메일 주소가 필요합니다"
    
    try:
        # email-validator 라이브러리 사용
        validated_email = validate_email(email)
        return True, validated_email.email
    except EmailNotValidError as e:
        return False, f"유효하지 않은 이메일 주소입니다: {str(e)}"


def validate_password(password: str) -> tuple[bool, str]:
    """비밀번호 검증"""
    if not password:
        return False, "비밀번호가 필요합니다"
    
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다"
    
    if len(password) > 128:
        return False, "비밀번호는 최대 128자까지 가능합니다"
    
    # 영문, 숫자, 특수문자 포함 확인
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if not (has_letter and has_digit):
        return False, "비밀번호는 영문과 숫자를 포함해야 합니다"
    
    return True, "유효한 비밀번호입니다"


def validate_phone_number(phone: str, country_code: str = "KR") -> tuple[bool, str]:
    """전화번호 검증"""
    if not phone:
        return False, "전화번호가 필요합니다"
    
    # 숫자만 추출
    digits_only = re.sub(r'\D', '', phone)
    
    if country_code == "KR":
        # 한국 전화번호 패턴
        if len(digits_only) == 10:
            # 010-XXXX-XXXX 형태로 포맷
            formatted = f"{digits_only[:3]}-{digits_only[3:7]}-{digits_only[7:]}"
            return True, formatted
        elif len(digits_only) == 11:
            # 010-XXXX-XXXX 형태로 포맷
            formatted = f"{digits_only[:3]}-{digits_only[3:7]}-{digits_only[7:]}"
            return True, formatted
        else:
            return False, "올바른 한국 전화번호 형식이 아닙니다"
    
    # 기본 검증 (국제 형식)
    if len(digits_only) < 7 or len(digits_only) > 15:
        return False, "전화번호 길이가 올바르지 않습니다"
    
    return True, digits_only


def validate_age(age: Union[int, str]) -> tuple[bool, int]:
    """나이 검증"""
    try:
        age_int = int(age)
    except (ValueError, TypeError):
        return False, 0
    
    if age_int < 0:
        return False, 0
    
    if age_int > 150:
        return False, 0
    
    return True, age_int


def validate_birthdate(birthdate: Union[str, date, datetime]) -> tuple[bool, Optional[date]]:
    """생년월일 검증"""
    if not birthdate:
        return False, None
    
    try:
        if isinstance(birthdate, str):
            # 다양한 날짜 형식 지원
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"]:
                try:
                    parsed_date = datetime.strptime(birthdate, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return False, None
        elif isinstance(birthdate, datetime):
            parsed_date = birthdate.date()
        elif isinstance(birthdate, date):
            parsed_date = birthdate
        else:
            return False, None
        
        # 미래 날짜 체크
        if parsed_date > date.today():
            return False, None
        
        # 너무 오래된 날짜 체크 (150년 전)
        oldest_date = date.today().replace(year=date.today().year - 150)
        if parsed_date < oldest_date:
            return False, None
        
        return True, parsed_date
        
    except (ValueError, TypeError):
        return False, None


def validate_text_length(text: str, min_length: int = 0, max_length: int = 1000) -> tuple[bool, str]:
    """텍스트 길이 검증"""
    if not isinstance(text, str):
        return False, "문자열이 아닙니다"
    
    if len(text) < min_length:
        return False, f"최소 {min_length}자 이상 입력해주세요"
    
    if len(text) > max_length:
        return False, f"최대 {max_length}자까지 입력 가능합니다"
    
    return True, text.strip()


def validate_diary_content(content: str) -> tuple[bool, str]:
    """일기 내용 검증"""
    if not content:
        return False, "일기 내용이 필요합니다"
    
    # 길이 검증
    is_valid, message = validate_text_length(content, min_length=10, max_length=5000)
    if not is_valid:
        return False, message
    
    # 금지 단어 체크 (예시)
    forbidden_words = ["스팸", "광고", "홍보"]
    content_lower = content.lower()
    
    for word in forbidden_words:
        if word in content_lower:
            return False, f"금지된 단어가 포함되어 있습니다: {word}"
    
    return True, content.strip()


def validate_json_data(data: Any, required_fields: List[str] = None) -> tuple[bool, str]:
    """JSON 데이터 검증"""
    if not isinstance(data, dict):
        return False, "JSON 객체가 아닙니다"
    
    if required_fields:
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
    
    return True, "유효한 JSON 데이터입니다"


def validate_file_upload(
    filename: str, 
    file_size: int, 
    allowed_extensions: List[str] = None,
    max_size_mb: int = 10
) -> tuple[bool, str]:
    """파일 업로드 검증"""
    if not filename:
        return False, "파일명이 필요합니다"
    
    # 파일 확장자 검증
    if allowed_extensions:
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if file_ext not in [ext.lower() for ext in allowed_extensions]:
            return False, f"허용되지 않는 파일 형식입니다. 허용 형식: {', '.join(allowed_extensions)}"
    
    # 파일 크기 검증
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"파일 크기가 너무 큽니다. 최대 {max_size_mb}MB까지 가능합니다"
    
    # 파일명 안전성 검증
    if re.search(r'[<>:"/\\|?*]', filename):
        return False, "파일명에 특수문자가 포함되어 있습니다"
    
    return True, "유효한 파일입니다"


def validate_url(url: str) -> tuple[bool, str]:
    """URL 검증"""
    if not url:
        return False, "URL이 필요합니다"
    
    # 기본 URL 패턴 검증
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "유효하지 않은 URL 형식입니다"
    
    return True, url


def validate_date_range(start_date: str, end_date: str) -> tuple[bool, str]:
    """날짜 범위 검증"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        if start > end:
            return False, "시작 날짜가 종료 날짜보다 늦습니다"
        
        # 너무 긴 범위 체크 (1년)
        if (end - start).days > 365:
            return False, "날짜 범위가 너무 깁니다 (최대 1년)"
        
        return True, "유효한 날짜 범위입니다"
        
    except ValueError:
        return False, "잘못된 날짜 형식입니다 (YYYY-MM-DD)"


def validate_score_range(score: Union[int, float], min_score: float = 0.0, max_score: float = 1.0) -> tuple[bool, float]:
    """점수 범위 검증"""
    try:
        score_float = float(score)
    except (ValueError, TypeError):
        return False, 0.0
    
    if score_float < min_score or score_float > max_score:
        return False, 0.0
    
    return True, score_float


def validate_mbti_type(mbti: str) -> tuple[bool, str]:
    """MBTI 유형 검증"""
    if not mbti:
        return False, "MBTI 유형이 필요합니다"
    
    mbti = mbti.upper().strip()
    
    if len(mbti) != 4:
        return False, "MBTI는 4자리여야 합니다"
    
    valid_types = [
        "INTJ", "INTP", "ENTJ", "ENTP",
        "INFJ", "INFP", "ENFJ", "ENFP",
        "ISTJ", "ISFJ", "ESTJ", "ESFJ",
        "ISTP", "ISFP", "ESTP", "ESFP"
    ]
    
    if mbti not in valid_types:
        return False, "유효하지 않은 MBTI 유형입니다"
    
    return True, mbti


def validate_emotion_tags(tags: List[str]) -> tuple[bool, List[str]]:
    """감정 태그 검증"""
    if not isinstance(tags, list):
        return False, []
    
    valid_emotions = [
        "기쁨", "슬픔", "화남", "두려움", "놀라움", "혐오", "사랑", "희망",
        "불안", "스트레스", "평온", "감사", "외로움", "자신감", "부끄러움", "죄책감",
        "joy", "sadness", "anger", "fear", "surprise", "disgust", "love", "hope",
        "anxiety", "stress", "calm", "gratitude", "loneliness", "confidence"
    ]
    
    validated_tags = []
    for tag in tags:
        if isinstance(tag, str) and tag.strip():
            clean_tag = tag.strip().lower()
            if clean_tag in [emotion.lower() for emotion in valid_emotions]:
                validated_tags.append(clean_tag)
    
    # 중복 제거
    validated_tags = list(set(validated_tags))
    
    # 최대 10개 제한
    if len(validated_tags) > 10:
        validated_tags = validated_tags[:10]
    
    return True, validated_tags


def validate_location(location: str) -> tuple[bool, str]:
    """위치 정보 검증"""
    if not location:
        return True, ""  # 위치는 선택사항
    
    # 길이 검증
    if len(location) > 100:
        return False, "위치 정보가 너무 깁니다"
    
    # 기본적인 한글, 영문, 숫자, 공백, 일부 특수문자만 허용
    if not re.match(r'^[가-힣a-zA-Z0-9\s\-\.,()]+$', location):
        return False, "위치 정보에 허용되지 않는 문자가 포함되어 있습니다"
    
    return True, location.strip()


def validate_user_settings(settings: Dict[str, Any]) -> tuple[bool, str, Dict[str, Any]]:
    """사용자 설정 검증"""
    if not isinstance(settings, dict):
        return False, "설정은 객체 형태여야 합니다", {}
    
    validated_settings = {}
    
    # 알림 설정
    if "notifications_enabled" in settings:
        if isinstance(settings["notifications_enabled"], bool):
            validated_settings["notifications_enabled"] = settings["notifications_enabled"]
    
    # 이메일 알림 설정
    if "email_notifications" in settings:
        if isinstance(settings["email_notifications"], bool):
            validated_settings["email_notifications"] = settings["email_notifications"]
    
    # 매칭 활성화
    if "matching_enabled" in settings:
        if isinstance(settings["matching_enabled"], bool):
            validated_settings["matching_enabled"] = settings["matching_enabled"]
    
    # 프로필 공개 수준
    if "profile_visibility" in settings:
        visibility = settings["profile_visibility"]
        if visibility in ["public", "friends", "private"]:
            validated_settings["profile_visibility"] = visibility
    
    # 언어 설정
    if "language" in settings:
        language = settings["language"]
        if language in ["ko", "en", "ja", "zh"]:
            validated_settings["language"] = language
    
    # 타임존
    if "timezone" in settings:
        timezone = settings["timezone"]
        # 간단한 타임존 검증
        valid_timezones = ["Asia/Seoul", "America/New_York", "Europe/London", "Asia/Tokyo"]
        if timezone in valid_timezones:
            validated_settings["timezone"] = timezone
    
    return True, "유효한 설정입니다", validated_settings


def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> tuple[bool, str, int, int]:
    """페이지네이션 매개변수 검증"""
    try:
        page = int(page)
        per_page = int(per_page)
    except (ValueError, TypeError):
        return False, "페이지 매개변수는 숫자여야 합니다", 1, 20
    
    # 페이지 번호 검증
    if page < 1:
        page = 1
    
    # 페이지당 항목 수 검증
    if per_page < 1:
        per_page = 20
    elif per_page > max_per_page:
        per_page = max_per_page
    
    return True, "", page, per_page


def validate_search_query(query: str, min_length: int = 2, max_length: int = 100) -> tuple[bool, str]:
    """검색 쿼리 검증"""
    if not query:
        return False, "검색어가 필요합니다"
    
    query = query.strip()
    
    if len(query) < min_length:
        return False, f"검색어는 최소 {min_length}자 이상이어야 합니다"
    
    if len(query) > max_length:
        return False, f"검색어는 최대 {max_length}자까지 가능합니다"
    
    # SQL 인젝션 방지를 위한 기본 검증
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    for char in dangerous_chars:
        if char in query.lower():
            return False, "허용되지 않는 문자가 포함되어 있습니다"
    
    return True, query


def validate_hex_color(color: str) -> tuple[bool, str]:
    """16진수 색상 코드 검증"""
    if not color:
        return False, "색상 코드가 필요합니다"
    
    # # 제거
    color = color.lstrip('#')
    
    # 길이 확인 (3자리 또는 6자리)
    if len(color) not in [3, 6]:
        return False, "색상 코드는 3자리 또는 6자리여야 합니다"
    
    # 16진수 확인
    try:
        int(color, 16)
    except ValueError:
        return False, "유효하지 않은 16진수 색상 코드입니다"
    
    # 6자리로 정규화
    if len(color) == 3:
        color = ''.join([c*2 for c in color])
    
    return True, f"#{color.upper()}"


def sanitize_input(data: Any) -> Any:
    """입력 데이터 정제"""
    if isinstance(data, str):
        # XSS 방지를 위한 기본 정제
        data = data.replace('<', '&lt;').replace('>', '&gt;')
        data = data.replace('"', '&quot;').replace("'", '&#x27;')
        return data.strip()
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data
