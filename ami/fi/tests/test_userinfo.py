def test_userinfo(
    django_app,
) -> None:
    response = django_app.get("/api/v1/fi/userinfo/")
    assert response.status_code == 200
