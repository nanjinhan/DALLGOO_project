import os

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.comment import Comment
from app.models.file import File
from app.models.like import PostLike
from app.models.post import Post

# 목록/상세에서 재사용하는 집계 서브쿼리 (post_id -> count)
_like_count_sq = (
    select(PostLike.post_id, func.count(PostLike.id).label("cnt"))
    .group_by(PostLike.post_id)
    .subquery()
)
_comment_count_sq = (
    select(Comment.post_id, func.count(Comment.id).label("cnt"))
    .where(Comment.is_deleted.is_(False))
    .group_by(Comment.post_id)
    .subquery()
)


def get(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


def get_with_files(db: Session, post_id: int) -> Post | None:
    return db.scalar(
        select(Post).options(selectinload(Post.files)).where(Post.id == post_id)
    )


def create(
    db: Session, *, user_id: int, title: str, content: str, is_secret: bool = False
) -> Post:
    post = Post(user_id=user_id, title=title, content=content, is_secret=is_secret)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update(
    db: Session,
    post: Post,
    *,
    title: str | None,
    content: str | None,
    is_secret: bool | None = None,
) -> Post:
    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    if is_secret is not None:
        post.is_secret = is_secret
    db.commit()
    db.refresh(post)
    return post


def suggest_titles(db: Session, keyword: str, limit: int = 8) -> list[str]:
    """검색 자동완성: 키워드가 제목에 포함된 공개글 제목을 최신순으로 반환."""
    like_kw = f"%{keyword}%"
    rows = db.scalars(
        select(Post.title)
        .where(Post.title.like(like_kw), Post.is_secret.is_(False))
        .order_by(desc(Post.created_at))
        .limit(limit)
    ).all()
    # 중복 제목 제거(순서 유지)
    seen: set[str] = set()
    result: list[str] = []
    for t in rows:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def increment_view(db: Session, post: Post) -> None:
    post.view_count = Post.view_count + 1
    db.commit()
    db.refresh(post)


def delete(db: Session, post: Post) -> None:
    """글 삭제 — 디스크의 실제 첨부파일까지 제거 후 DB 레코드 삭제(CASCADE)."""
    for f in list(post.files):
        path = os.path.join(settings.UPLOAD_DIR, f.stored_name)
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass  # 디스크 삭제 실패해도 DB 정합성은 유지
    db.delete(post)
    db.commit()


def like_count(db: Session, post_id: int) -> int:
    return (
        db.scalar(
            select(func.count()).select_from(PostLike).where(PostLike.post_id == post_id)
        )
        or 0
    )


def comment_count(db: Session, post_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Comment)
            .where(Comment.post_id == post_id, Comment.is_deleted.is_(False))
        )
        or 0
    )


def list_posts(
    db: Session,
    *,
    page: int,
    size: int,
    sort: str,
    search_type: str | None,
    keyword: str | None,
):
    """목록 조회 — (rows, total). rows 각 항목: (Post, like_cnt, comment_cnt)."""
    from app.models.user import User

    like_cnt = func.coalesce(_like_count_sq.c.cnt, 0)
    comment_cnt = func.coalesce(_comment_count_sq.c.cnt, 0)

    stmt = (
        select(Post, like_cnt, comment_cnt)
        .outerjoin(_like_count_sq, _like_count_sq.c.post_id == Post.id)
        .outerjoin(_comment_count_sq, _comment_count_sq.c.post_id == Post.id)
        .options(selectinload(Post.author))
    )

    # --- 검색 ---
    if keyword:
        like_kw = f"%{keyword}%"
        if search_type == "title":
            stmt = stmt.where(Post.title.like(like_kw))
        elif search_type == "content":
            stmt = stmt.where(Post.content.like(like_kw))
        elif search_type == "author":
            stmt = stmt.join(User, User.id == Post.user_id).where(
                User.nickname.like(like_kw)
            )
        else:  # title_content (기본)
            stmt = stmt.where(Post.title.like(like_kw) | Post.content.like(like_kw))

    # --- 정렬 ---
    if sort == "oldest":
        stmt = stmt.order_by(asc(Post.created_at), asc(Post.id))
    elif sort == "views":
        stmt = stmt.order_by(desc(Post.view_count), desc(Post.id))
    elif sort == "likes":
        stmt = stmt.order_by(desc(like_cnt), desc(Post.id))
    else:  # latest
        stmt = stmt.order_by(desc(Post.created_at), desc(Post.id))

    # --- total ---
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0

    # --- 페이지 ---
    rows = db.execute(stmt.offset((page - 1) * size).limit(size)).all()
    return rows, total
