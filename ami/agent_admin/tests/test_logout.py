import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_auth


@pytest.mark.django_db
def test_logout(settings, django_app, agent: Agent) -> None:
    django_app.set_user(agent.user)
    response = django_app.get("/agent-admin/logout/")
    response = response.form.submit()
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(settings.OIDC_OP_LOGOUT_ENDPOINT)


@pytest.mark.django_db
def test_logout_without_agent_auth(django_app) -> None:
    assert_query_fails_without_agent_auth(django_app, "/agent-admin/logout/")
