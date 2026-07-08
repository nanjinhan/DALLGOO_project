import os

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_optional_user
from app.core.config import settings
from app.core.database import get_db
from app.core.errors import bad_request, not_found
from app.crud import transport as tr_crud
from app.models.user import User
from app.schemas.common import Message, Page
from app.schemas.transport import (
    GuardianVerifyRequest,
    GuardianVerifyResponse,
    TransportCommentCreate,
    TransportCommentOut,
    TransportDetail,
    TransportListItem,
)

router = APIRouter(prefix="/transport", tags=["transport"])


def _mask_name(name: str) -> str:
    """이름 마스킹 — 첫 글자 + **. (예: 박영수 → 박**)"""
    name = (name or "").strip()
    if not name:
        return "익명"
    return name[0] + "**"


def _mask_crew(crew: str) -> list[str]:
    return [_mask_name(c) for c in crew.split(",") if c.strip()]


def _title(rec) -> str:
    # 환자 이름은 완전 마스킹
    return "***님 이송 기록"


@router.post("", response_model=TransportDetail, status_code=status.HTTP_201_CREATED)
def create_record(
    patient_name: str = Form(..., min_length=1, max_length=50),
    from_hospital: str = Form(..., min_length=1, max_length=120),
    to_hospital: str = Form(..., min_length=1, max_length=120),
    distance_km: int = Form(default=0, ge=0),
    duration_min: int = Form(default=0, ge=0),
    crew: str = Form(default=""),
    detail: str = Form(default=""),
    guardian_name: str = Form(default="", max_length=50),
    image: UploadFile | None = File(default=None),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    image_name = None
    if image and image.filename:
        image_name = tr_crud.save_image(image)
    rec = tr_crud.create(
        db,
        user_id=admin.id,
        patient_name=patient_name,
        from_hospital=from_hospital,
        to_hospital=to_hospital,
        distance_km=distance_km,
        duration_min=duration_min,
        crew=crew,
        detail=detail,
        image_name=image_name,
        guardian_name=guardian_name,
    )
    return _to_detail(rec, db, is_admin=True)


@router.get("", response_model=Page[TransportListItem])
def list_records(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=50),
    search_type: str | None = Query(None),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    rows, total = tr_crud.list_records(
        db, page=page, size=size, search_type=search_type, keyword=keyword
    )
    items = [
        TransportListItem(
            id=r.id,
            title=_title(r),
            author=_mask_name(r.author.nickname if r.author else ""),
            from_hospital=r.from_hospital,
            to_hospital=r.to_hospital,
            has_image=bool(r.image_name),
            view_count=r.view_count,
            created_at=r.created_at,
        )
        for r in rows
    ]
    total_pages = (total + size - 1) // size
    return Page(items=items, page=page, size=size, total=total, total_pages=total_pages)


@router.get("/{record_id}", response_model=TransportDetail)
def get_record(
    record_id: int,
    current: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    rec = tr_crud.get(db, record_id)
    if rec is None:
        raise not_found("이송 기록을 찾을 수 없습니다.", "TRANSPORT_NOT_FOUND")
    tr_crud.increment_view(db, rec)
    is_admin = current is not None and current.is_admin
    return _to_detail(rec, db, is_admin=is_admin)


@router.post("/{record_id}/verify", response_model=GuardianVerifyResponse)
def verify_guardian(
    record_id: int,
    payload: GuardianVerifyRequest,
    db: Session = Depends(get_db),
):
    rec = tr_crud.get(db, record_id)
    if rec is None:
        raise not_found("이송 기록을 찾을 수 없습니다.", "TRANSPORT_NOT_FOUND")
    if not tr_crud.verify_guardian(rec, payload.name, payload.code):
        raise bad_request(
            "보호자 이름 또는 인증 코드가 올바르지 않습니다.", "GUARDIAN_INVALID"
        )
    return GuardianVerifyResponse(patient_name=rec.patient_name, detail=rec.detail)


@router.get("/{record_id}/comments", response_model=list[TransportCommentOut])
def list_comments(record_id: int, db: Session = Depends(get_db)):
    rows = tr_crud.list_comments(db, record_id)
    return [
        TransportCommentOut(
            id=c.id,
            guardian_name=_mask_name(c.guardian_name),
            content=c.content,
            medical=c.medical,
            driving=c.driving,
            hygiene=c.hygiene,
            recommend=c.recommend,
            created_at=c.created_at,
        )
        for c in rows
    ]


@router.post(
    "/{record_id}/comments",
    response_model=TransportCommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    record_id: int,
    payload: TransportCommentCreate,
    db: Session = Depends(get_db),
):
    rec = tr_crud.get(db, record_id)
    if rec is None:
        raise not_found("이송 기록을 찾을 수 없습니다.", "TRANSPORT_NOT_FOUND")
    if not tr_crud.verify_guardian(rec, payload.name, payload.code):
        raise bad_request(
            "보호자 이름 또는 인증 코드가 올바르지 않습니다.", "GUARDIAN_INVALID"
        )
    # 첫 댓글에는 이송 서비스 평가가 필수
    is_first = tr_crud.comment_count(db, record_id) == 0
    if is_first and None in (
        payload.medical,
        payload.driving,
        payload.hygiene,
        payload.recommend,
    ):
        raise bad_request(
            "첫 댓글에는 이송 서비스 평가가 필수입니다.", "RATING_REQUIRED"
        )
    c = tr_crud.create_comment(
        db,
        record_id=record_id,
        guardian_name=payload.name.strip(),
        content=payload.content,
        medical=payload.medical if is_first else None,
        driving=payload.driving if is_first else None,
        hygiene=payload.hygiene if is_first else None,
        recommend=payload.recommend if is_first else None,
    )
    return TransportCommentOut(
        id=c.id,
        guardian_name=_mask_name(c.guardian_name),
        content=c.content,
        medical=c.medical,
        driving=c.driving,
        hygiene=c.hygiene,
        recommend=c.recommend,
        created_at=c.created_at,
    )


@router.get("/{record_id}/image")
def get_record_image(record_id: int, db: Session = Depends(get_db)):
    rec = tr_crud.get(db, record_id)
    if rec is None or not rec.image_name:
        raise not_found("이미지를 찾을 수 없습니다.", "IMAGE_NOT_FOUND")
    path = os.path.join(settings.UPLOAD_DIR, rec.image_name)
    if not os.path.exists(path):
        raise not_found("이미지를 찾을 수 없습니다.", "IMAGE_NOT_FOUND")
    return FileResponse(path)


@router.delete("/{record_id}", response_model=Message)
def delete_record(
    record_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    rec = tr_crud.get(db, record_id)
    if rec is None:
        raise not_found("이송 기록을 찾을 수 없습니다.", "TRANSPORT_NOT_FOUND")
    tr_crud.delete(db, rec)
    return Message(detail="이송 기록을 삭제했습니다.")


def _to_detail(rec, db: Session, *, is_admin: bool = False) -> TransportDetail:
    return TransportDetail(
        id=rec.id,
        title=_title(rec),
        author=_mask_name(rec.author.nickname if rec.author else ""),
        from_hospital=rec.from_hospital,
        to_hospital=rec.to_hospital,
        distance_km=rec.distance_km,
        duration_min=rec.duration_min,
        crew=_mask_crew(rec.crew),
        has_image=bool(rec.image_name),
        view_count=rec.view_count,
        comment_count=tr_crud.comment_count(db, rec.id),
        created_at=rec.created_at,
        # 관리자에게만 보호자 정보 노출(보호자에게 코드 전달용)
        guardian_name=rec.guardian_name if is_admin else None,
        guardian_code=rec.guardian_code if is_admin else None,
    )
