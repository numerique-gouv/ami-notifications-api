def test_authorize(
    django_app,
) -> None:
    response = django_app.get("/api/v1/fi/authorize/")
    assert response.status_code == 200
