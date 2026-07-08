import os
import secrets
import uuid

from fastapi import UploadFile
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.errors import bad_request
from app.models.transport import TransportComment, TransportRecord
from app.models.user import User


def generate_guardian_code() -> str:
    """6자리 보호자 인증 코드."""
    return f"{secrets.randbelow(1000000):06d}"


def _ext(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def save_image(upload: UploadFile) -> str:
    """이송 기록 대표 이미지 저장 후 stored_name 반환(확장자·용량 검증)."""
    ext = _ext(upload.filename or "").lstrip(".")
    allowed = settings.allowed_ext_set
    if allowed and ext not in allowed:
        raise bad_request(
            f"허용되지 않는 파일 형식입니다(.{ext or '?'}).", "FILE_TYPE_NOT_ALLOWED"
        )
    contents = upload.file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise bad_request(
            f"파일 용량이 제한({settings.MAX_UPLOAD_SIZE_MB}MB)을 초과했습니다.",
            "FILE_TOO_LARGE",
        )
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{_ext(upload.filename or '')}"
    with open(os.path.join(settings.UPLOAD_DIR, stored_name), "wb") as f:
        f.write(contents)
    return stored_name


def create(
    db: Session,
    *,
    user_id: int,
    patient_name: str,
    from_hospital: str,
    to_hospital: str,
    distance_km: int,
    duration_min: int,
    crew: str,
    detail: str,
    image_name: str | None,
    guardian_name: str,
) -> TransportRecord:
    rec = TransportRecord(
        user_id=user_id,
        patient_name=patient_name,
        from_hospital=from_hospital,
        to_hospital=to_hospital,
        distance_km=distance_km,
        duration_min=duration_min,
        crew=crew,
        detail=detail,
        image_name=image_name,
        guardian_name=guardian_name,
        guardian_code=generate_guardian_code(),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def verify_guardian(rec: TransportRecord, name: str, code: str) -> bool:
    """보호자 이름 + 코드 일치 확인."""
    return (
        bool(rec.guardian_code)
        and name.strip() == rec.guardian_name.strip()
        and code.strip() == rec.guardian_code.strip()
    )


def list_comments(db: Session, record_id: int) -> list[TransportComment]:
    return list(
        db.scalars(
            select(TransportComment)
            .where(TransportComment.record_id == record_id)
            .order_by(asc(TransportComment.created_at), asc(TransportComment.id))
        ).all()
    )


def comment_count(db: Session, record_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(TransportComment)
            .where(TransportComment.record_id == record_id)
        )
        or 0
    )


def create_comment(
    db: Session,
    *,
    record_id: int,
    guardian_name: str,
    content: str,
    medical: int | None,
    driving: int | None,
    hygiene: int | None,
    recommend: int | None,
) -> TransportComment:
    c = TransportComment(
        record_id=record_id,
        guardian_name=guardian_name,
        content=content,
        medical=medical,
        driving=driving,
        hygiene=hygiene,
        recommend=recommend,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def get(db: Session, record_id: int) -> TransportRecord | None:
    return db.scalar(
        select(TransportRecord)
        .options(selectinload(TransportRecord.author))
        .where(TransportRecord.id == record_id)
    )


def increment_view(db: Session, rec: TransportRecord) -> None:
    rec.view_count = TransportRecord.view_count + 1
    db.commit()
    db.refresh(rec)


def delete(db: Session, rec: TransportRecord) -> None:
    if rec.image_name:
        path = os.path.join(settings.UPLOAD_DIR, rec.image_name)
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
    db.delete(rec)
    db.commit()


def list_records(
    db: Session,
    *,
    page: int,
    size: int,
    search_type: str | None,
    keyword: str | None,
):
    stmt = (
        select(TransportRecord)
        .options(selectinload(TransportRecord.author))
        .order_by(desc(TransportRecord.created_at), desc(TransportRecord.id))
    )
    if keyword:
        kw = f"%{keyword}%"
        if search_type == "title":
            stmt = stmt.where(TransportRecord.patient_name.like(kw))
        elif search_type == "hospital":
            stmt = stmt.where(
                or_(
                    TransportRecord.from_hospital.like(kw),
                    TransportRecord.to_hospital.like(kw),
                )
            )
        elif search_type == "author":
            stmt = stmt.join(User, User.id == TransportRecord.user_id).where(
                User.nickname.like(kw)
            )
        else:  # 전체
            stmt = stmt.join(User, User.id == TransportRecord.user_id).where(
                or_(
                    TransportRecord.patient_name.like(kw),
                    TransportRecord.from_hospital.like(kw),
                    TransportRecord.to_hospital.like(kw),
                    User.nickname.like(kw),
                )
            )

    total = db.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    ) or 0
    rows = db.scalars(stmt.offset((page - 1) * size).limit(size)).all()
    return rows, total
