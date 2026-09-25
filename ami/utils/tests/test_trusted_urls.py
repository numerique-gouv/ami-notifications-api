import pytest

from ami.tests.utils import login
from ami.user.models import User


@pytest.mark.django_db
def test_get_trusted_urls(user: User, app, settings):
    login(app, user)

    settings.TRUSTED_URLS = ""
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": []}

    settings.TRUSTED_URLS = ".*\.gouv\.fr"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": [".*\.gouv\.fr"]}

    settings.TRUSTED_URLS = "https://test1.fr,https://test2.fr"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": ["https://test1.fr", "https://test2.fr"]}

    settings.TRUSTED_URLS = ".*\.gouv\.fr,https://test.fr"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": [".*\.gouv\.fr", "https://test.fr"]}

    settings.TRUSTED_URLS = ",  .*\.gouv\.fr ,   https://test.fr     ,"
    response = app.get("/api-utils/trusted_urls", status=200)
    assert response.json == {"trusted_urls": [".*\.gouv\.fr", "https://test.fr"]}
