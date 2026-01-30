import datetime
from unittest import mock

import pytest
from pytest_httpx import HTTPXMock

from app.data.internal import get_elections_catalog, get_elections_data
from app.schemas import (
    AgendaCatalog,
    AgendaCatalogItem,
    AgendaCatalogItemKind,
    AgendaCatalogStatus,
    Election,
)


async def test_get_elections_data(
    httpx_mock: HTTPXMock,
) -> None:
    result = get_elections_data(datetime.date(2025, 3, 15), datetime.date(2026, 3, 22))
    assert result == [
        Election(
            title="Élection municipales - Premier tour de scrutin",
            description="Votez au premier tour des municipales",
            date=datetime.date(2026, 3, 15),
            emoji="🗳️",
        ),
        Election(
            title="Élection municipales - Second tour de scrutin",
            description="Votez au second tour des municipales",
            date=datetime.date(2026, 3, 22),
            emoji="🗳️",
        ),
    ]
    result = get_elections_data(datetime.date(2026, 3, 16), datetime.date(2026, 3, 22))
    assert result == [
        Election(
            title="Élection municipales - Second tour de scrutin",
            description="Votez au second tour des municipales",
            date=datetime.date(2026, 3, 22),
            emoji="🗳️",
        )
    ]
    result = get_elections_data(datetime.date(2026, 3, 15), datetime.date(2026, 3, 21))
    assert result == [
        Election(
            title="Élection municipales - Premier tour de scrutin",
            description="Votez au premier tour des municipales",
            date=datetime.date(2026, 3, 15),
            emoji="🗳️",
        ),
    ]


async def test_get_elections_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    holidays = [
        Election(
            title="Foo",
            description="Votez au premier tour des municipales",
            date=datetime.date(2026, 3, 15),
            emoji="🗳️",
        ),
        Election(
            title="Foo",
            description="Votez au second tour des municipales",
            date=datetime.date(2026, 3, 22),
            emoji="🗳️",
        ),
    ]
    data_mock = mock.Mock(return_value=holidays)
    monkeypatch.setattr("app.data.internal.get_elections_data", data_mock)
    result = await get_elections_catalog(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    items = [
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.ELECTION,
            title="Foo",
            description="Votez au premier tour des municipales",
            date=datetime.date(2026, 3, 15),
            emoji="🗳️",
        ),
        AgendaCatalogItem(
            kind=AgendaCatalogItemKind.ELECTION,
            title="Foo",
            description="Votez au second tour des municipales",
            date=datetime.date(2026, 3, 22),
            emoji="🗳️",
        ),
    ]
    assert result == AgendaCatalog(status=AgendaCatalogStatus.SUCCESS, items=items)
