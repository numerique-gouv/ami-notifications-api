import time

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


@pytest.mark.django_db
def test_access_key_rate_limit(app, settings):
    settings.WEB_APP_ACCESS_KEYS = {"123", "456"}
    settings.WEB_APP_ACCESS_KEY_RATE_LIMIT = "1/s"
    settings.WEB_APP_ACCESS_KEY_RATE_LIMIT_DELAY = 1
    t0 = time.time()
    app.post("/api/v1/access-key", params={"key": "789"}, status=401)
    assert time.time() - t0 < 0.5
    app.post("/api/v1/access-key", params={"key": "789"}, status=401)
    assert time.time() - t0 > 1
