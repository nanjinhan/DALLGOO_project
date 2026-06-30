from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.post import AuthorOut


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    parent_id: int | None
    content: str
    author: AuthorOut | None
    is_deleted: bool
    like_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    updated_at: datetime
    replies: list["CommentOut"] = []


CommentOut.model_rebuild()


class CommentListResponse(BaseModel):
    items: list[CommentOut]
