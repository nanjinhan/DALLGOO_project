from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    file_size: int
    content_type: str
    download_url: str = ""


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)


class PostListItem(BaseModel):
    """목록용 요약."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: AuthorOut
    view_count: int
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime


class PostDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author: AuthorOut
    view_count: int
    like_count: int = 0
    liked_by_me: bool = False
    comment_count: int = 0
    files: list[FileOut] = []
    created_at: datetime
    updated_at: datetime
