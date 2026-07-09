def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    # 공통 응답 봉투로 감싸져서 data 안에 실제 값
    assert r.json()["data"]["status"] == "ok"
