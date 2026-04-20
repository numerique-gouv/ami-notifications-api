import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_notifications_auth


@pytest.mark.django_db
def test_send_notification(app, notifications_agent: Agent) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/notification/")
    assert "Envoyer une notification" in response


@pytest.mark.django_db
def test_send_notification_without_agent_notifications_auth(app) -> None:
    assert_query_fails_without_agent_notifications_auth(app, "/agent-admin/notification/")
