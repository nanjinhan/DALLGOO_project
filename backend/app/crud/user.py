from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User


def get(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_nickname(db: Session, nickname: str) -> User | None:
    return db.scalar(select(User).where(User.nickname == nickname))


def create(
    db: Session, *, username: str, email: str, nickname: str, password: str
) -> User:
    user = User(
        username=username,
        email=email,
        nickname=nickname,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_profile(
    db: Session, user: User, *, nickname: str | None, email: str | None
) -> User:
    if nickname is not None:
        user.nickname = nickname
    if email is not None:
        user.email = email
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, new_password: str) -> None:
    user.password_hash = hash_password(new_password)
    db.commit()


def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def counts(db: Session, user_id: int) -> tuple[int, int]:
    """(글 수, 댓글 수)."""
    post_count = db.scalar(
        select(func.count()).select_from(Post).where(Post.user_id == user_id)
    )
    comment_count = db.scalar(
        select(func.count())
        .select_from(Comment)
        .where(Comment.user_id == user_id, Comment.is_deleted.is_(False))
    )
    return post_count or 0, comment_count or 0
