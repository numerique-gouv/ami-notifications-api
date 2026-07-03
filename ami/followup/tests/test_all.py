import datetime
from unittest import mock

import pytest

from ami.followup.schemas import (
    FollowupItem,
    FollowupItemEvent,
    FollowupSource,
    FollowupSourceStatus,
    ItemGenericStatus,
)
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_followup(
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    app,
) -> None:
    login(app, user)

    psl_source = FollowupSource(
        status=FollowupSourceStatus.SUCCESS,
        items=[
            FollowupItem(
                partner_id="psl",
                item_type="OperationTranquilliteVacances",
                item_external_id="44",
                status_id=ItemGenericStatus.CLOSED,
                status_label="Validé",
                milestone_start_date=datetime.datetime(
                    2026, 2, 26, 17, 24, tzinfo=datetime.timezone.utc
                ),
                milestone_end_date=datetime.datetime(
                    2026, 3, 26, 17, 24, tzinfo=datetime.timezone.utc
                ),
                events=[
                    FollowupItemEvent(
                        id="fake-followup-id",
                        created_at=datetime.datetime(
                            2026, 2, 23, 17, 24, tzinfo=datetime.timezone.utc
                        ),
                        description="Evénement lié à l'item",
                    ),
                ],
                title="Notification title 6",
                description="notification 6",
                icon="icon 6",
                external_url="http://bar.com",
                is_archived=False,
                created_at=datetime.datetime(2026, 2, 23, 17, 24, tzinfo=datetime.timezone.utc),
                updated_at=datetime.datetime(2026, 2, 24, 17, 24, tzinfo=datetime.timezone.utc),
            ),
            FollowupItem(
                partner_id="psl",
                item_type="OperationTranquilliteVacances",
                item_external_id="43",
                status_id=ItemGenericStatus.NEW,
                status_label="Nouveau",
                milestone_start_date=None,
                milestone_end_date=None,
                events=[],
                title="Notification title 4",
                description="notification 4",
                icon="icon 4",
                external_url="http://foo.com",
                is_archived=True,
                created_at=datetime.datetime(2026, 1, 26, 17, 24, tzinfo=datetime.timezone.utc),
                updated_at=datetime.datetime(2026, 1, 27, 17, 24, tzinfo=datetime.timezone.utc),
            ),
        ],
    )
    psl_data_mock = mock.Mock(return_value=psl_source)
    monkeypatch.setattr("ami.followup.api_views.get_notifications_source", psl_data_mock)

    response = app.get("/api/v1/users/data/followup", status=200)
    assert response.json == {
        "notifications": {
            "status": "success",
            "items": [
                {
                    "partner_id": "psl",
                    "item_type": "OperationTranquilliteVacances",
                    "item_external_id": "44",
                    "status_id": "closed",
                    "status_label": "Validé",
                    "milestone_start_date": "2026-02-26T17:24:00Z",
                    "milestone_end_date": "2026-03-26T17:24:00Z",
                    "events": [
                        {
                            "description": "Evénement lié à l'item",
                            "created_at": "2026-02-23T17:24:00Z",
                            "id": "fake-followup-id",
                        },
                    ],
                    "title": "Notification title 6",
                    "description": "notification 6",
                    "icon": "icon 6",
                    "external_url": "http://bar.com",
                    "is_archived": False,
                    "created_at": "2026-02-23T17:24:00Z",
                    "updated_at": "2026-02-24T17:24:00Z",
                },
                {
                    "partner_id": "psl",
                    "item_type": "OperationTranquilliteVacances",
                    "item_external_id": "43",
                    "status_id": "new",
                    "status_label": "Nouveau",
                    "milestone_start_date": None,
                    "milestone_end_date": None,
                    "events": [],
                    "title": "Notification title 4",
                    "description": "notification 4",
                    "icon": "icon 4",
                    "external_url": "http://foo.com",
                    "is_archived": True,
                    "created_at": "2026-01-26T17:24:00Z",
                    "updated_at": "2026-01-27T17:24:00Z",
                },
            ],
        }
    }


@pytest.mark.django_db
def test_get_followup_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/data/followup")
