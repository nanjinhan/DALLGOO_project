from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user
from app.core.config import settings
from app.core.database import get_db
from app.core.errors import bad_request, forbidden, not_found
from app.core.queue import publish_email_job
from app.crud import comment as comment_crud
from app.crud import like as like_crud
from app.crud import notification as notif_crud
from app.crud import post as post_crud
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentOut,
    CommentUpdate,
)
from app.schemas.common import LikeResponse, Message

# 글 하위 댓글 (목록/작성)
post_router = APIRouter(prefix="/posts", tags=["comments"])
# 댓글 단건 (수정/삭제/좋아요)
router = APIRouter(prefix="/comments", tags=["comments"])


def _serialize(
    c: Comment, like_map: dict[int, int], liked_ids: set[int]
) -> CommentOut:
    deleted = c.is_deleted
    return CommentOut(
        id=c.id,
        post_id=c.post_id,
        parent_id=c.parent_id,
        content="삭제된 댓글입니다." if deleted else c.content,
        author=None if deleted else {"id": c.author.id, "nickname": c.author.nickname},
        is_deleted=deleted,
        like_count=like_map.get(c.id, 0),
        liked_by_me=c.id in liked_ids,
        created_at=c.created_at,
        updated_at=c.updated_at,
        replies=[],
    )


@post_router.get("/{post_id}/comments", response_model=CommentListResponse)
def list_comments(
    post_id: int,
    current: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if post_crud.get(db, post_id) is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")

    flat = comment_crud.list_for_post(db, post_id)
    like_map = comment_crud.like_counts(db, post_id)
    liked_ids = (
        comment_crud.liked_comment_ids(db, post_id, current.id) if current else set()
    )

    nodes = {c.id: _serialize(c, like_map, liked_ids) for c in flat}
    roots: list[CommentOut] = []
    for c in flat:
        node = nodes[c.id]
        if c.parent_id and c.parent_id in nodes:
            nodes[c.parent_id].replies.append(node)
        else:
            roots.append(node)
    return CommentListResponse(items=roots)


@post_router.post(
    "/{post_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = post_crud.get(db, post_id)
    if post is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")

    parent = None
    if payload.parent_id is not None:
        parent = comment_crud.get(db, payload.parent_id)
        if parent is None or parent.post_id != post_id:
            raise not_found("부모 댓글을 찾을 수 없습니다.", "PARENT_NOT_FOUND")
        # 대댓글은 1단계까지만 — 부모는 top-level이어야 함
        if parent.parent_id is not None:
            raise bad_request("대댓글에는 다시 답글을 달 수 없습니다.", "NESTING_TOO_DEEP")

    comment = comment_crud.create(
        db,
        post_id=post_id,
        user_id=current.id,
        content=payload.content,
        parent_id=payload.parent_id,
    )
    db.refresh(comment)

    # 알림: 글 작성자에게 (본인 제외)
    notif_crud.notify(
        db,
        recipient_id=post.user_id,
        actor_id=current.id,
        type="comment",
        message=f"{current.nickname}님이 회원님의 글에 댓글을 남겼습니다.",
        post_id=post_id,
    )
    # 대댓글이면 부모 댓글 작성자에게도
    if parent is not None:
        notif_crud.notify(
            db,
            recipient_id=parent.user_id,
            actor_id=current.id,
            type="reply",
            message=f"{current.nickname}님이 회원님의 댓글에 답글을 남겼습니다.",
            post_id=post_id,
        )
    # 이메일 알림(메일 설정된 경우, 글 작성자에게)
    if settings.email_enabled and post.user_id != current.id and post.author:
        publish_email_job(
            post.author.email,
            "[달구 게시판] 새 댓글 알림",
            f"'{post.title}' 글에 {current.nickname}님이 댓글을 남겼습니다.\n\n"
            f"{payload.content}",
        )
    return _serialize(comment, {}, set())


@router.patch("/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = comment_crud.get(db, comment_id)
    if comment is None or comment.is_deleted:
        raise not_found("댓글을 찾을 수 없습니다.", "COMMENT_NOT_FOUND")
    if comment.user_id != current.id:
        raise forbidden("본인 댓글만 수정할 수 있습니다.", "NOT_OWNER")
    comment_crud.update(db, comment, payload.content)
    return _serialize(comment, {}, set())


@router.delete("/{comment_id}", response_model=Message)
def delete_comment(
    comment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = comment_crud.get(db, comment_id)
    if comment is None or comment.is_deleted:
        raise not_found("댓글을 찾을 수 없습니다.", "COMMENT_NOT_FOUND")
    if comment.user_id != current.id:
        raise forbidden("본인 댓글만 삭제할 수 있습니다.", "NOT_OWNER")

    if comment_crud.has_replies(db, comment_id):
        comment_crud.soft_delete(db, comment)  # 대댓글 보존
    else:
        comment_crud.hard_delete(db, comment)
    return Message(detail="댓글이 삭제되었습니다.")


@router.post("/{comment_id}/like", response_model=LikeResponse)
def like_comment(
    comment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = comment_crud.get(db, comment_id)
    if comment is None or comment.is_deleted:
        raise not_found("댓글을 찾을 수 없습니다.", "COMMENT_NOT_FOUND")
    if like_crud.add_comment_like(db, comment_id, current.id):
        notif_crud.notify(
            db,
            recipient_id=comment.user_id,
            actor_id=current.id,
            type="comment_like",
            message=f"{current.nickname}님이 회원님의 댓글을 좋아합니다.",
            post_id=comment.post_id,
        )
    return LikeResponse(
        liked=True, like_count=like_crud.comment_like_count(db, comment_id)
    )


@router.delete("/{comment_id}/like", response_model=LikeResponse)
def unlike_comment(
    comment_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = comment_crud.get(db, comment_id)
    if comment is None:
        raise not_found("댓글을 찾을 수 없습니다.", "COMMENT_NOT_FOUND")
    like_crud.remove_comment_like(db, comment_id, current.id)
    return LikeResponse(
        liked=False, like_count=like_crud.comment_like_count(db, comment_id)
    )
