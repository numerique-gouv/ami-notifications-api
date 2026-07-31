import pytest


@pytest.mark.django_db
def test_access_key(app, settings):
    settings.WEB_APP_ACCESS_KEYS = set()
    app.post("/api/v1/access-key", status=404)
    settings.WEB_APP_ACCESS_KEYS = {"123", "456"}
    app.get("/api/v1/access-key", status=405)
    app.post("/api/v1/access-key", status=401)
    app.post("/api/v1/access-key", params={"key": "123"}, status=200)
    app.post("/api/v1/access-key", params={"key": "456"}, status=200)
    app.post("/api/v1/access-key", params={"key": "789"}, status=401)
