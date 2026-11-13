import pytest


@pytest.mark.django_db
def test_get_trusted_urls(app, settings):
    settings.TRUSTED_URLS = ""
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": []}

    settings.TRUSTED_URLS = r".*\.gouv\.fr"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": [r".*\.gouv\.fr"]}

    settings.TRUSTED_URLS = "https://test1.fr,https://test2.fr"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": ["https://test1.fr", "https://test2.fr"]}

    settings.TRUSTED_URLS = r".*\.gouv\.fr,https://test.fr"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": [r".*\.gouv\.fr", "https://test.fr"]}

    settings.TRUSTED_URLS = r",  .*\.gouv\.fr ,   https://test.fr     ,"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": [r".*\.gouv\.fr", "https://test.fr"]}
