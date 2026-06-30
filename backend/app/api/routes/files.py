import os

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import forbidden, not_found
from app.crud import file as file_crud
from app.crud import post as post_crud
from app.models.user import User
from app.schemas.common import Message

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file = file_crud.get(db, file_id)
    if file is None:
        raise not_found("파일을 찾을 수 없습니다.", "FILE_NOT_FOUND")
    path = file_crud.disk_path(file)
    if not os.path.exists(path):
        raise not_found("파일이 서버에 존재하지 않습니다.", "FILE_MISSING")
    return FileResponse(
        path,
        filename=file.original_name,
        media_type=file.content_type,
    )


@router.delete("/{file_id}", response_model=Message)
def delete_file(
    file_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file = file_crud.get(db, file_id)
    if file is None:
        raise not_found("파일을 찾을 수 없습니다.", "FILE_NOT_FOUND")
    post = post_crud.get(db, file.post_id)
    if post is None or post.user_id != current.id:
        raise forbidden("본인 글의 파일만 삭제할 수 있습니다.", "NOT_OWNER")
    file_crud.delete(db, file)
    return Message(detail="파일이 삭제되었습니다.")
