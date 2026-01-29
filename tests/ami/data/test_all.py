import datetime
from unittest import mock

import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.testing import TestClient

from app.data.holidays import SchoolHolidaysError
from app.models import User
from app.schemas import PublicHoliday, SchoolHoliday
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_get_school_holidays(
    user: User,
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login(user, test_client)

    today = datetime.date.today()
    dates_mock = mock.Mock(return_value=(today, today + datetime.timedelta(days=2)))
    monkeypatch.setattr("app.data.routes.get_holidays_dates", dates_mock)
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
    monkeypatch.setattr("app.data.routes.get_school_holidays_data", data_mock)

    result = [
        {
            "description": "Vacances de Noël",
            "start_date": "2025-12-20",
            "end_date": "2026-01-05",
            "zones": "",
            "emoji": "🎄",
        },
        {
            "description": "Vacances d'Hiver",
            "start_date": "2026-02-07",
            "end_date": "2026-02-23",
            "zones": "Zone A",
            "emoji": "❄️",
        },
    ]
    response = test_client.get("/data/school-holidays", params={"current_date": "2025-12-12"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == result

    assert dates_mock.call_args_list == [mock.call(datetime.date(2025, 12, 12))]
    assert data_mock.call_args_list == [
        mock.call(today, today + datetime.timedelta(days=2), mock.ANY)
    ]


async def test_get_school_holidays_error(
    user: User,
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login(user, test_client)

    today = datetime.date.today()
    dates_mock = mock.Mock(return_value=(today, today + datetime.timedelta(days=2)))
    monkeypatch.setattr("app.data.routes.get_holidays_dates", dates_mock)
    data_mock = mock.AsyncMock(
        side_effect=SchoolHolidaysError(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    )
    monkeypatch.setattr("app.data.routes.get_school_holidays_data", data_mock)
    response = test_client.get("/data/school-holidays", params={"current_date": "2025-09-01"})
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"ami_details": "School holidays error"}


async def test_get_school_holidays_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/data/school-holidays", test_client)


async def test_get_public_holidays(
    user: User,
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login(user, test_client)

    today = datetime.date.today()
    dates_mock = mock.Mock(return_value=(today, today + datetime.timedelta(days=2)))
    monkeypatch.setattr("app.data.routes.get_holidays_dates", dates_mock)
    holidays = [
        PublicHoliday(description="Noël", date=datetime.date(2025, 12, 25), emoji="📅"),
        PublicHoliday(description="Jour de l’An", date=datetime.date(2026, 1, 1), emoji="🎉"),
    ]
    data_mock = mock.Mock(return_value=holidays)
    monkeypatch.setattr("app.data.routes.get_public_holidays_data", data_mock)

    result = [
        {"description": "Noël", "date": "2025-12-25", "emoji": "📅"},
        {"description": "Jour de l’An", "date": "2026-01-01", "emoji": "🎉"},
    ]
    response = test_client.get("/data/public-holidays", params={"current_date": "2025-12-12"})
    assert response.status_code == HTTP_200_OK
    assert response.json() == result

    assert dates_mock.call_args_list == [mock.call(datetime.date(2025, 12, 12))]
    assert data_mock.call_args_list == [mock.call(today, today + datetime.timedelta(days=2))]


async def test_get_public_holidays_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/data/public-holidays", test_client)
