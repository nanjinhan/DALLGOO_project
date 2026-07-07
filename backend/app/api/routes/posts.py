from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user
from app.core.database import get_db
from app.core.errors import forbidden, not_found
from app.core.events import publish_activity
from app.crud import file as file_crud
from app.crud import like as like_crud
from app.crud import notification as notif_crud
from app.crud import post as post_crud
from app.models.user import User
from app.schemas.common import LikeResponse, Message, Page
from app.schemas.post import PostDetail, PostListItem, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostDetail, status_code=status.HTTP_201_CREATED)
def create_post(
    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1),
    files: list[UploadFile] | None = File(default=None),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = post_crud.create(db, user_id=current.id, title=title, content=content)
    if files:
        for upload in files:
            if upload and upload.filename:
                file_crud.save_upload(db, post.id, upload)
    publish_activity("post", current.nickname, f"'{title[:30]}' 글을 작성했습니다.")
    return _to_detail(db, post, current)


@router.get("", response_model=Page[PostListItem])
def list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    sort: str = Query("latest"),
    search_type: str | None = Query(None),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    rows, total = post_crud.list_posts(
        db,
        page=page,
        size=size,
        sort=sort,
        search_type=search_type,
        keyword=keyword,
    )
    items = [
        PostListItem(
            id=post.id,
            title=post.title,
            author={"id": post.author.id, "nickname": post.author.nickname},
            view_count=post.view_count,
            like_count=like_cnt,
            comment_count=comment_cnt,
            created_at=post.created_at,
        )
        for post, like_cnt, comment_cnt in rows
    ]
    total_pages = (total + size - 1) // size
    return Page(items=items, page=page, size=size, total=total, total_pages=total_pages)


@router.get("/{post_id}", response_model=PostDetail)
def get_post(
    post_id: int,
    current: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    post = post_crud.get_with_files(db, post_id)
    if post is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")
    post_crud.increment_view(db, post)
    return _to_detail(db, post, current)


@router.patch("/{post_id}", response_model=PostDetail)
def update_post(
    post_id: int,
    payload: PostUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = post_crud.get_with_files(db, post_id)
    if post is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")
    if post.user_id != current.id:
        raise forbidden("본인 글만 수정할 수 있습니다.", "NOT_OWNER")
    post_crud.update(db, post, title=payload.title, content=payload.content)
    return _to_detail(db, post, current)


@router.delete("/{post_id}", response_model=Message)
def delete_post(
    post_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = post_crud.get_with_files(db, post_id)
    if post is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")
    if post.user_id != current.id:
        raise forbidden("본인 글만 삭제할 수 있습니다.", "NOT_OWNER")
    post_crud.delete(db, post)
    return Message(detail="게시글이 삭제되었습니다.")


@router.post("/{post_id}/like", response_model=LikeResponse)
def like_post(
    post_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = post_crud.get(db, post_id)
    if post is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")
    if like_crud.add_post_like(db, post_id, current.id):
        notif_crud.notify(
            db,
            recipient_id=post.user_id,
            actor_id=current.id,
            type="post_like",
            message=f"{current.nickname}님이 회원님의 글을 좋아합니다.",
            post_id=post_id,
        )
        publish_activity(
            "like", current.nickname, f"'{post.title[:30]}' 글을 좋아합니다."
        )
    return LikeResponse(liked=True, like_count=like_crud.post_like_count(db, post_id))


@router.delete("/{post_id}/like", response_model=LikeResponse)
def unlike_post(
    post_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if post_crud.get(db, post_id) is None:
        raise not_found("게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")
    like_crud.remove_post_like(db, post_id, current.id)
    return LikeResponse(liked=False, like_count=like_crud.post_like_count(db, post_id))


def _to_detail(db: Session, post, current: User | None) -> PostDetail:
    liked = (
        current is not None
        and like_crud.post_like_exists(db, post.id, current.id)
    )
    return PostDetail(
        id=post.id,
        title=post.title,
        content=post.content,
        author={"id": post.author.id, "nickname": post.author.nickname},
        view_count=post.view_count,
        like_count=post_crud.like_count(db, post.id),
        liked_by_me=liked,
        comment_count=post_crud.comment_count(db, post.id),
        files=[
            {
                "id": f.id,
                "original_name": f.original_name,
                "file_size": f.file_size,
                "content_type": f.content_type,
                "download_url": f"/api/files/{f.id}/download",
            }
            for f in post.files
        ],
        created_at=post.created_at,
        updated_at=post.updated_at,
    )
