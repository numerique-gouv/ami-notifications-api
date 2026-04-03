def test_authorize(
    app,
) -> None:
    response = app.get("/api/v1/fi/authorize/")
    assert response.status_code == 200
