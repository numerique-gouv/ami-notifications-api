import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock

from app.httpx import httpx
from app.models import User
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_get_api_particulier_quotient(
    user: User,
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    login(user, test_client)

    fake_quotient_data = {"foo": "bar"}
    auth = {"fc_authorization": "Bearer foobar_access_token"}
    fc_auth = {"authorization": "Bearer foobar_access_token"}
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=fc_auth,
        json=fake_quotient_data,
    )
    response = test_client.get("/data/api-particulier/quotient", headers=auth)

    assert response.status_code == HTTP_200_OK
    assert response.json() == fake_quotient_data


async def test_get_api_particulier_quotient_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/data/api-particulier/quotient", test_client)


async def test_get_api_particulier_quotient_without_scope(
    user: User,
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock: HTTPXMock,
) -> None:
    # No `cnaf_quotient_familial` like in production
    monkeypatch.setattr("app.env.PUBLIC_FC_SCOPE", "openid identite_pivot preferred_username email")
    login(user, test_client)
    auth = {"fc_authorization": "Bearer foobar_access_token"}
    response = test_client.get("/data/api-particulier/quotient", headers=auth)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert response.text == ""
    assert not httpx_mock.get_requests()


async def test_get_holidays(
    user: User,
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    login(user, test_client)

    fake_holidays_data = [
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2025-12-19T23:00:00+00:00",
            "end_date": "2026-01-04T23:00:00+00:00",
            "location": "Bordeaux",
            "zones": "Zone A",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2025-12-19T23:00:00+00:00",
            "end_date": "2026-01-04T23:00:00+00:00",
            "location": "Bordeaux",
            "zones": "Zone B",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2025-12-19T23:00:00+00:00",
            "end_date": "2026-01-04T23:00:00+00:00",
            "location": "Versailles",
            "zones": "Zone C",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances d'Hiver",
            "population": "-",
            "start_date": "2026-02-06T23:00:00+00:00",
            "end_date": "2026-02-22T23:00:00+00:00",
            "location": "Bordeaux",
            "zones": "Zone A",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances d'Hiver",
            "population": "-",
            "start_date": "2026-02-13T23:00:00+00:00",
            "end_date": "2026-03-01T23:00:00+00:00",
            "location": "Lille",
            "zones": "Zone B",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances d'Hiver",
            "population": "-",
            "start_date": "2026-02-20T23:00:00+00:00",
            "end_date": "2026-03-08T23:00:00+00:00",
            "location": "Versailles",
            "zones": "Zone C",
            "annee_scolaire": "2025-2026",
        },
    ]
    fake_holidays_data = {"total_counts": len(fake_holidays_data), "results": fake_holidays_data}

    httpx_mock.add_response(
        url=httpx.URL(
            "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
            params={
                "where": (
                    "end_date >= date'2025-11-12' AND start_date < date'2026-09-15' AND "
                    "(location = 'Bordeaux' OR location = 'Lille' OR location = 'Versailles') "
                    "AND population IN ('-', 'Élèves')"
                ),
                "order_by": "start_date",
                "limit": 100,
            },
        ),
        json=fake_holidays_data,
    )

    # christmas holidays are deduplicated: the dates are the same for all zones
    holidays = [
        {
            "description": "Vacances de Noël",
            "start_date": "2025-12-19T23:00:00Z",
            "end_date": "2026-01-04T23:00:00Z",
            "zones": "",
            "emoji": "🎄",
        },
        {
            "description": "Vacances d'Hiver",
            "start_date": "2026-02-06T23:00:00Z",
            "end_date": "2026-02-22T23:00:00Z",
            "zones": "Zone A",
            "emoji": "❄️",
        },
        {
            "description": "Vacances d'Hiver",
            "start_date": "2026-02-13T23:00:00Z",
            "end_date": "2026-03-01T23:00:00Z",
            "zones": "Zone B",
            "emoji": "❄️",
        },
        {
            "description": "Vacances d'Hiver",
            "start_date": "2026-02-20T23:00:00Z",
            "end_date": "2026-03-08T23:00:00Z",
            "zones": "Zone C",
            "emoji": "❄️",
        },
    ]
    response = test_client.get("/data/holidays", params={"current_date": "2025-12-12"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == holidays


async def test_get_holidays_school_year(
    user: User,
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    login(user, test_client)

    httpx_mock.add_response(is_reusable=True)

    # get holidays of current school year only
    test_client.get("/data/holidays", params={"current_date": "2025-09-01"})
    request = httpx_mock.get_requests()[0]
    assert (
        "end_date >= date'2025-08-02' AND start_date < date'2026-09-15'"
        in request.url.params.get("where")
    )

    test_client.get("/data/holidays", params={"current_date": "2025-12-31"})
    request = httpx_mock.get_requests()[1]
    assert (
        "end_date >= date'2025-12-01' AND start_date < date'2026-09-15'"
        in request.url.params.get("where")
    )

    # get holidays of current and next school years
    test_client.get("/data/holidays", params={"current_date": "2026-01-01"})
    request = httpx_mock.get_requests()[2]
    assert (
        "end_date >= date'2025-12-02' AND start_date < date'2027-09-15'"
        in request.url.params.get("where")
    )

    test_client.get("/data/holidays", params={"current_date": "2026-08-31"})
    request = httpx_mock.get_requests()[3]
    assert (
        "end_date >= date'2026-08-01' AND start_date < date'2027-09-15'"
        in request.url.params.get("where")
    )


async def test_get_holidays_emoji(
    user: User,
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    login(user, test_client)

    def mock_data(description: str):
        fake_holidays_data = [
            {
                "description": description,
                "population": "-",
                "start_date": "2025-12-19T23:00:00+00:00",
                "end_date": "2026-01-04T23:00:00+00:00",
                "location": "Bordeaux",
                "zones": "Zone A",
                "annee_scolaire": "2025-2026",
            },
        ]
        fake_holidays_data = {
            "total_counts": len(fake_holidays_data),
            "results": fake_holidays_data,
        }

        httpx_mock.add_response(
            json=fake_holidays_data,
        )

    mock_data("Vacances de la Toussaint")
    response = test_client.get("/data/holidays", params={"current_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "🍁"

    mock_data("Vacances de Noël")
    response = test_client.get("/data/holidays", params={"current_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "🎄"

    mock_data("Vacances d'Hiver")
    response = test_client.get("/data/holidays", params={"current_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "❄️"

    mock_data("Vacances de Printemps")
    response = test_client.get("/data/holidays", params={"current_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "🌸"

    mock_data("Pont de l'Ascension")
    response = test_client.get("/data/holidays", params={"current_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == ""

    mock_data("Vacances d'Été")
    response = test_client.get("/data/holidays", params={"current_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "☀️"

    mock_data("Unknown")
    response = test_client.get("/data/holidays", params={"current_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == ""


async def test_get_holidays_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/data/holidays", test_client)
