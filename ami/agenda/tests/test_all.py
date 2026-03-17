import datetime
from unittest import mock

import pytest
from rest_framework.status import HTTP_200_OK

from ami.agenda.schemas import (
    AgendaCatalog,
    AgendaCatalogItem,
    AgendaCatalogItemKind,
    AgendaCatalogStatus,
)
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_agenda_items(
    django_app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login(django_app, user)

    today = datetime.date.today()
    dates_mock = mock.Mock(return_value=(today, today + datetime.timedelta(days=2)))
    monkeypatch.setattr("ami.agenda.data.holidays.get_holidays_dates", dates_mock)
    school_catalog = AgendaCatalog(
        status=AgendaCatalogStatus.SUCCESS,
        items=[
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
        ],
    )
    school_data_mock = mock.AsyncMock(return_value=school_catalog)
    monkeypatch.setattr("ami.agenda.data.holidays.get_school_holidays_catalog", school_data_mock)
    public_catalog = AgendaCatalog(
        status=AgendaCatalogStatus.SUCCESS,
        items=[
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
        ],
    )
    public_data_mock = mock.AsyncMock(return_value=public_catalog)
    monkeypatch.setattr("ami.agenda.data.holidays.get_public_holidays_catalog", public_data_mock)
    election_catalog = AgendaCatalog(
        status=AgendaCatalogStatus.SUCCESS,
        items=[
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
        ],
    )
    election_data_mock = mock.AsyncMock(return_value=election_catalog)
    monkeypatch.setattr("ami.agenda.data.internal.get_elections_catalog", election_data_mock)

    duration_mock = mock.Mock(
        return_value=datetime.datetime(2026, 2, 14, 11, 16, tzinfo=datetime.timezone.utc)
    )
    monkeypatch.setattr("ami.utils.schemas.DurationExpiration.compute_expires_at", duration_mock)
    monthly_mock = mock.Mock(
        return_value=datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
    )
    monkeypatch.setattr("ami.utils.schemas.MonthlyExpiration.compute_expires_at", monthly_mock)

    response = django_app.get("/data/agenda/items", params={"current_date": "2025-12-12"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "school_holidays": {
            "status": "success",
            "items": [
                {
                    "kind": "holiday",
                    "title": "Vacances de Noël",
                    "description": "",
                    "date": None,
                    "start_date": "2025-12-20",
                    "end_date": "2026-01-05",
                    "zones": "",
                    "emoji": "🎄",
                },
                {
                    "kind": "holiday",
                    "title": "Vacances d'Hiver",
                    "description": "",
                    "date": None,
                    "start_date": "2026-02-07",
                    "end_date": "2026-02-23",
                    "zones": "Zone A",
                    "emoji": "❄️",
                },
            ],
            "expires_at": "2026-03-01T00:00:00Z",
        },
        "public_holidays": {
            "status": "success",
            "items": [
                {
                    "kind": "holiday",
                    "title": "Noël",
                    "description": "",
                    "date": "2025-12-25",
                    "start_date": None,
                    "end_date": None,
                    "zones": "",
                    "emoji": "📅",
                },
                {
                    "kind": "holiday",
                    "title": "Jour de l’An",
                    "description": "",
                    "date": "2026-01-01",
                    "start_date": None,
                    "end_date": None,
                    "zones": "",
                    "emoji": "🎉",
                },
            ],
            "expires_at": "2026-03-01T00:00:00Z",
        },
        "elections": {
            "status": "success",
            "items": [
                {
                    "kind": "election",
                    "title": "Foo",
                    "description": "Votez au premier tour des municipales",
                    "date": "2026-03-15",
                    "start_date": None,
                    "end_date": None,
                    "zones": "",
                    "emoji": "🗳️",
                },
                {
                    "kind": "election",
                    "title": "Foo",
                    "description": "Votez au second tour des municipales",
                    "date": "2026-03-22",
                    "start_date": None,
                    "end_date": None,
                    "zones": "",
                    "emoji": "🗳️",
                },
            ],
            "expires_at": "2026-02-14T11:16:00Z",
        },
    }

    assert dates_mock.call_args_list == [mock.call(datetime.date(2025, 12, 12))]
    assert school_data_mock.call_args_list == [
        mock.call(
            start_date=today,
            end_date=today + datetime.timedelta(days=2),
            httpx_async_client=mock.ANY,
        )
    ]
    assert public_data_mock.call_args_list == [
        mock.call(
            start_date=today,
            end_date=today + datetime.timedelta(days=2),
            httpx_async_client=mock.ANY,
        )
    ]
    assert election_data_mock.call_args_list == [
        mock.call(
            start_date=today,
            end_date=today + datetime.timedelta(days=2),
            httpx_async_client=mock.ANY,
        )
    ]

    school_data_mock.reset_mock()
    public_data_mock.reset_mock()
    election_data_mock.reset_mock()
    response = django_app.get(
        "/data/agenda/items", params={"current_date": "2025-12-12", "filter-items": []}
    )
    assert response.json()["school_holidays"] is not None
    assert response.json()["public_holidays"] is not None
    assert response.json()["elections"] is not None
    assert len(school_data_mock.call_args_list) == 1
    assert len(public_data_mock.call_args_list) == 1
    assert len(election_data_mock.call_args_list) == 1

    school_data_mock.reset_mock()
    public_data_mock.reset_mock()
    election_data_mock.reset_mock()
    response = django_app.get(
        "/data/agenda/items", params={"current_date": "2025-12-12", "filter-items": ["unknown"]}
    )
    assert response.json()["school_holidays"] is not None
    assert response.json()["public_holidays"] is not None
    assert response.json()["elections"] is not None
    assert len(school_data_mock.call_args_list) == 1
    assert len(public_data_mock.call_args_list) == 1
    assert len(election_data_mock.call_args_list) == 1

    school_data_mock.reset_mock()
    public_data_mock.reset_mock()
    election_data_mock.reset_mock()
    response = django_app.get(
        "/data/agenda/items",
        params={
            "current_date": "2025-12-12",
            "filter-items": ["school_holidays", "public_holidays", "elections", "unknown"],
        },
    )
    assert response.json()["school_holidays"] is not None
    assert response.json()["public_holidays"] is not None
    assert response.json()["elections"] is not None
    assert len(school_data_mock.call_args_list) == 1
    assert len(public_data_mock.call_args_list) == 1
    assert len(election_data_mock.call_args_list) == 1

    school_data_mock.reset_mock()
    public_data_mock.reset_mock()
    election_data_mock.reset_mock()
    response = django_app.get(
        "/data/agenda/items", params={"current_date": "2025-12-12", "filter-items": ["elections"]}
    )
    assert response.json()["school_holidays"] is None
    assert response.json()["public_holidays"] is None
    assert response.json()["elections"] is not None
    assert len(school_data_mock.call_args_list) == 0
    assert len(public_data_mock.call_args_list) == 0
    assert len(election_data_mock.call_args_list) == 1

    school_data_mock.reset_mock()
    public_data_mock.reset_mock()
    election_data_mock.reset_mock()
    response = django_app.get(
        "/data/agenda/items",
        params={"current_date": "2025-12-12", "filter-items": ["elections", "public_holidays"]},
    )
    assert response.json()["school_holidays"] is None
    assert response.json()["public_holidays"] is not None
    assert response.json()["elections"] is not None
    assert len(school_data_mock.call_args_list) == 0
    assert len(public_data_mock.call_args_list) == 1
    assert len(election_data_mock.call_args_list) == 1


@pytest.mark.django_db
def test_get_agenda_items_without_auth(
    django_app,
) -> None:
    assert_query_fails_without_auth(django_app, "/data/agenda/items")
