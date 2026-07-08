from datetime import datetime

from pydantic import BaseModel, Field


class TransportListItem(BaseModel):
    """갤러리 목록용 요약."""

    id: int
    title: str  # 예: "○○○님 이송 기록" (마스킹)
    author: str  # 마스킹된 작성자 (예: 박**)
    from_hospital: str
    to_hospital: str
    has_image: bool
    view_count: int
    created_at: datetime


class TransportDetail(BaseModel):
    id: int
    title: str
    author: str
    from_hospital: str
    to_hospital: str
    distance_km: int
    duration_min: int
    crew: list[str]  # 마스킹된 크루원 이름들
    has_image: bool
    view_count: int
    comment_count: int = 0
    created_at: datetime
    # 관리자에게만 채워지는 보호자 인증 정보(그 외에는 None)
    guardian_name: str | None = None
    guardian_code: str | None = None


class GuardianVerifyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=12)


class GuardianVerifyResponse(BaseModel):
    """인증 성공 시 잠금 해제된 정보."""

    patient_name: str
    detail: str


class TransportCommentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=12)
    content: str = Field(min_length=1, max_length=100)
    # 평가(첫 댓글 필수) — 1~4 / 추천 1~10
    medical: int | None = Field(default=None, ge=1, le=4)
    driving: int | None = Field(default=None, ge=1, le=4)
    hygiene: int | None = Field(default=None, ge=1, le=4)
    recommend: int | None = Field(default=None, ge=1, le=10)


class TransportCommentOut(BaseModel):
    id: int
    guardian_name: str  # 마스킹
    content: str
    medical: int | None = None
    driving: int | None = None
    hygiene: int | None = None
    recommend: int | None = None
    created_at: datetime
