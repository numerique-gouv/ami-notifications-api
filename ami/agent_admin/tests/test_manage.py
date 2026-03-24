import pytest
from django.utils.formats import date_format
from pyquery import PyQuery

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth


@pytest.mark.django_db
def test_manage_access(
    django_app, agent: Agent, support_agent: Agent, notifications_agent: Agent, admin_agent: Agent
) -> None:
    django_app.set_user(admin_agent.user)
    response = django_app.get("/agent-admin/manage/access/")
    assert [PyQuery(li).text() for li in response.pyquery("#with-role li")] == [
        "AGENT Admin",
        "AGENT Notifications",
        "AGENT Support",
    ]
    last_login = date_format(agent.proconnect_last_login, "d/m/Y à H\\Hi")
    assert [PyQuery(li).text() for li in response.pyquery("#without-role li")] == [
        f"AGENT Simple {last_login}"
    ]


@pytest.mark.django_db
def test_manage_access_without_agent_admin_auth(django_app) -> None:
    assert_query_fails_without_agent_admin_auth(django_app, "/agent-admin/manage/access/")
