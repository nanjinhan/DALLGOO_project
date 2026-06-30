import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import bad_request, conflict, forbidden, unauthorized
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud import token as token_crud
from app.crud import user as user_crud
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import AvailableResponse, Message
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_by_username(db, payload.username):
        raise conflict("이미 사용 중인 아이디입니다.", "USERNAME_DUPLICATE")
    if user_crud.get_by_email(db, payload.email):
        raise conflict("이미 사용 중인 이메일입니다.", "EMAIL_DUPLICATE")
    if user_crud.get_by_nickname(db, payload.nickname):
        raise conflict("이미 사용 중인 닉네임입니다.", "NICKNAME_DUPLICATE")
    try:
        user = user_crud.create(
            db,
            username=payload.username,
            email=payload.email,
            nickname=payload.nickname,
            password=payload.password,
        )
    except IntegrityError:
        # 중복확인 통과 ~ 가입 사이의 race condition: DB UNIQUE가 최종 방어선.
        db.rollback()
        if user_crud.get_by_username(db, payload.username):
            raise conflict("이미 사용 중인 아이디입니다.", "USERNAME_DUPLICATE")
        if user_crud.get_by_email(db, payload.email):
            raise conflict("이미 사용 중인 이메일입니다.", "EMAIL_DUPLICATE")
        if user_crud.get_by_nickname(db, payload.nickname):
            raise conflict("이미 사용 중인 닉네임입니다.", "NICKNAME_DUPLICATE")
        raise conflict("이미 사용 중인 값입니다.", "DUPLICATE")
    return user


@router.get("/check-username", response_model=AvailableResponse)
def check_username(username: str = Query(...), db: Session = Depends(get_db)):
    # 저장 형식(소문자)에 맞춰 조회해야 중복 판정이 일치한다.
    normalized = username.strip().lower()
    return AvailableResponse(
        available=user_crud.get_by_username(db, normalized) is None
    )


@router.get("/check-email", response_model=AvailableResponse)
def check_email(email: str = Query(...), db: Session = Depends(get_db)):
    normalized = email.strip().lower()
    return AvailableResponse(available=user_crud.get_by_email(db, normalized) is None)


@router.get("/check-nickname", response_model=AvailableResponse)
def check_nickname(nickname: str = Query(...), db: Session = Depends(get_db)):
    return AvailableResponse(
        available=user_crud.get_by_nickname(db, nickname.strip()) is None
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.get_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise unauthorized("아이디 또는 비밀번호가 올바르지 않습니다.", "INVALID_CREDENTIALS")
    if not user.is_active:
        raise forbidden("탈퇴 또는 정지된 계정입니다.", "ACCOUNT_INACTIVE")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    token_crud.store_refresh(db, user.id, refresh)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    if decoded is None:
        raise unauthorized("유효하지 않은 리프레시 토큰입니다.", "INVALID_REFRESH")

    stored = token_crud.get_refresh(db, payload.refresh_token)
    if not token_crud.is_valid(stored):
        raise unauthorized("만료되었거나 폐기된 토큰입니다.", "EXPIRED_REFRESH")

    user_id = int(decoded["sub"])
    # Rotation: 기존 토큰 폐기 후 새 토큰 발급
    token_crud.revoke(db, payload.refresh_token)
    access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)
    token_crud.store_refresh(db, user_id, new_refresh)
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout", response_model=Message)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    token_crud.revoke(db, payload.refresh_token)
    return Message(detail="로그아웃되었습니다.")


@router.post("/password/forgot", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, payload.email)
    # 이메일 존재 여부를 노출하지 않되, 학습용으로 토큰은 반환
    if user is None:
        return ForgotPasswordResponse(
            detail="해당 이메일로 재설정 안내를 보냈습니다.", reset_token=""
        )
    reset_token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_crud.create_reset(db, user.id, reset_token, expires)
    return ForgotPasswordResponse(
        detail="해당 이메일로 재설정 안내를 보냈습니다.", reset_token=reset_token
    )


@router.post("/password/reset", response_model=Message)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    prt = token_crud.get_reset(db, payload.token)
    if prt is None:
        raise bad_request("유효하지 않거나 만료된 토큰입니다.", "TOKEN_EXPIRED")
    if prt.used:
        raise bad_request("이미 사용된 토큰입니다.", "TOKEN_USED")
    if not token_crud.reset_is_valid(prt):
        raise bad_request("만료된 토큰입니다.", "TOKEN_EXPIRED")
    user = user_crud.get(db, prt.user_id)
    if user is None:
        raise unauthorized("유효하지 않은 사용자입니다.", "INVALID_USER")
    user_crud.change_password(db, user, payload.new_password)
    token_crud.mark_reset_used(db, prt)
    token_crud.revoke_all_for_user(db, user.id)  # 보안: 기존 세션 무효화
    return Message(detail="비밀번호가 변경되었습니다. 다시 로그인해주세요.")
