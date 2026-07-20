from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.setting import SiteSetting

# 허용 키와 기본값. 레코드가 없으면 여기 값을 쓴다(초기 시딩 불필요).
DEFAULTS: dict[str, str] = {
    "intro_video_url": "https://www.youtube.com/watch?v=34iGMGGwTj0",
}


def get_all(db: Session) -> dict[str, str]:
    """전체 설정을 기본값 위에 덮어써서 반환."""
    rows = db.scalars(select(SiteSetting)).all()
    result = dict(DEFAULTS)
    for row in rows:
        if row.key in DEFAULTS:
            result[row.key] = row.value
    return result


def set_value(db: Session, key: str, value: str) -> None:
    """upsert. 커밋은 호출한 쪽에서 한 번에 한다."""
    if key not in DEFAULTS:
        raise ValueError(f"알 수 없는 설정 키입니다: {key}")
    row = db.get(SiteSetting, key)
    if row is None:
        db.add(SiteSetting(key=key, value=value))
    else:
        row.value = value
