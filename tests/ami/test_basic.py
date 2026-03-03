import pytest
from litestar import Litestar
from litestar.testing import TestClient

pytestmark = pytest.mark.skip("skip tests for Django migration")


async def test_ping(
    test_client: TestClient[Litestar],
):
    response = test_client.head("/ping")
    assert response.status_code == 200


async def test_get_sector_identifier_url(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.env.PUBLIC_SECTOR_IDENTIFIER_URL", "  https://example.com  \nfoobar \n"
    )
    response = test_client.get("/sector_identifier_url")
    assert response.json() == ["https://example.com", "foobar"]
