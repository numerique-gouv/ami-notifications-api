import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_support_auth


@pytest.mark.django_db
def test_home_with_support_agent(django_app, support_agent: Agent) -> None:
    django_app.set_user(support_agent.user)
    response = django_app.get("/agent-admin/", status=200)
    assert "/agent-admin/manage/access/" not in response


@pytest.mark.django_db
def test_home_with_notifications_agent(django_app, notifications_agent: Agent) -> None:
    django_app.set_user(notifications_agent.user)
    response = django_app.get("/agent-admin/", status=200)
    assert "/agent-admin/manage/access/" not in response


@pytest.mark.django_db
def test_home_with_admin_agent(django_app, admin_agent: Agent) -> None:
    django_app.set_user(admin_agent.user)
    response = django_app.get("/agent-admin/", status=200)
    assert "/agent-admin/manage/access/" in response


@pytest.mark.django_db
def test_home_without_agent_support_auth(django_app) -> None:
    assert_query_fails_without_agent_support_auth(django_app, "/agent-admin/")
