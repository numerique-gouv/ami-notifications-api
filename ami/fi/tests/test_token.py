def test_token(
    app,
) -> None:
    response = app.post("/api/v1/fi/token/")
    assert response.status_code == 200
