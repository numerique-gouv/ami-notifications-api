from unittest import mock

import pytest
from django.utils.timezone import now

from ami.agent.models import Agent
from ami.agent_admin.forms import simulate_event_call
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_notifications_auth
from ami.partner.models import Partner


@pytest.mark.django_db
def test_send_notification(app, notifications_agent: Agent) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/manage/notification/")
    assert "Envoyer une notification" in response.pyquery("main").text()

    assert response.forms["send-notification"]["recipient_fc_hash"].value == ""
    assert response.forms["send-notification"]["content_title"].value == ""
    assert response.forms["send-notification"]["content_body"].value == ""
    assert response.forms["send-notification"]["content_private_body"].value == ""
    assert response.forms["send-notification"]["content_subheading"].value == ""
    assert response.forms["send-notification"]["content_icon"].value == ""
    assert response.forms["send-notification"]["content_link"].value == ""
    assert response.forms["send-notification"]["item_type"].value == ""
    assert response.forms["send-notification"]["item_id"].value == ""
    assert response.forms["send-notification"]["item_parent_partner_id"].value == ""
    assert response.forms["send-notification"]["item_parent_type"].value == ""
    assert response.forms["send-notification"]["item_parent_id"].value == ""
    assert response.forms["send-notification"]["item_status_label"].value == ""
    assert response.forms["send-notification"]["item_generic_status"].value == ""
    assert response.forms["send-notification"]["item_canal"].value == ""
    assert response.forms["send-notification"]["item_milestone_start_date"].value == ""
    assert response.forms["send-notification"]["item_milestone_end_date"].value == ""
    assert response.forms["send-notification"]["event_date"].value == now().strftime(
        "%Y-%m-%dT%H:%M:00.000"
    )
    assert response.forms["send-notification"]["valid_until"].value == ""
    assert response.forms["send-notification"]["try_push"].value is None


@pytest.mark.django_db
def test_send_notification_submit_validation_errors(app, notifications_agent: Agent) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/manage/notification/")
    response = response.forms["send-notification"].submit()
    assert response.context["form"].errors == {
        "recipient_fc_hash": ["Ce champ est obligatoire."],
        "content_title": ["Ce champ est obligatoire."],
        "content_body": ["Ce champ est obligatoire."],
    }


@mock.patch("ami.agent_admin.forms.simulate_event_call")
@pytest.mark.django_db
def test_send_notification_submit_with_error(
    simulate_event_call,
    app,
    notifications_agent: Agent,
    partner: Partner,
) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/manage/notification/")

    response.forms["send-notification"]["recipient_fc_hash"] = "a-recipient"
    response.forms["send-notification"]["content_title"] = "a-title"
    response.forms["send-notification"]["content_body"] = "a-body"
    response.forms["send-notification"]["item_generic_status"] = ""
    response.forms["send-notification"]["item_canal"] = ""
    response.forms["send-notification"]["event_date"] = "2026-04-21T16:24:00.000"

    simulate_event_call.return_value = (
        None,
        {
            "recipient_fc_hash": ["error 1", "error 2"],
            "item_type": ["error 3"],
            "unknown_field": ["error 4"],
        },
    )

    response = response.forms["send-notification"].submit()
    assert response.context["form"].errors == {
        "__all__": ["error 4"],
        "recipient_fc_hash": ["error 1", "error 2"],
        "item_type": ["error 3"],
    }
    assert response.pyquery(".fr-notice.success").text() == ""


@mock.patch("ami.agent_admin.forms.simulate_event_call")
@pytest.mark.django_db
def test_send_notification_submit_success(
    simulate_event_call,
    app,
    notifications_agent: Agent,
    partner: Partner,
) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/manage/notification/")

    response.forms["send-notification"]["recipient_fc_hash"] = "a-recipient"
    response.forms["send-notification"]["content_title"] = "a-title"
    response.forms["send-notification"]["content_body"] = "a-body"

    simulate_event_call.return_value = (
        {
            "notification_id": "5c108865-3ca3-403b-bd53-942bcc025f2c",
            "notification_send_status": True,
        },
        None,
    )

    response = response.forms["send-notification"].submit()
    assert (
        response.pyquery(".fr-notice.success").text() == "Notification envoyée avec succès\n"
        "notification_id: 5c108865-3ca3-403b-bd53-942bcc025f2c\nnotification_send_status: True"
    )


@pytest.mark.django_db
def test_send_notification_without_agent_notifications_auth(app) -> None:
    assert_query_fails_without_agent_notifications_auth(app, "/agent-admin/manage/notification/")


@pytest.mark.django_db
def test_simulate_event_call(partner, user, consent):
    response_data, errors = simulate_event_call(
        partner,
        {
            "recipient_fc_hash": user.fc_hash,
            "content_title": "x",
            "content_body": "x",
            "event_date": "2025-01-01 00:00",
        },
    )
    assert response_data is not None
    assert response_data["notification_id"]


@pytest.mark.django_db
def test_simulate_event_call_user_no_consent(partner, user):
    response_data, errors = simulate_event_call(
        partner,
        {
            "recipient_fc_hash": user.fc_hash,
            "content_title": "x",
            "content_body": "x",
            "event_date": "2025-01-01 00:00",
        },
    )
    assert response_data is None
    assert errors
    assert errors == {None: ["Consent not found"]}


@pytest.mark.django_db
def test_simulate_event_call_user_not_found(partner):
    response_data, errors = simulate_event_call(
        partner,
        {
            "recipient_fc_hash": "x",
            "content_title": "x",
            "content_body": "x",
            "event_date": "2025-01-01 00:00",
        },
    )
    assert response_data is None
    assert errors
    assert errors == {None: ["User not found"]}


@pytest.mark.django_db
def test_simulate_event_call_errors(partner):
    response_data, errors = simulate_event_call(partner, {})
    assert response_data is None
    assert errors == {
        "recipient_fc_hash": ["Ce champ est obligatoire."],
        "content_title": ["Ce champ est obligatoire."],
        "content_body": ["Ce champ est obligatoire."],
        "event_date": ["Ce champ est obligatoire."],
    }

    response_data, errors = simulate_event_call(
        partner,
        {
            "recipient_fc_hash": "x",
            "content_title": "x",
            "content_body": "x",
            "event_date": "2025-01-01 00:00",
            "item_parent_id": "plop",
        },
    )
    assert response_data is None
    assert errors == {
        "item_type": ["Ce champ est obligatoire pour une notification associée à un objet."],
        "item_id": ["Ce champ est obligatoire pour une notification associée à un objet."],
        "item_status_label": [
            "Ce champ est obligatoire pour une notification associée à un objet."
        ],
        "item_generic_status": [
            "Ce champ est obligatoire pour une notification associée à un objet."
        ],
    }
