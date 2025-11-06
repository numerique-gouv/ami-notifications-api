from litestar import Litestar
from litestar.testing import TestClient


async def check_url_when_logged_out(
    tested_url: str,
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get(tested_url, follow_redirects=False)
    assert response.status_code == 302
    assert "redirect_once_connected" in test_client.get_session_data()
    assert (
        test_client.get_session_data()["redirect_once_connected"]
        == f"http://testserver.local{tested_url}"
    )
