import json

from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock


async def test_get_api_particulier_quotient(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    fake_quotient_data = {"foo": "bar"}
    auth = {"authorization": "Bearer foobar_access_token"}
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=fake_quotient_data,
    )
    response = test_client.get("/data/api-particulier/quotient", headers=auth)

    assert response.status_code == HTTP_200_OK
    assert json.loads(response.text) == fake_quotient_data
