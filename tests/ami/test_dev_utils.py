from litestar import Litestar
from litestar.testing import TestClient


async def test_recipient_fc_hash(
    test_client: TestClient[Litestar],
) -> None:
    params = {
        "given_name": "Angela Claire Louise",
        "family_name": "DUBOIS",
        "birthdate": "1962-08-24",
        "gender": "female",
        "birthplace": "75107",
        "birthcountry": "99100",
    }
    response = test_client.get("/dev-utils/recipient-fc-hash", params=params)
    assert response.text == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
