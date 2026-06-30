from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import forbidden, unauthorized
from app.core.security import ACCESS_TOKEN_TYPE, decode_token
from app.crud import user as user_crud
from app.models.user import User

# auto_error=False → 토큰 없을 때 직접 401(한국어/code) 처리
_bearer = HTTPBearer(auto_error=False)
_bearer_optional = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise unauthorized()
    payload = decode_token(creds.credentials, expected_type=ACCESS_TOKEN_TYPE)
    if payload is None:
        raise unauthorized("유효하지 않은 토큰입니다.", "INVALID_TOKEN")
    user = user_crud.get(db, int(payload["sub"]))
    if user is None or not user.is_active:
        raise unauthorized("유효하지 않은 사용자입니다.", "INVALID_USER")
    return user


def get_admin_user(current: User = Depends(get_current_user)) -> User:
    """관리자만 통과. 아니면 403."""
    if not current.is_admin:
        raise forbidden("관리자 권한이 필요합니다.", "ADMIN_ONLY")
    return current


def get_optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """비로그인 허용 엔드포인트에서 좋아요 여부 등을 표시하기 위한 선택적 사용자."""
    if creds is None:
        return None
    payload = decode_token(creds.credentials, expected_type=ACCESS_TOKEN_TYPE)
    if payload is None:
        return None
    return user_crud.get(db, int(payload["sub"]))
