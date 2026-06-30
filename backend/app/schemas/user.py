from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)

from app.schemas.validators import (
    normalize_email,
    normalize_username,
    validate_nickname,
    validate_password,
)


class UserBase(BaseModel):
    username: str
    email: EmailStr
    nickname: str

    @field_validator("username")
    @classmethod
    def _v_username(cls, v: str) -> str:
        return normalize_username(v)

    @field_validator("email")
    @classmethod
    def _v_email(cls, v: str) -> str:
        return normalize_email(v)

    @field_validator("nickname")
    @classmethod
    def _v_nickname(cls, v: str) -> str:
        return validate_nickname(v)


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def _v_password(cls, v: str) -> str:
        return validate_password(v)

    @model_validator(mode="after")
    def _password_not_contains_identity(self):
        pw = self.password.lower()
        # 짧은 토큰(예: 한 글자 이메일 아이디)은 우연히 포함될 수 있어 4자 이상만 검사
        if len(self.username) >= 4 and self.username in pw:
            raise ValueError("비밀번호에 아이디를 포함할 수 없습니다.")
        local = self.email.split("@")[0].lower()
        if len(local) >= 4 and local in pw:
            raise ValueError("비밀번호에 이메일 아이디를 포함할 수 없습니다.")
        return self


class UserUpdate(BaseModel):
    nickname: str | None = None
    email: EmailStr | None = None

    @field_validator("nickname")
    @classmethod
    def _v_nickname(cls, v):
        return validate_nickname(v) if v is not None else v

    @field_validator("email")
    @classmethod
    def _v_email(cls, v):
        return normalize_email(v) if v is not None else v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _v_new_password(cls, v: str) -> str:
        return validate_password(v)

    @model_validator(mode="after")
    def _new_differs_from_current(self):
        if self.current_password == self.new_password:
            raise ValueError("새 비밀번호는 현재 비밀번호와 달라야 합니다.")
        return self


class UserDelete(BaseModel):
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    nickname: str
    is_active: bool
    created_at: datetime


class UserMe(UserOut):
    """마이페이지 — 내 글/댓글 수 포함."""

    post_count: int = 0
    comment_count: int = 0
