from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SiteSetting(Base):
    """사이트 운영 설정 — 관리자가 코드 수정 없이 바꾸는 값(key-value).

    설정 항목이 늘어나도 마이그레이션이 필요 없도록 키-값 한 테이블로 둔다.
    허용 키는 app/crud/setting.py의 DEFAULTS에서 관리한다.
    """

    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_at: Mapped[object] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
