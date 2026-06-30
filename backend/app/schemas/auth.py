from pydantic import BaseModel, EmailStr, field_validator

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
    detail: str
    # 학습/내부용: 메일 발송 인프라가 없으므로 토큰을 응답으로 노출.
    reset_token: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _v_new_password(cls, v: str) -> str:
        return validate_password(v)
