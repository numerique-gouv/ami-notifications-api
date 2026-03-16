import datetime
from unittest import mock

import pytest
from pytest_httpx import HTTPXMock

from ami.agenda.data.holidays import (
    SchoolHolidaysError,
    get_school_holidays_catalog,
    get_school_holidays_data,
)
from ami.agenda.data.schemas import SchoolHoliday
from ami.agenda.schemas import (
    AgendaCatalog,
    AgendaCatalogItem,
    AgendaCatalogItemKind,
    AgendaCatalogStatus,
)
from ami.utils.httpx import URL, AsyncClient


async def test_get_school_holidays_data(
    httpx_mock: HTTPXMock,
) -> None:
    fake_holidays_data = [
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2025-12-20T00:00:00+01:00",
            "end_date": "2026-01-05T00:00:00+01:00",
            "location": "Bordeaux",
            "zones": "Zone A",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2025-12-20T00:00:00+01:00",
            "end_date": "2026-01-05T00:00:00+01:00",
            "location": "Bordeaux",
            "zones": "Zone B",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2025-12-20T00:00:00+01:00",
            "end_date": "2026-01-05T00:00:00+01:00",
            "location": "Versailles",
            "zones": "Zone C",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances d'Hiver",
            "population": "-",
            "start_date": "2026-02-07T00:00:00+01:00",
            "end_date": "2026-02-23T00:00:00+01:00",
            "location": "Bordeaux",
            "zones": "Zone A",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances d'Hiver",
            "population": "-",
            "start_date": "2026-02-14T00:00:00+01:00",
            "end_date": "2026-03-02T00:00:00+01:00",
            "location": "Lille",
            "zones": "Zone B",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances d'Hiver",
            "population": "-",
            "start_date": "2026-02-21T00:00:00+01:00",
            "end_date": "2026-03-09T00:00:00+01:00",
            "location": "Versailles",
            "zones": "Zone C",
            "annee_scolaire": "2025-2026",
        },
    ]
    fake_holidays_data = {"total_counts": len(fake_holidays_data), "results": fake_holidays_data}

    httpx_mock.add_response(
        url=URL(
            "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
            params={
                "where": (
                    "end_date >= date'2025-11-12' AND start_date < date'2026-09-15' AND "
                    "(location = 'Bordeaux' OR location = 'Lille' OR location = 'Versailles') "
                    "AND population IN ('-', 'Élèves')"
                ),
                "order_by": "start_date",
                "limit": 100,
                "timezone": "Europe/Paris",
            },
        ),
        json=fake_holidays_data,
    )

    # christmas holidays are deduplicated: the dates are the same for all zones
    holidays = [
        SchoolHoliday(
            description="Vacances de Noël",
            start_date=datetime.date(2025, 12, 20),
            end_date=datetime.date(2026, 1, 5),
            zones="",
            emoji="🎄",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 7),
            end_date=datetime.date(2026, 2, 23),
            zones="Zone A",
            emoji="❄️",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 14),
            end_date=datetime.date(2026, 3, 2),
            zones="Zone B",
            emoji="❄️",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 21),
            end_date=datetime.date(2026, 3, 9),
            zones="Zone C",
            emoji="❄️",
        ),
    ]
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result == holidays


async def test_get_school_holidays_data_emoji(
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
            json=fake_holidays_data,
        )

    mock_data("Vacances de la Toussaint")
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result[0].emoji == "🍁"

    mock_data("Vacances de Noël")
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result[0].emoji == "🎄"

    mock_data("Vacances d'Hiver")
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result[0].emoji == "❄️"

    mock_data("Vacances de Printemps")
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result[0].emoji == "🌸"

    mock_data("Pont de l'Ascension")
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result[0].emoji == ""

    mock_data("Vacances d'Été")
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result[0].emoji == "☀️"

    mock_data("Unknown")
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_data(
            datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
        )
    assert result[0].emoji == ""


async def test_get_school_holidays_data_error(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(status_code=500)
    with pytest.raises(SchoolHolidaysError) as e:
        async with AsyncClient() as httpx_async_client:
            await get_school_holidays_data(
                datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
            )
    assert e.value.status_code == 500


async def test_get_school_holidays_catalog(
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    holidays = [
        SchoolHoliday(
            description="Vacances de Noël",
            start_date=datetime.date(2025, 12, 20),
            end_date=datetime.date(2026, 1, 5),
            zones="",
            emoji="🎄",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 7),
            end_date=datetime.date(2026, 2, 23),
            zones="Zone A",
            emoji="❄️",
        ),
    ]
    data_mock = mock.AsyncMock(return_value=holidays)
    monkeypatch.setattr("ami.agenda.data.holidays.get_school_holidays_data", data_mock)
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_catalog(
            start_date=datetime.date(2025, 11, 12),
            end_date=datetime.date(2026, 9, 15),
            httpx_async_client=httpx_async_client,
        )
    items = [
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title="Vacances de Noël",
            start_date=datetime.date(2025, 12, 20),
            end_date=datetime.date(2026, 1, 5),
            zones="",
            emoji="🎄",
        ),
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 7),
            end_date=datetime.date(2026, 2, 23),
            zones="Zone A",
            emoji="❄️",
        ),
    ]
    assert result == AgendaCatalog(status=AgendaCatalogStatus.SUCCESS, items=items)


async def test_get_school_holidays_catalog_error(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(status_code=500)
    async with AsyncClient() as httpx_async_client:
        result = await get_school_holidays_catalog(
            start_date=datetime.date(2025, 11, 12),
            end_date=datetime.date(2026, 9, 15),
            httpx_async_client=httpx_async_client,
        )
    assert result == AgendaCatalog(status=AgendaCatalogStatus.FAILED)
