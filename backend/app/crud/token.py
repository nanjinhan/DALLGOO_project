from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.security import refresh_token_expires_at
from app.models.token import PasswordResetToken, RefreshToken


# ===== Refresh Token =====
def store_refresh(db: Session, user_id: int, token: str) -> RefreshToken:
    rt = RefreshToken(
        user_id=user_id, token=token, expires_at=refresh_token_expires_at()
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def get_refresh(db: Session, token: str) -> RefreshToken | None:
    return db.scalar(select(RefreshToken).where(RefreshToken.token == token))


def is_valid(rt: RefreshToken | None) -> bool:
    if rt is None or rt.revoked:
        return False
    expires = rt.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return expires > datetime.now(timezone.utc)


def revoke(db: Session, token: str) -> None:
    db.execute(
        update(RefreshToken).where(RefreshToken.token == token).values(revoked=True)
    )
    db.commit()


def revoke_all_for_user(db: Session, user_id: int) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .values(revoked=True)
    )
    db.commit()


# ===== Password Reset Token =====
def create_reset(
    db: Session, user_id: int, token: str, expires_at: datetime
) -> PasswordResetToken:
    prt = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(prt)
    db.commit()
    db.refresh(prt)
    return prt


def get_reset(db: Session, token: str) -> PasswordResetToken | None:
    return db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    )


def reset_is_valid(prt: PasswordResetToken | None) -> bool:
    if prt is None or prt.used:
        return False
    expires = prt.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return expires > datetime.now(timezone.utc)


def mark_reset_used(db: Session, prt: PasswordResetToken) -> None:
    prt.used = True
    db.commit()
