from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.validators import validate_password


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _normalize_username(cls, v: str) -> str:
        # 저장 시 소문자 정규화하므로 로그인도 동일하게 맞춘다.
        return (v or "").strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    # 보안상 토큰은 응답에 노출하지 않는다. (실서비스: 이메일 발송 / 개발: 서버 로그)
    detail: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _v_new_password(cls, v: str) -> str:
        return validate_password(v)


# ===== 이메일 인증 / 아이디 찾기 =====
class EmailRequest(BaseModel):
    email: EmailStr


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
