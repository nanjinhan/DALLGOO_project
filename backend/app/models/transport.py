from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class TransportRecord(Base, TimestampMixin):
    """이송 기록 — 관리자가 등록하는 구급 이송 사례(사진 + 경로 + 세부정보)."""

    __tablename__ = "transport_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    patient_name: Mapped[str] = mapped_column(String(50), nullable=False)  # 출력 시 마스킹
    from_hospital: Mapped[str] = mapped_column(String(120), nullable=False)
    to_hospital: Mapped[str] = mapped_column(String(120), nullable=False)
    distance_km: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    crew: Mapped[str] = mapped_column(String(255), default="", nullable=False)  # 쉼표 구분
    detail: Mapped[str] = mapped_column(Text, default="", nullable=False)  # 잠금 콘텐츠
    image_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # 보호자 인증 — 등록 시 지정한 보호자 이름 + 자동 생성 코드(관리자에게만 노출)
    guardian_name: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    guardian_code: Mapped[str] = mapped_column(String(12), default="", nullable=False)

    author: Mapped["User"] = relationship()
    comments: Mapped[list["TransportComment"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )


class TransportComment(Base, TimestampMixin):
    """보호자가 인증 후 남기는 댓글 + 이송 서비스 평가(첫 댓글 필수)."""

    __tablename__ = "transport_comments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("transport_records.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    guardian_name: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 평가(첫 댓글에만 존재) — 1~4 척도 / 추천 1~10(NPS)
    medical: Mapped[int | None] = mapped_column(Integer, nullable=True)
    driving: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hygiene: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommend: Mapped[int | None] = mapped_column(Integer, nullable=True)

    record: Mapped["TransportRecord"] = relationship(back_populates="comments")


from app.models.user import User  # noqa: E402
