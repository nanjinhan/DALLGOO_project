from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import not_found
from app.crud import notification as notif_crud
from app.models.user import User
from app.schemas.common import Message
from app.schemas.notification import NotificationOut, UnreadCount

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def my_notifications(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return notif_crud.list_for_user(db, current.id)


@router.get("/unread-count", response_model=UnreadCount)
def unread(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return UnreadCount(unread=notif_crud.unread_count(db, current.id))


@router.patch("/read-all", response_model=Message)
def read_all(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    notif_crud.mark_all_read(db, current.id)
    return Message(detail="모두 읽음 처리했습니다.")


@router.patch("/{notif_id}/read", response_model=Message)
def read_one(
    notif_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notif = notif_crud.get(db, notif_id)
    if notif is None or notif.user_id != current.id:
        raise not_found("알림을 찾을 수 없습니다.", "NOTIF_NOT_FOUND")
    notif_crud.mark_read(db, notif)
    return Message(detail="읽음 처리했습니다.")
