"""pytest 공통 설정 — 테스트 DB 준비 + TestClient.

- DATABASE_URL / REDIS_URL 은 CI(또는 로컬)에서 환경변수로 주입한다.
- 모델 기준으로 테이블을 생성(create_all)하고, 세션 종료 시 제거한다.
- Kafka/RabbitMQ 발행은 실패해도 흐름을 끊지 않으므로 별도 준비가 필요 없다.
"""

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 — 모든 모델을 metadata에 등록
from app.core.database import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def signup(client, username, nickname, email=None, password="Testpw123"):
    return client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email or f"{username}@example.com",
            "nickname": nickname,
            "password": password,
        },
    )


def auth_headers(client, username, nickname):
    """회원가입 + 로그인 후 Authorization 헤더 반환."""
    signup(client, username, nickname)
    r = client.post(
        "/api/auth/login", json={"username": username, "password": "Testpw123"}
    )
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
