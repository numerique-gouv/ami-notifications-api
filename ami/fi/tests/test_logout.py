def test_logout(
    django_app,
) -> None:
    response = django_app.get("/api/v1/fi/logout/")
    assert response.status_code == 200
