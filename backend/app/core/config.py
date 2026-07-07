from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 환경설정 (.env 로드)."""

    # --- Database ---
    DATABASE_URL: str

    # --- JWT ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Redis (메모리 DB: rate limit / 인증번호) ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- RabbitMQ (이메일 발송 큐) ---
    RABBITMQ_URL: str = "amqp://dallgoo:dallgoo_mq_pw_2026@rabbitmq:5672/"

    # --- 로그인 잠금(rate limiting) ---
    LOGIN_MAX_ATTEMPTS: int = 5  # 이 횟수 넘게 틀리면 잠금
    LOGIN_LOCK_MINUTES: int = 10  # 잠금 시간(분)

    # --- 이메일 인증 ---
    EMAIL_CODE_TTL_MINUTES: int = 5  # 인증번호 유효시간(분)
    EMAIL_CODE_RESEND_SECONDS: int = 60  # 재발송 최소 간격(초)
    EMAIL_VERIFIED_TTL_MINUTES: int = 30  # 인증완료 상태 유지(분)

    # --- 메일 발송(SMTP / Gmail). 비어 있으면 '발송 대신 서버 로그' 모드 ---
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # 보내는 Gmail 주소
    SMTP_PASSWORD: str = ""  # Gmail 앱 비밀번호(16자)
    SMTP_FROM: str = "달구 게시판 <no-reply@dallgoo.io>"

    # --- File upload ---
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    # 허용 확장자(쉼표 구분). 비우면 모두 허용.
    ALLOWED_EXTENSIONS: str = (
        "jpg,jpeg,png,gif,webp,pdf,txt,csv,doc,docx,xls,xlsx,ppt,pptx,zip,hwp"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def email_enabled(self) -> bool:
        return bool(self.SMTP_USER and self.SMTP_PASSWORD)

    @property
    def allowed_ext_set(self) -> set[str]:
        # 'jpg' 형태(점 없이, 소문자)로 보관
        return {
            e.strip().lower().lstrip(".")
            for e in self.ALLOWED_EXTENSIONS.split(",")
            if e.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
