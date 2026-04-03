def test_userinfo(
    app,
) -> None:
    response = app.get("/api/v1/fi/userinfo/")
    assert response.status_code == 200
