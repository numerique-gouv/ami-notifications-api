import datetime
from unittest import mock

import pytest

from ami.agenda.data.holidays import get_public_holidays_catalog, get_public_holidays_data
from ami.agenda.data.schemas import PublicHoliday
from ami.agenda.schemas import (
    AgendaCatalog,
    AgendaCatalogItem,
    AgendaCatalogItemKind,
    AgendaCatalogStatus,
)


def test_get_public_holidays_data() -> None:
    result = get_public_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result == [
        PublicHoliday(description="Noël", date=datetime.date(2025, 12, 25), emoji="📅"),
        PublicHoliday(description="Jour de l’An", date=datetime.date(2026, 1, 1), emoji="🎉"),
        PublicHoliday(description="Lundi de Pâques", date=datetime.date(2026, 4, 6), emoji="📅"),
        PublicHoliday(description="Fête du Travail", date=datetime.date(2026, 5, 1), emoji="📅"),
        PublicHoliday(description="Victoire 1945", date=datetime.date(2026, 5, 8), emoji="📅"),
        PublicHoliday(description="Ascension", date=datetime.date(2026, 5, 14), emoji="📅"),
        PublicHoliday(
            description="Lundi de Pentecôte", date=datetime.date(2026, 5, 25), emoji="📅"
        ),
        PublicHoliday(description="Fête Nationale", date=datetime.date(2026, 7, 14), emoji="🎆"),
        PublicHoliday(description="Assomption", date=datetime.date(2026, 8, 15), emoji="📅"),
    ]


def test_get_public_holidays_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    holidays = [
        PublicHoliday(description="Noël", date=datetime.date(2025, 12, 25), emoji="📅"),
        PublicHoliday(description="Jour de l’An", date=datetime.date(2026, 1, 1), emoji="🎉"),
    ]
    data_mock = mock.Mock(return_value=holidays)
    monkeypatch.setattr("ami.agenda.data.holidays.get_public_holidays_data", data_mock)
    result = get_public_holidays_catalog(
        start_date=datetime.date(2025, 11, 12), end_date=datetime.date(2026, 9, 15)
    )
    items = [
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title="Noël",
            date=datetime.date(2025, 12, 25),
            emoji="📅",
        ),
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title="Jour de l’An",
            date=datetime.date(2026, 1, 1),
            emoji="🎉",
        ),
    ]
    assert result == AgendaCatalog(status=AgendaCatalogStatus.SUCCESS, items=items)
