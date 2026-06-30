"""Redis 기반 임시 상태 저장 — 로그인 잠금(rate limit) + 이메일 인증번호.

모두 TTL(유효기간)을 붙여서 시간이 지나면 자동으로 사라진다.
"""

import secrets

from app.core.config import settings
from app.core.redis_client import redis_client


# ===== 로그인 잠금 (rate limiting) =====
def _fail_key(username: str) -> str:
    return f"login_fail:{username.lower()}"


def login_locked_seconds(username: str) -> int:
    """잠겨 있으면 남은 잠금 시간(초), 아니면 0."""
    key = _fail_key(username)
    count = int(redis_client.get(key) or 0)
    if count >= settings.LOGIN_MAX_ATTEMPTS:
        ttl = redis_client.ttl(key)
        return ttl if ttl and ttl > 0 else 0
    return 0


def login_record_fail(username: str) -> int:
    """실패 1회 기록. 첫 실패 때 TTL 설정. 현재 누적 실패 수 반환."""
    key = _fail_key(username)
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, settings.LOGIN_LOCK_MINUTES * 60)
    return count


def login_reset(username: str) -> None:
    """로그인 성공 시 실패 카운트 초기화."""
    redis_client.delete(_fail_key(username))


# ===== 이메일 인증번호 =====
def _code_key(email: str) -> str:
    return f"email_code:{email.lower()}"


def _resent_key(email: str) -> str:
    return f"email_code_sent:{email.lower()}"


def _verified_key(email: str) -> str:
    return f"email_verified:{email.lower()}"


def code_resend_blocked_seconds(email: str) -> int:
    """재발송 쿨다운이 남아 있으면 남은 초, 아니면 0."""
    ttl = redis_client.ttl(_resent_key(email))
    return ttl if ttl and ttl > 0 else 0


def issue_code(email: str) -> str:
    """6자리 인증번호 생성 → TTL 저장 + 재발송 쿨다운 설정. 코드 반환."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    redis_client.setex(_code_key(email), settings.EMAIL_CODE_TTL_MINUTES * 60, code)
    redis_client.setex(_resent_key(email), settings.EMAIL_CODE_RESEND_SECONDS, "1")
    return code


def verify_code(email: str, code: str) -> bool:
    """코드 일치 시 인증완료 표시(TTL) + 코드 폐기. 성공 여부 반환."""
    saved = redis_client.get(_code_key(email))
    if saved and saved == code:
        redis_client.delete(_code_key(email))
        redis_client.setex(
            _verified_key(email), settings.EMAIL_VERIFIED_TTL_MINUTES * 60, "1"
        )
        return True
    return False


def is_email_verified(email: str) -> bool:
    return redis_client.exists(_verified_key(email)) == 1


def clear_email_verified(email: str) -> None:
    redis_client.delete(_verified_key(email))
