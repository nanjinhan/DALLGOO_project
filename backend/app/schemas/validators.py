"""회원 입력 검증 규칙 (CLAUDE.md §7.1.1).

- 모든 규칙은 DB에 닿기 전에 Pydantic 단계에서 막는다.
- 위반 시 ValueError(한국어 메시지) → RequestValidationError → 422.
"""

import re

# 아이디: 영문 소문자로 시작, 영문 소문자+숫자, 총 4~20자
USERNAME_RE = re.compile(r"^[a-z][a-z0-9]{3,19}$")
# 비밀번호: 대문자·소문자·숫자 각 1개 이상, 8~64자
PASSWORD_RE = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,64}$")
# 닉네임: 한글·영문·숫자, 2~20자
NICKNAME_RE = re.compile(r"^[가-힣a-zA-Z0-9]{2,20}$")


def normalize_username(value: str) -> str:
    """trim + 소문자 정규화 후 형식 검증 (대소문자 구분 없이 저장)."""
    v = (value or "").strip().lower()
    if not USERNAME_RE.match(v):
        raise ValueError(
            "아이디는 영문 소문자로 시작하는 4~20자이며, 영문 소문자와 숫자만 사용할 수 있습니다."
        )
    return v


def validate_nickname(value: str) -> str:
    v = (value or "").strip()
    if not NICKNAME_RE.match(v):
        raise ValueError("닉네임은 2~20자이며 한글, 영문, 숫자만 사용할 수 있습니다.")
    return v


def validate_password(value: str) -> str:
    v = value or ""
    if re.search(r"\s", v):
        raise ValueError("비밀번호에 공백을 포함할 수 없습니다.")
    if not (8 <= len(v) <= 64):
        raise ValueError("비밀번호는 8~64자여야 합니다.")
    if not PASSWORD_RE.match(v):
        raise ValueError("비밀번호는 대문자·소문자·숫자를 각각 1자 이상 포함해야 합니다.")
    return v


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()
