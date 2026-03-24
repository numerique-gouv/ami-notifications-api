import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_auth


@pytest.mark.django_db
def test_home(django_app, agent: Agent) -> None:
    django_app.set_user(agent.user)
    django_app.get("/agent-admin/")


@pytest.mark.django_db
def test_home_without_agent_auth(django_app) -> None:
    assert_query_fails_without_agent_auth(django_app, "/agent-admin/")
