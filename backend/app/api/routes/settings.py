from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.database import get_db
from app.crud import setting as setting_crud
from app.models.user import User
from app.schemas.setting import SiteSettingsOut, SiteSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SiteSettingsOut)
def get_settings(db: Session = Depends(get_db)):
    """공개 설정 조회 — 랜딩페이지가 비로그인 상태로 호출한다."""
    return SiteSettingsOut(**setting_crud.get_all(db))


@router.patch("", response_model=SiteSettingsOut)
def update_settings(
    payload: SiteSettingsUpdate,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """설정 변경 — 관리자만."""
    for key, value in payload.model_dump().items():
        setting_crud.set_value(db, key, value)
    db.commit()
    return SiteSettingsOut(**setting_crud.get_all(db))
