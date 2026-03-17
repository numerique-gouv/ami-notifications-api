import datetime
from unittest import mock

import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.schemas import (
    FollowUpInventory,
    FollowUpInventoryItem,
    FollowUpInventoryItemKind,
    FollowUpInventoryStatus,
)
from app.models import User
from app.schemas import ItemGenericStatus
from tests.ami.utils import assert_query_fails_without_auth, login

pytestmark = pytest.mark.skip("skip tests for Django migration")


async def test_get_follow_up_inventories(
    user: User,
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login(user, test_client)

    psl_inventory = FollowUpInventory(
        status=FollowUpInventoryStatus.SUCCESS,
        items=[
            FollowUpInventoryItem(
                external_id="OperationTranquilliteVacances:44",
                kind=FollowUpInventoryItemKind.OTV,
                status_id=ItemGenericStatus.CLOSED,
                status_label="Validé",
                milestone_start_date=datetime.datetime(
                    2026, 2, 26, 17, 24, tzinfo=datetime.timezone.utc
                ),
                milestone_end_date=datetime.datetime(
                    2026, 3, 26, 17, 24, tzinfo=datetime.timezone.utc
                ),
                title="Notification title 6",
                description="notification 6",
                external_url="http://bar.com",
                created_at=datetime.datetime(2026, 2, 23, 17, 24, tzinfo=datetime.timezone.utc),
                updated_at=datetime.datetime(2026, 2, 24, 17, 24, tzinfo=datetime.timezone.utc),
            ),
            FollowUpInventoryItem(
                external_id="OperationTranquilliteVacances:43",
                kind=FollowUpInventoryItemKind.OTV,
                status_id=ItemGenericStatus.NEW,
                status_label="Nouveau",
                milestone_start_date=None,
                milestone_end_date=None,
                title="Notification title 4",
                description="notification 4",
                external_url="http://foo.com",
                created_at=datetime.datetime(2026, 1, 26, 17, 24, tzinfo=datetime.timezone.utc),
                updated_at=datetime.datetime(2026, 1, 27, 17, 24, tzinfo=datetime.timezone.utc),
            ),
        ],
    )
    psl_data_mock = mock.AsyncMock(return_value=psl_inventory)
    monkeypatch.setattr("app.data.routes.get_psl_inventory", psl_data_mock)

    response = test_client.get("/data/follow-up/inventories")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "psl": {
            "status": "success",
            "items": [
                {
                    "external_id": "OperationTranquilliteVacances:44",
                    "kind": "otv",
                    "status_id": "closed",
                    "status_label": "Validé",
                    "milestone_start_date": "2026-02-26T17:24:00Z",
                    "milestone_end_date": "2026-03-26T17:24:00Z",
                    "title": "Notification title 6",
                    "description": "notification 6",
                    "external_url": "http://bar.com",
                    "created_at": "2026-02-23T17:24:00Z",
                    "updated_at": "2026-02-24T17:24:00Z",
                },
                {
                    "external_id": "OperationTranquilliteVacances:43",
                    "kind": "otv",
                    "status_id": "new",
                    "status_label": "Nouveau",
                    "milestone_start_date": None,
                    "milestone_end_date": None,
                    "title": "Notification title 4",
                    "description": "notification 4",
                    "external_url": "http://foo.com",
                    "created_at": "2026-01-26T17:24:00Z",
                    "updated_at": "2026-01-27T17:24:00Z",
                },
            ],
        }
    }


async def test_get_follow_up_inventories_without_auth(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
) -> None:
    await assert_query_fails_without_auth("/data/follow-up/inventories", test_client, db_session)
