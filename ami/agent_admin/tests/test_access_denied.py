import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_auth


@pytest.mark.django_db
def test_access_denied(app, agent: Agent) -> None:
    app.set_user(agent.user)
    app.get("/agent-admin/access-denied/", status=200)


@pytest.mark.django_db
def test_access_denied_without_agent_auth(app) -> None:
    assert_query_fails_without_agent_auth(app, "/agent-admin/access-denied/")
