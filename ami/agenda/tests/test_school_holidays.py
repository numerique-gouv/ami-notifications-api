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
from ami.utils.httpx import URL


def test_get_school_holidays_data(
    app,
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
            "location": "Limoges",
            "zones": "Zone A",
            "annee_scolaire": "2025-2026",
        },
        {
            "description": "Vacances de Noël",
            "population": "-",
            "start_date": "2025-12-20T00:00:00+01:00",
            "end_date": "2026-01-05T00:00:00+01:00",
            "location": "Lille",
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
        {
            "description": "Pont de l'Ascension",
            "population": "-",
            "start_date": "2027-05-07T00:00:00+02:00",
            "end_date": "2027-05-07T00:00:00+02:00",
            "location": "Bordeaux",
            "zones": "Zone A",
            "annee_scolaire": "2026-2027",
        },
    ]

    httpx_mock.add_response(
        url=URL(
            "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/exports/json",
            params={
                "where": (
                    "end_date >= date'2025-11-12' AND start_date < date'2026-09-15' AND population IN ('-', 'Élèves')"
                ),
                "order_by": "start_date",
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
            end_date=datetime.date(2026, 1, 4),
            zones=["Zone A", "Zone B", "Zone C"],
            emoji="🎄",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 7),
            end_date=datetime.date(2026, 2, 22),
            zones=["Zone A"],
            emoji="❄️",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 14),
            end_date=datetime.date(2026, 3, 1),
            zones=["Zone B"],
            emoji="❄️",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 21),
            end_date=datetime.date(2026, 3, 8),
            zones=["Zone C"],
            emoji="❄️",
        ),
        SchoolHoliday(
            description="Pont de l'Ascension",
            zones=["Zone A"],
            start_date=datetime.date(2027, 5, 7),
            end_date=datetime.date(2027, 5, 7),
            emoji="",
        ),
    ]
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result == holidays


def test_get_school_holidays_data_emoji(
    nocache,
    app,
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

        httpx_mock.add_response(
            json=fake_holidays_data,
        )

    mock_data("Vacances de la Toussaint")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🍁"

    mock_data("Vacances de Noël")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🎄"

    mock_data("Vacances d'Hiver")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "❄️"

    mock_data("Vacances de Printemps")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🌸"

    mock_data("Vacances d'Été")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "☀️"

    mock_data("Vacances de Carnaval")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🎭"

    mock_data("Vacances de Pâques")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🐣"

    mock_data("Vacances d'Été austral")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🏝️"

    mock_data("Vacances d'Hiver austral")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🏖️"

    mock_data("Début des Vacances d'Hiver austral")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "🏖️"

    mock_data("Début des Vacances d'Été")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == "☀️"

    mock_data("Unknown")
    result = get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result[0].emoji == ""


def test_get_school_holidays_data_error(
    app,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(status_code=500)
    with pytest.raises(SchoolHolidaysError) as e:
        get_school_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert e.value.status_code == 500


def test_get_school_holidays_catalog(
    app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    holidays = [
        SchoolHoliday(
            description="Vacances de Noël",
            start_date=datetime.date(2025, 12, 20),
            end_date=datetime.date(2026, 1, 5),
            zones=[],
            emoji="🎄",
        ),
        SchoolHoliday(
            description="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 7),
            end_date=datetime.date(2026, 2, 23),
            zones=["Zone A"],
            emoji="❄️",
        ),
    ]
    data_mock = mock.Mock(return_value=holidays)
    monkeypatch.setattr("ami.agenda.data.holidays.get_school_holidays_data", data_mock)
    result = get_school_holidays_catalog(
        start_date=datetime.date(2025, 11, 12), end_date=datetime.date(2026, 9, 15)
    )
    items = [
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title="Vacances de Noël",
            start_date=datetime.date(2025, 12, 20),
            end_date=datetime.date(2026, 1, 5),
            zones=[],
            emoji="🎄",
        ),
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title="Vacances d'Hiver",
            start_date=datetime.date(2026, 2, 7),
            end_date=datetime.date(2026, 2, 23),
            zones=["Zone A"],
            emoji="❄️",
        ),
    ]
    assert result == AgendaCatalog(status=AgendaCatalogStatus.SUCCESS, items=items)


def test_get_school_holidays_catalog_error(
    app,
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(status_code=500)
    result = get_school_holidays_catalog(
        start_date=datetime.date(2025, 11, 12), end_date=datetime.date(2026, 9, 15)
    )
    assert result == AgendaCatalog(status=AgendaCatalogStatus.FAILED)
