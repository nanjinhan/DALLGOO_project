import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import bad_request
from app.models.file import File


def _ext(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def save_upload(db: Session, post_id: int, upload: UploadFile) -> File:
    """단일 업로드 파일을 디스크에 저장하고 DB 레코드 생성."""
    # 1) 확장자 검증 (화이트리스트)
    ext = _ext(upload.filename or "").lstrip(".")
    allowed = settings.allowed_ext_set
    if allowed and ext not in allowed:
        raise bad_request(
            f"허용되지 않는 파일 형식입니다(.{ext or '?'}). "
            f"허용: {', '.join(sorted(allowed))}",
            "FILE_TYPE_NOT_ALLOWED",
        )

    # 2) 용량 검증
    contents = upload.file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise bad_request(
            f"파일 용량이 제한({settings.MAX_UPLOAD_SIZE_MB}MB)을 초과했습니다.",
            "FILE_TOO_LARGE",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{_ext(upload.filename or '')}"
    path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(path, "wb") as f:
        f.write(contents)

    record = File(
        post_id=post_id,
        original_name=upload.filename or stored_name,
        stored_name=stored_name,
        file_size=len(contents),
        content_type=upload.content_type or "application/octet-stream",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get(db: Session, file_id: int) -> File | None:
    return db.get(File, file_id)


def delete(db: Session, file: File) -> None:
    path = os.path.join(settings.UPLOAD_DIR, file.stored_name)
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
    db.delete(file)
    db.commit()


def disk_path(file: File) -> str:
    return os.path.join(settings.UPLOAD_DIR, file.stored_name)
