def test_token(
    django_app,
) -> None:
    response = django_app.post("/api/v1/fi/token/")
    assert response.status_code == 200
