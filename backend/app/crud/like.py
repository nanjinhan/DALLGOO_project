from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.like import CommentLike, PostLike


def post_like_count(db: Session, post_id: int) -> int:
    return (
        db.scalar(
            select(func.count()).select_from(PostLike).where(PostLike.post_id == post_id)
        )
        or 0
    )


def comment_like_count(db: Session, comment_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(CommentLike)
            .where(CommentLike.comment_id == comment_id)
        )
        or 0
    )


# ===== 게시글 좋아요 =====
def post_like_exists(db: Session, post_id: int, user_id: int) -> bool:
    return (
        db.scalar(
            select(PostLike.id).where(
                PostLike.post_id == post_id, PostLike.user_id == user_id
            )
        )
        is not None
    )


def add_post_like(db: Session, post_id: int, user_id: int) -> bool:
    """이미 눌렀으면 False, 새로 추가하면 True."""
    if post_like_exists(db, post_id, user_id):
        return False
    db.add(PostLike(post_id=post_id, user_id=user_id))
    db.commit()
    return True


def remove_post_like(db: Session, post_id: int, user_id: int) -> bool:
    result = db.execute(
        sa_delete(PostLike).where(
            PostLike.post_id == post_id, PostLike.user_id == user_id
        )
    )
    db.commit()
    return result.rowcount > 0


# ===== 댓글 좋아요 =====
def comment_like_exists(db: Session, comment_id: int, user_id: int) -> bool:
    return (
        db.scalar(
            select(CommentLike.id).where(
                CommentLike.comment_id == comment_id, CommentLike.user_id == user_id
            )
        )
        is not None
    )


def add_comment_like(db: Session, comment_id: int, user_id: int) -> bool:
    if comment_like_exists(db, comment_id, user_id):
        return False
    db.add(CommentLike(comment_id=comment_id, user_id=user_id))
    db.commit()
    return True


def remove_comment_like(db: Session, comment_id: int, user_id: int) -> bool:
    result = db.execute(
        sa_delete(CommentLike).where(
            CommentLike.comment_id == comment_id, CommentLike.user_id == user_id
        )
    )
    db.commit()
    return result.rowcount > 0
