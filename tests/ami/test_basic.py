import pytest
from litestar import Litestar
from litestar.testing import TestClient

from app.utils import ami_hash


async def test_get_sector_identifier_url(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.env.PUBLIC_SECTOR_IDENTIFIER_URL", "  https://example.com  \nfoobar \n"
    )
    response = test_client.get("/sector_identifier_url")
    assert response.json() == ["https://example.com", "foobar"]


async def test_ami_hash(
    test_client: TestClient[Litestar],
) -> None:
    given_name = "Angela Claire Louise"
    family_name = "DUBOIS"
    birthdate = "1962-08-24"
    gender = "female"
    birthplace = "75107"
    birthcountry = "99100"
    response = ami_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"

    birthplace = ""
    response = ami_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "7e74df2cbebae761eccedbc24b7fe589bb83137f7808a2930031f52c73d75efe"
