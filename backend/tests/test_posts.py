from tests.conftest import auth_headers


def test_create_requires_auth(client):
    # 비로그인 글쓰기 → 401
    r = client.post("/api/posts", data={"title": "제목", "content": "내용"})
    assert r.status_code == 401


def test_post_create_and_read(client):
    h = auth_headers(client, "poster", "포스터")
    r = client.post(
        "/api/posts", data={"title": "첫 글", "content": "본문입니다"}, headers=h
    )
    assert r.status_code == 201, r.text
    pid = r.json()["data"]["id"]

    # 상세 조회
    r = client.get(f"/api/posts/{pid}")
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "첫 글"

    # 목록에 최소 1건
    r = client.get("/api/posts")
    assert r.json()["data"]["total"] >= 1


def test_secret_post_permission(client):
    owner = auth_headers(client, "ownerx", "오너엑스")
    other = auth_headers(client, "otherx", "아더엑스")

    r = client.post(
        "/api/posts",
        data={"title": "비밀 문의", "content": "비밀 내용", "is_secret": "true"},
        headers=owner,
    )
    assert r.status_code == 201
    pid = r.json()["data"]["id"]

    # 작성자 본인은 열람 가능
    r = client.get(f"/api/posts/{pid}", headers=owner)
    assert r.status_code == 200

    # 타인은 403 차단
    r = client.get(f"/api/posts/{pid}", headers=other)
    assert r.status_code == 403
    assert r.json()["code"] == "SECRET_POST"

    # 비로그인 목록에서는 제목이 마스킹됨
    r = client.get("/api/posts")
    items = r.json()["data"]["items"]
    secret = next((i for i in items if i["id"] == pid), None)
    assert secret is not None
    assert secret["is_secret"] is True
    assert secret["title"] == "🔒 비밀글입니다"
