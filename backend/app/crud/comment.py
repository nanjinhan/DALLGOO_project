from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.comment import Comment
from app.models.like import CommentLike


def get(db: Session, comment_id: int) -> Comment | None:
    return db.get(Comment, comment_id)


def list_for_post(db: Session, post_id: int) -> list[Comment]:
    """해당 글의 모든 댓글(대댓글 포함)을 작성순으로 평면 조회."""
    return list(
        db.scalars(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc(), Comment.id.asc())
        ).all()
    )


def create(
    db: Session,
    *,
    post_id: int,
    user_id: int,
    content: str,
    parent_id: int | None,
) -> Comment:
    comment = Comment(
        post_id=post_id, user_id=user_id, content=content, parent_id=parent_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update(db: Session, comment: Comment, content: str) -> Comment:
    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def has_replies(db: Session, comment_id: int) -> bool:
    return (
        db.scalar(select(Comment.id).where(Comment.parent_id == comment_id)) is not None
    )


def soft_delete(db: Session, comment: Comment) -> None:
    """대댓글이 있으면 내용만 지우고 표시 유지."""
    comment.is_deleted = True
    comment.content = ""
    db.commit()


def hard_delete(db: Session, comment: Comment) -> None:
    db.delete(comment)
    db.commit()


def like_counts(db: Session, post_id: int) -> dict[int, int]:
    """글에 속한 댓글들의 좋아요 수 매핑 {comment_id: count}."""
    rows = db.execute(
        select(CommentLike.comment_id, func.count(CommentLike.id))
        .join(Comment, Comment.id == CommentLike.comment_id)
        .where(Comment.post_id == post_id)
        .group_by(CommentLike.comment_id)
    ).all()
    return {cid: cnt for cid, cnt in rows}


def liked_comment_ids(db: Session, post_id: int, user_id: int) -> set[int]:
    rows = db.scalars(
        select(CommentLike.comment_id)
        .join(Comment, Comment.id == CommentLike.comment_id)
        .where(Comment.post_id == post_id, CommentLike.user_id == user_id)
    ).all()
    return set(rows)
