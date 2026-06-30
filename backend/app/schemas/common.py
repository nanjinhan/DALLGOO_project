from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """공통 페이지네이션 응답."""

    items: list[T]
    page: int
    size: int
    total: int
    total_pages: int


class Message(BaseModel):
    detail: str


class AvailableResponse(BaseModel):
    available: bool


class LikeResponse(BaseModel):
    liked: bool
    like_count: int
