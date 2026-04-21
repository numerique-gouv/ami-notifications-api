import pytest
from django.conf import settings
from django.utils.timezone import now
from pytest_httpx import HTTPXMock

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_notifications_auth


@pytest.mark.django_db
def test_send_notification(app, notifications_agent: Agent) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/notification/")
    assert "Envoyer une notification" in response

    assert response.forms["send-notification"]["recipient_fc_hash"].value == ""
    assert response.forms["send-notification"]["content_title"].value == ""
    assert response.forms["send-notification"]["content_body"].value == ""
    assert response.forms["send-notification"]["content_icon"].value == ""
    assert response.forms["send-notification"]["item_type"].value == ""
    assert response.forms["send-notification"]["item_id"].value == ""
    assert response.forms["send-notification"]["item_status_label"].value == ""
    assert response.forms["send-notification"]["item_generic_status"].value == "new"
    assert response.forms["send-notification"]["item_canal"].value == "admin"
    assert response.forms["send-notification"]["item_milestone_start_date"].value == ""
    assert response.forms["send-notification"]["item_milestone_end_date"].value == ""
    assert response.forms["send-notification"]["item_external_url"].value == ""
    assert response.forms["send-notification"]["send_date"].value == now().strftime(
        "%Y-%m-%dT%H:%M:00.000"
    )
    assert response.forms["send-notification"]["try_push"].value is None


@pytest.mark.django_db
def test_send_notification_submit_validation_errors(app, notifications_agent: Agent) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/notification/")
    response = response.forms["send-notification"].submit()
    assert response.context["form"].errors == {
        "recipient_fc_hash": ["Ce champ est obligatoire."],
        "content_title": ["Ce champ est obligatoire."],
        "content_body": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_send_notification_submit_with_400(
    app,
    notifications_agent: Agent,
    httpx_mock: HTTPXMock,
) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/notification/")

    response.forms["send-notification"]["recipient_fc_hash"] = "a-recipient"
    response.forms["send-notification"]["content_title"] = "a-title"
    response.forms["send-notification"]["content_body"] = "a-body"
    response.forms["send-notification"]["item_generic_status"] = ""
    response.forms["send-notification"]["item_canal"] = ""
    response.forms["send-notification"]["send_date"] = "2026-04-21T16:24:00.000"

    httpx_mock.add_response(
        url=f"{settings.PUBLIC_API_URL}/api/v1/notifications",
        json={
            "recipient_fc_hash": ["error 1", "error 2"],
            "item_type": ["error 3"],
            "unknown_field": ["error 4"],
        },
        match_json={
            "recipient_fc_hash": "a-recipient",
            "content_title": "a-title",
            "content_body": "a-body",
            "send_date": "2026-04-21T16:24:00Z",
            "try_push": False,
        },
        status_code=400,
    )

    response = response.forms["send-notification"].submit()
    assert response.context["form"].errors == {
        "__all__": ["error 4"],
        "recipient_fc_hash": ["error 1", "error 2"],
        "item_type": ["error 3"],
    }


@pytest.mark.django_db
def test_send_notification_submit_with_404(
    app,
    notifications_agent: Agent,
    httpx_mock: HTTPXMock,
) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/notification/")

    response.forms["send-notification"]["recipient_fc_hash"] = "a-recipient"
    response.forms["send-notification"]["content_title"] = "a-title"
    response.forms["send-notification"]["content_body"] = "a-body"

    httpx_mock.add_response(
        url=f"{settings.PUBLIC_API_URL}/api/v1/notifications",
        status_code=404,
    )

    response = response.forms["send-notification"].submit()
    assert response.context["form"].errors == {"__all__": ["Not found error"]}


@pytest.mark.django_db
def test_send_notification_submit_with_404_and_message(
    app,
    notifications_agent: Agent,
    httpx_mock: HTTPXMock,
) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/notification/")

    response.forms["send-notification"]["recipient_fc_hash"] = "a-recipient"
    response.forms["send-notification"]["content_title"] = "a-title"
    response.forms["send-notification"]["content_body"] = "a-body"

    httpx_mock.add_response(
        url=f"{settings.PUBLIC_API_URL}/api/v1/notifications",
        json={"error": "User not found"},
        status_code=404,
    )

    response = response.forms["send-notification"].submit()
    assert response.context["form"].errors == {"__all__": ["User not found"]}

    httpx_mock.add_response(
        url=f"{settings.PUBLIC_API_URL}/api/v1/notifications",
        json={"unknown_field": "User not found"},
        status_code=404,
    )

    response = response.forms["send-notification"].submit()
    assert response.context["form"].errors == {"__all__": ["Not found error"]}


@pytest.mark.django_db
def test_send_notification_submit_success(
    app,
    notifications_agent: Agent,
    httpx_mock: HTTPXMock,
) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/notification/")

    response.forms["send-notification"]["recipient_fc_hash"] = "a-recipient"
    response.forms["send-notification"]["content_title"] = "a-title"
    response.forms["send-notification"]["content_body"] = "a-body"

    httpx_mock.add_response(
        url=f"{settings.PUBLIC_API_URL}/api/v1/notifications",
        json={
            "notification_id": "5c108865-3ca3-403b-bd53-942bcc025f2c",
            "notification_send_status": True,
        },
        status_code=200,
    )

    response = response.forms["send-notification"].submit()
    assert (
        response.pyquery(".fr-alert--success").text() == "Notification envoyée avec succès\n"
        "notification_id: 5c108865-3ca3-403b-bd53-942bcc025f2c, notification_send_status: True\n"
        "Masquer le message"
    )


@pytest.mark.django_db
def test_send_notification_without_agent_notifications_auth(app) -> None:
    assert_query_fails_without_agent_notifications_auth(app, "/agent-admin/notification/")
