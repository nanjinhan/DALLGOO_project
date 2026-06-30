from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    likes: Mapped[list["PostLike"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    files: Mapped[list["File"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )


from app.models.comment import Comment  # noqa: E402
from app.models.file import File  # noqa: E402
from app.models.like import PostLike  # noqa: E402
from app.models.user import User  # noqa: E402
