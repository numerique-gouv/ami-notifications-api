import datetime

import httpx
import pytest
from httpx import AsyncClient
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from pytest_httpx import HTTPXMock

from app.data.holidays import SchoolHolidaysError, get_school_holidays_data
from app.schemas import SchoolHoliday


async def test_get_school_holidays_data(
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
        SchoolHoliday(
            description="Vacances de Noël",
            start_date=datetime.datetime(2025, 12, 19, 23, 0, tzinfo=datetime.timezone.utc),
            end_date=datetime.datetime(2026, 1, 4, 23, 0, tzinfo=datetime.timezone.utc),
            zones="",
            emoji="🎄",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.datetime(2026, 2, 6, 23, 0, tzinfo=datetime.timezone.utc),
            end_date=datetime.datetime(2026, 2, 22, 23, 0, tzinfo=datetime.timezone.utc),
            zones="Zone A",
            emoji="❄️",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.datetime(2026, 2, 13, 23, 0, tzinfo=datetime.timezone.utc),
            end_date=datetime.datetime(2026, 3, 1, 23, 0, tzinfo=datetime.timezone.utc),
            zones="Zone B",
            emoji="❄️",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.datetime(2026, 2, 20, 23, 0, tzinfo=datetime.timezone.utc),
            end_date=datetime.datetime(2026, 3, 8, 23, 0, tzinfo=datetime.timezone.utc),
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
    httpx_mock.add_response(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    with pytest.raises(SchoolHolidaysError) as e:
        async with AsyncClient() as httpx_async_client:
            await get_school_holidays_data(
                datetime.date(2025, 11, 12), datetime.date(2026, 9, 15), httpx_async_client
            )
    assert e.value.status_code == HTTP_500_INTERNAL_SERVER_ERROR
