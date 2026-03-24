import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth


@pytest.mark.django_db
def test_manage_access(django_app, admin_agent: Agent) -> None:
    django_app.set_user(admin_agent.user)
    django_app.get("/agent-admin/manage/access/", status=200)


@pytest.mark.django_db
def test_manage_access_without_agent_admin_auth(django_app) -> None:
    assert_query_fails_without_agent_admin_auth(django_app, "/agent-admin/manage/access/")
