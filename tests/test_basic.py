from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient


def test_homepage_title(test_client: TestClient[Litestar]) -> None:
    response = test_client.get("/")
    assert response.status_code == HTTP_200_OK
    assert "<title>Notification test</title>" in response.text
