from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import conflict, unauthorized
from app.core.security import verify_password
from app.crud import token as token_crud
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.common import Message
from app.schemas.user import PasswordChange, UserDelete, UserMe, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMe)
def get_me(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    post_count, comment_count = user_crud.counts(db, current.id)
    return UserMe(
        id=current.id,
        username=current.username,
        email=current.email,
        nickname=current.nickname,
        is_active=current.is_active,
        created_at=current.created_at,
        post_count=post_count,
        comment_count=comment_count,
    )


@router.patch("/me", response_model=UserMe)
def update_me(
    payload: UserUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.nickname and payload.nickname != current.nickname:
        if user_crud.get_by_nickname(db, payload.nickname):
            raise conflict("이미 사용 중인 닉네임입니다.", "NICKNAME_DUPLICATE")
    if payload.email and payload.email != current.email:
        if user_crud.get_by_email(db, payload.email):
            raise conflict("이미 사용 중인 이메일입니다.", "EMAIL_DUPLICATE")

    try:
        user_crud.update_profile(
            db, current, nickname=payload.nickname, email=payload.email
        )
    except IntegrityError:
        db.rollback()
        if payload.nickname and user_crud.get_by_nickname(db, payload.nickname):
            raise conflict("이미 사용 중인 닉네임입니다.", "NICKNAME_DUPLICATE")
        if payload.email and user_crud.get_by_email(db, payload.email):
            raise conflict("이미 사용 중인 이메일입니다.", "EMAIL_DUPLICATE")
        raise conflict("이미 사용 중인 값입니다.", "DUPLICATE")
    post_count, comment_count = user_crud.counts(db, current.id)
    return UserMe(
        id=current.id,
        username=current.username,
        email=current.email,
        nickname=current.nickname,
        is_active=current.is_active,
        created_at=current.created_at,
        post_count=post_count,
        comment_count=comment_count,
    )


@router.patch("/me/password", response_model=Message)
def change_my_password(
    payload: PasswordChange,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current.password_hash):
        raise unauthorized("현재 비밀번호가 올바르지 않습니다.", "WRONG_PASSWORD")
    user_crud.change_password(db, current, payload.new_password)
    token_crud.revoke_all_for_user(db, current.id)  # 비번 변경 시 기존 세션 무효화
    return Message(detail="비밀번호가 변경되었습니다. 다시 로그인해주세요.")


@router.delete("/me", response_model=Message, status_code=status.HTTP_200_OK)
def delete_me(
    payload: UserDelete,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.password, current.password_hash):
        raise unauthorized("비밀번호가 올바르지 않습니다.", "INVALID_PASSWORD")
    token_crud.revoke_all_for_user(db, current.id)
    user_crud.delete(db, current)
    return Message(detail="회원 탈퇴가 완료되었습니다.")
