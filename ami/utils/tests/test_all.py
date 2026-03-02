def test_ping(django_app):
    response = django_app.get("/ping")
    assert response.status_code == 200
