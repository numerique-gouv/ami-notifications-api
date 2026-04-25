import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_support_auth


@pytest.mark.django_db
def test_home_with_support_agent(app, support_agent: Agent) -> None:
    app.set_user(support_agent.user)
    response = app.get("/agent-admin/", status=200)
    assert "/agent-admin/manage/access/" not in response
    assert "/agent-admin/manage/user/" not in response
    assert "/agent-admin/manage/notification/" not in response


@pytest.mark.django_db
def test_home_with_notifications_agent(app, notifications_agent: Agent) -> None:
    app.set_user(notifications_agent.user)
    response = app.get("/agent-admin/", status=200)
    assert "/agent-admin/manage/access/" not in response
    assert "/agent-admin/manage/user/" not in response
    assert "/agent-admin/manage/notification/" in response


@pytest.mark.django_db
def test_home_with_admin_agent(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/", status=200)
    assert "/agent-admin/manage/access/" in response
    assert "/agent-admin/manage/user/" in response
    assert "/agent-admin/manage/notification/" in response


@pytest.mark.django_db
def test_home_without_agent_support_auth(app) -> None:
    assert_query_fails_without_agent_support_auth(app, "/agent-admin/")
