import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import security_store as store
from app.core.config import settings
from app.core.database import get_db
from app.core.email import send_email
from app.core.errors import bad_request, conflict, forbidden, too_many, unauthorized
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
    EmailRequest,
    EmailVerifyRequest,
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
logger = logging.getLogger("uvicorn.error")


@router.get("/config")
def auth_config():
    # 프론트가 '이메일 인증 단계'를 보여줄지 판단하는 용도
    return {"email_verification_required": settings.email_enabled}


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    # 메일 발송이 설정된 경우에만 이메일 인증을 요구(미설정 시 가입 막지 않음)
    if settings.email_enabled and not store.is_email_verified(payload.email):
        raise bad_request("이메일 인증을 먼저 완료해주세요.", "EMAIL_NOT_VERIFIED")
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
    # 가입 완료 → 인증완료 표시 소진
    store.clear_email_verified(payload.email)
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


# ===== 이메일 인증 (회원가입용) =====
@router.post("/email/send-code", response_model=Message)
def send_email_code(payload: EmailRequest, db: Session = Depends(get_db)):
    email = payload.email
    if user_crud.get_by_email(db, email):
        raise conflict("이미 가입된 이메일입니다.", "EMAIL_DUPLICATE")
    wait = store.code_resend_blocked_seconds(email)
    if wait > 0:
        raise too_many(
            f"인증번호는 {wait}초 후 다시 받을 수 있습니다.", "RESEND_TOO_SOON"
        )
    code = store.issue_code(email)
    send_email(
        email,
        "[달구 게시판] 이메일 인증번호",
        f"인증번호는 [{code}] 입니다.\n"
        f"{settings.EMAIL_CODE_TTL_MINUTES}분 안에 입력해주세요.",
    )
    return Message(
        detail=f"인증번호를 보냈습니다. {settings.EMAIL_CODE_TTL_MINUTES}분 안에 입력해주세요."
    )


@router.post("/email/verify", response_model=Message)
def verify_email_code(payload: EmailVerifyRequest):
    if not store.verify_code(payload.email, payload.code):
        raise bad_request("인증번호가 올바르지 않거나 만료되었습니다.", "INVALID_CODE")
    return Message(detail="이메일 인증이 완료되었습니다.")


# ===== 아이디 찾기 (이메일로 발송) =====
@router.post("/username/find", response_model=Message)
def find_username(payload: EmailRequest, db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, payload.email)
    # user enumeration 방지 → 존재 여부와 무관하게 같은 메시지
    if user:
        send_email(
            payload.email,
            "[달구 게시판] 아이디 안내",
            f"회원님의 아이디는 '{user.username}' 입니다.",
        )
    return Message(detail="가입된 이메일이라면 아이디를 보냈습니다.")


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1) 잠금 확인 (rate limiting): 너무 많이 틀렸으면 일정 시간 차단
    locked = store.login_locked_seconds(payload.username)
    if locked > 0:
        raise too_many(
            f"로그인 시도가 너무 많습니다. 약 {locked // 60 + 1}분 후 다시 시도해주세요.",
            "TOO_MANY_ATTEMPTS",
        )

    user = user_crud.get_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        # 2) 실패 기록 (+1). 한도 도달 시 안내
        count = store.login_record_fail(payload.username)
        left = settings.LOGIN_MAX_ATTEMPTS - count
        if left <= 0:
            raise too_many(
                f"비밀번호를 {settings.LOGIN_MAX_ATTEMPTS}회 틀렸습니다. "
                f"{settings.LOGIN_LOCK_MINUTES}분 후 다시 시도해주세요.",
                "TOO_MANY_ATTEMPTS",
            )
        raise unauthorized(
            f"아이디 또는 비밀번호가 올바르지 않습니다. (남은 시도 {left}회)",
            "INVALID_CREDENTIALS",
        )
    if not user.is_active:
        raise forbidden("탈퇴 또는 정지된 계정입니다.", "ACCOUNT_INACTIVE")

    # 3) 성공 → 실패 카운트 초기화
    store.login_reset(payload.username)
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
    # 이메일 존재 여부를 응답으로 노출하지 않는다(user enumeration 방지) → 항상 같은 메시지.
    detail = "가입된 이메일이라면 재설정 안내를 보냈습니다."
    if user is None:
        return ForgotPasswordResponse(detail=detail)

    reset_token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_crud.create_reset(db, user.id, reset_token, expires)

    # 토큰은 절대 응답에 넣지 않는다. 실서비스는 이메일 발송, 개발 중에는 서버 로그로만 확인.
    logger.info("[비밀번호 재설정] %s 토큰(30분 유효): %s", payload.email, reset_token)
    return ForgotPasswordResponse(detail=detail)


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
