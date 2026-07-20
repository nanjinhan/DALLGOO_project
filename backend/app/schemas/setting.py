import re

from pydantic import BaseModel, field_validator

# watch?v= / youtu.be / embed / shorts / live 형태에서 11자리 영상 ID 추출
_YOUTUBE_RE = re.compile(
    r"(?:youtu\.be/|v=|/embed/|/shorts/|/live/)([A-Za-z0-9_-]{11})"
)
_BARE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_youtube_id(value: str) -> str | None:
    """유튜브 주소(또는 ID)에서 영상 ID를 뽑는다. 못 뽑으면 None."""
    raw = (value or "").strip()
    if not raw:
        return None
    match = _YOUTUBE_RE.search(raw)
    if match:
        return match.group(1)
    return raw if _BARE_ID_RE.match(raw) else None


class SiteSettingsOut(BaseModel):
    """공개 설정 — 비로그인도 조회 가능(랜딩페이지가 사용)."""

    intro_video_url: str


class SiteSettingsUpdate(BaseModel):
    intro_video_url: str

    @field_validator("intro_video_url")
    @classmethod
    def check_youtube(cls, v: str) -> str:
        """빈 값이면 영상 숨김. 값이 있으면 유튜브 주소여야 한다."""
        raw = (v or "").strip()
        if not raw:
            return ""
        video_id = extract_youtube_id(raw)
        if video_id is None:
            raise ValueError(
                "유튜브 주소 형식이 아닙니다. 예: https://www.youtube.com/watch?v=영상ID"
            )
        # 저장은 표준 주소로 통일 — 프론트가 어떤 형태로 받아도 동일하게 동작한다.
        return f"https://www.youtube.com/watch?v={video_id}"
