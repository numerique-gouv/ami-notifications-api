def test_logout(
    app,
) -> None:
    response = app.get("/api/v1/fi/logout/")
    assert response.status_code == 200
