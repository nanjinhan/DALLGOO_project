from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.notification import Notification


def notify(
    db: Session,
    *,
    recipient_id: int,
    actor_id: int,
    type: str,
    message: str,
    post_id: int | None = None,
) -> None:
    """알림 생성. 단, 자기 자신의 행동엔 알림을 만들지 않는다."""
    if recipient_id == actor_id:
        return
    db.add(
        Notification(
            user_id=recipient_id,
            actor_id=actor_id,
            type=type,
            message=message,
            post_id=post_id,
        )
    )
    db.commit()


def list_for_user(db: Session, user_id: int, limit: int = 30) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
        ).all()
    )


def unread_count(db: Session, user_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id, Notification.is_read.is_(False)
            )
        )
        or 0
    )


def get(db: Session, notif_id: int) -> Notification | None:
    return db.get(Notification, notif_id)


def mark_read(db: Session, notif: Notification) -> None:
    notif.is_read = True
    db.commit()


def mark_all_read(db: Session, user_id: int) -> None:
    db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()
