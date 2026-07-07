import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.activity_consumer import RECENT_KEY
from app.api.deps import get_admin_user
from app.core.database import get_db
from app.core.errors import bad_request, not_found
from app.core.redis_client import redis_client
from app.crud import comment as comment_crud
from app.crud import post as post_crud
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.common import Message
from app.schemas.user import UserAdminOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/activities")
def list_activities(_: User = Depends(get_admin_user)):
    """Kafka 소비자가 Redis에 쌓아둔 최근 활동을 최신순으로 반환."""
    raw = redis_client.lrange(RECENT_KEY, 0, 49)
    activities = []
    for item in raw:
        try:
            activities.append(json.loads(item))
        except (ValueError, TypeError):
            continue
    return activities


@router.get("/users", response_model=list[UserAdminOut])
def list_users(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id)).all()
    result = []
    for u in users:
        pc, cc = user_crud.counts(db, u.id)
        result.append(
            UserAdminOut(
                id=u.id,
                username=u.username,
                email=u.email,
                nickname=u.nickname,
                is_active=u.is_active,
                is_admin=u.is_admin,
                post_count=pc,
                comment_count=cc,
                created_at=u.created_at,
            )
        )
    return result


@router.patch("/users/{user_id}/active", response_model=Message)
def set_user_active(
    user_id: int,
    active: bool = Query(...),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise not_found("회원을 찾을 수 없습니다.", "USER_NOT_FOUND")
    if user.id == admin.id:
        raise bad_request("본인 계정은 정지할 수 없습니다.", "CANNOT_BAN_SELF")
    user.is_active = active
    db.commit()
    return Message(detail="정지를 해제했습니다." if active else "회원을 정지했습니다.")


@router.delete("/posts/{post_id}", response_model=Message)
def admin_delete_post(
    post_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    post = post_crud.get_with_files(db, post_id)
    if post is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")
    post_crud.delete(db, post)
    return Message(detail="게시글을 삭제했습니다.")


@router.delete("/comments/{comment_id}", response_model=Message)
def admin_delete_comment(
    comment_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    comment = comment_crud.get(db, comment_id)
    if comment is None:
        raise not_found("댓글을 찾을 수 없습니다.", "COMMENT_NOT_FOUND")
    if comment_crud.has_replies(db, comment_id):
        comment_crud.soft_delete(db, comment)
    else:
        comment_crud.hard_delete(db, comment)
    return Message(detail="댓글을 삭제했습니다.")
