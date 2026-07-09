from tests.conftest import signup


def test_signup_login_me(client):
    r = signup(client, "alice", "앨리스")
    assert r.status_code == 201, r.text
    assert r.json()["data"]["username"] == "alice"

    # 로그인 → 토큰 발급
    r = client.post("/api/auth/login", json={"username": "alice", "password": "Testpw123"})
    assert r.status_code == 200
    token = r.json()["data"]["access_token"]
    assert token

    # 내 정보 조회
    r = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["data"]["username"] == "alice"


def test_duplicate_username(client):
    signup(client, "bobby", "바비")
    r = signup(client, "bobby", "바비둘", email="bobby2@example.com")
    assert r.status_code == 409
    assert r.json()["code"] == "USERNAME_DUPLICATE"


def test_login_wrong_password(client):
    signup(client, "carol", "캐롤")
    r = client.post("/api/auth/login", json={"username": "carol", "password": "Wrongpw123"})
    assert r.status_code == 401
    assert r.json()["code"] == "INVALID_CREDENTIALS"


def test_check_username_availability(client):
    signup(client, "davey", "데이비")
    # 이미 있는 아이디 → 사용 불가
    r = client.get("/api/auth/check-username", params={"username": "davey"})
    assert r.json()["data"]["available"] is False
    # 없는 아이디 → 사용 가능
    r = client.get("/api/auth/check-username", params={"username": "freename99"})
    assert r.json()["data"]["available"] is True


def test_signup_invalid_password(client):
    # 대문자 없는 비밀번호 → 422 검증 오류
    r = client.post(
        "/api/auth/signup",
        json={
            "username": "evan",
            "email": "evan@example.com",
            "nickname": "에반",
            "password": "weakpassword1",
        },
    )
    assert r.status_code == 422
