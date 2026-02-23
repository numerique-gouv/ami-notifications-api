import pytest
from litestar import Litestar
from litestar.testing import TestClient

from tests.base import ConnectedTestClient


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


async def check_url_access(
    tested_url: str,
    connected_test_client: ConnectedTestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.admin.auth.AMI_ADMIN_RESTRICTED_ACCESS", "false")
    response = connected_test_client.get(tested_url, follow_redirects=False)
    assert response.status_code == 200

    monkeypatch.setattr("app.admin.auth.AMI_ADMIN_RESTRICTED_ACCESS", "true")
    monkeypatch.setattr("app.admin.auth.AMI_ADMIN_RESTRICTED_TO", "")
    response = connected_test_client.get(tested_url, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/ami_admin/unauthorized"

    monkeypatch.setattr("app.admin.auth.AMI_ADMIN_RESTRICTED_TO", "email@foo.com")
    response = connected_test_client.get(tested_url, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/ami_admin/unauthorized"

    monkeypatch.setattr(
        "app.admin.auth.AMI_ADMIN_RESTRICTED_TO", "email@foo.com, ,, angela@dubois.fr "
    )
    response = connected_test_client.get(tested_url, follow_redirects=False)
    assert response.status_code == 200
