import httpx
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
    assert response.json() == fake_quotient_data


async def test_get_holidays(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
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
                    "(zones = 'Zone A' AND location = 'Bordeaux' OR zones = 'Zone B' "
                    "AND location = 'Lille' OR zones = 'Zone C' AND location = 'Versailles') "
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
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-12"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == holidays


async def test_get_holidays_school_year(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    fake_holidays_data_2526 = [
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
            "description": "Vacances d'Hiver",
            "population": "-",
            "start_date": "2026-02-13T23:00:00+00:00",
            "end_date": "2026-03-01T23:00:00+00:00",
            "location": "Lille",
            "zones": "Zone B",
            "annee_scolaire": "2025-2026",
        },
    ]
    fake_holidays_data_2627 = [
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2026-12-18T23:00:00+00:00",
            "end_date": "2027-01-03T23:00:00+00:00",
            "location": "Lille",
            "zones": "Zone B",
            "annee_scolaire": "2026-2027",
        },
        {
            "description": "Vacances de Printemps",
            "population": "-",
            "start_date": "2027-04-16T22:00:00+00:00",
            "end_date": "2027-05-02T22:00:00+00:00",
            "location": "Reims",
            "zones": "Zone B",
            "annee_scolaire": "2026-2027",
        },
    ]
    fake_holidays_data1 = {"total_counts": 2, "results": fake_holidays_data_2526}
    fake_holidays_data2 = {
        "total_counts": 4,
        "results": fake_holidays_data_2526 + fake_holidays_data_2627,
    }

    holidays_2526 = [
        {
            "description": "Vacances de Noël",
            "start_date": "2025-12-19T23:00:00Z",
            "end_date": "2026-01-04T23:00:00Z",
            "zones": "Zone B",
            "emoji": "🎄",
        },
        {
            "description": "Vacances d'Hiver",
            "start_date": "2026-02-13T23:00:00Z",
            "end_date": "2026-03-01T23:00:00Z",
            "zones": "Zone B",
            "emoji": "❄️",
        },
    ]
    holidays_2627 = [
        {
            "description": "Vacances de Noël",
            "start_date": "2026-12-18T23:00:00Z",
            "end_date": "2027-01-03T23:00:00Z",
            "zones": "Zone B",
            "emoji": "🎄",
        },
        {
            "description": "Vacances de Printemps",
            "start_date": "2027-04-16T22:00:00Z",
            "end_date": "2027-05-02T22:00:00Z",
            "zones": "Zone B",
            "emoji": "🌸",
        },
    ]
    fake_holidays_data1 = {
        "total_counts": len(fake_holidays_data_2526),
        "results": fake_holidays_data_2526,
    }
    fake_holidays_data2 = {
        "total_counts": len(fake_holidays_data_2526 + fake_holidays_data_2627),
        "results": fake_holidays_data_2526 + fake_holidays_data_2627,
    }

    # get holidays of current school year only
    httpx_mock.add_response(
        url=httpx.URL(
            "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
            params={
                "where": (
                    "end_date >= date'2025-09-01' AND start_date < date'2026-09-15' AND "
                    "(zones = 'Zone A' AND location = 'Bordeaux' OR zones = 'Zone B' "
                    "AND location = 'Lille' OR zones = 'Zone C' AND location = 'Versailles') "
                    "AND population IN ('-', 'Élèves')"
                ),
                "order_by": "start_date",
                "limit": 100,
            },
        ),
        json=fake_holidays_data1,
    )
    response = test_client.get("/data/holidays", params={"start_date": "2025-09-01"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == holidays_2526

    httpx_mock.add_response(
        url=httpx.URL(
            "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
            params={
                "where": (
                    "end_date >= date'2025-12-31' AND start_date < date'2026-09-15' AND "
                    "(zones = 'Zone A' AND location = 'Bordeaux' OR zones = 'Zone B' "
                    "AND location = 'Lille' OR zones = 'Zone C' AND location = 'Versailles') "
                    "AND population IN ('-', 'Élèves')"
                ),
                "order_by": "start_date",
                "limit": 100,
            },
        ),
        json=fake_holidays_data1,
    )
    response = test_client.get("/data/holidays", params={"start_date": "2025-12-31"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == holidays_2526

    # get holidays of current and next school years
    httpx_mock.add_response(
        url=httpx.URL(
            "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
            params={
                "where": (
                    "end_date >= date'2026-01-01' AND start_date < date'2027-09-15' AND "
                    "(zones = 'Zone A' AND location = 'Bordeaux' OR zones = 'Zone B' "
                    "AND location = 'Lille' OR zones = 'Zone C' AND location = 'Versailles') "
                    "AND population IN ('-', 'Élèves')"
                ),
                "order_by": "start_date",
                "limit": 100,
            },
        ),
        json=fake_holidays_data2,
    )
    response = test_client.get("/data/holidays", params={"start_date": "2026-01-01"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == holidays_2526 + holidays_2627

    httpx_mock.add_response(
        url=httpx.URL(
            "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
            params={
                "where": (
                    "end_date >= date'2026-08-31' AND start_date < date'2027-09-15' AND "
                    "(zones = 'Zone A' AND location = 'Bordeaux' OR zones = 'Zone B' "
                    "AND location = 'Lille' OR zones = 'Zone C' AND location = 'Versailles') "
                    "AND population IN ('-', 'Élèves')"
                ),
                "order_by": "start_date",
                "limit": 100,
            },
        ),
        json=fake_holidays_data2,
    )
    response = test_client.get("/data/holidays", params={"start_date": "2026-08-31"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == holidays_2526 + holidays_2627


async def test_get_holidays_emoji(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
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
            url=httpx.URL(
                "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
                params={
                    "where": (
                        "end_date >= date'2025-11-13' AND start_date < date'2026-09-15' AND "
                        "(zones = 'Zone A' AND location = 'Bordeaux' OR zones = 'Zone B' "
                        "AND location = 'Lille' OR zones = 'Zone C' AND location = 'Versailles') "
                        "AND population IN ('-', 'Élèves')"
                    ),
                    "order_by": "start_date",
                    "limit": 100,
                },
            ),
            json=fake_holidays_data,
        )

    mock_data("Vacances de la Toussaint")
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "🍁"

    mock_data("Vacances de Noël")
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "🎄"

    mock_data("Vacances d'Hiver")
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "❄️"

    mock_data("Vacances de Printemps")
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "🌸"

    mock_data("Pont de l'Ascension")
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == ""

    mock_data("Vacances d'Été")
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == "☀️"

    mock_data("Unknown")
    response = test_client.get("/data/holidays", params={"start_date": "2025-11-13"})
    assert response.status_code == HTTP_200_OK
    assert response.json()[0]["emoji"] == ""
