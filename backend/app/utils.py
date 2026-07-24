import secrets
import random
import string
import re
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional


def generate_reference_number() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%y%m%d%H%M%S")
    random_part = secrets.token_hex(4).upper()
    return f"TXN{timestamp}{random_part}"


def generate_utr_number() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(3).upper()
    return f"UTR{timestamp}{random_part}"


def generate_account_number() -> str:
    prefix = "1000"
    middle = str(random.randint(10000000, 99999999))
    suffix = str(random.randint(1000, 9999))
    raw = prefix + middle + suffix
    checksum = str(sum(int(d) for d in raw) % 10)
    return raw + checksum


def generate_card_number() -> str:
    prefix = "4000"
    groups = []
    for _ in range(3):
        groups.append(f"{random.randint(100000, 999999)}")
    middle = "".join(groups)
    raw = prefix + middle
    digits = [int(d) for d in raw]
    for i in range(len(digits) - 1, -1, -1):
        if i % 2 == 0:
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
    checksum = (10 - (sum(digits) % 10)) % 10
    return raw + str(checksum)


def generate_cvv() -> str:
    return f"{random.randint(100, 999)}"


def generate_session_id() -> str:
    return str(uuid.uuid4())


def generate_temp_token() -> str:
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    return secrets.token_urlsafe(48)


def hash_device_fingerprint(fingerprint: str) -> str:
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password.encode('utf-8')) > 72:
        return False, "Password must not exceed 72 bytes when encoded as UTF-8 (bcrypt limit)"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, None


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    pattern = r"^\+?[1-9]\d{9,14}$"
    return bool(re.match(pattern, cleaned))


def validate_ifsc(ifsc: str) -> bool:
    pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"
    return bool(re.match(pattern, ifsc))


def validate_upi_id(upi_id: str) -> bool:
    pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$"
    return bool(re.match(pattern, upi_id))


def sanitize_input(value: str) -> str:
    return re.sub(r"[<>\'\"%;()&+]", "", value)


def get_client_ip(request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    client_host = request.client.host if request.client else "0.0.0.0"
    return client_host


def get_user_agent(request) -> str:
    return request.headers.get("User-Agent", "")


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return principal / tenure_months
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    return round(emi, 2)


def mask_card_number(card_number: str) -> str:
    if len(card_number) < 8:
        return card_number
    return card_number[:4] + "XXXXXXXX" + card_number[-4:]


def parse_device_fingerprint(headers: dict) -> dict:
    return {
        "user_agent": headers.get("user-agent", ""),
        "accept_language": headers.get("accept-language", ""),
        "accept_encoding": headers.get("accept-encoding", ""),
        "sec_ch_ua": headers.get("sec-ch-ua", ""),
        "sec_ch_ua_platform": headers.get("sec-ch-ua-platform", ""),
        "sec_ch_ua_mobile": headers.get("sec-ch-ua-mobile", ""),
        "dnt": headers.get("dnt", ""),
    }
