import pytest
from django.utils.formats import date_format
from pyquery import PyQuery

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth


@pytest.mark.django_db
def test_manage_access_for_form_initialization(
    django_app, agent: Agent, support_agent: Agent, notifications_agent: Agent, admin_agent: Agent
) -> None:
    django_app.set_user(admin_agent.user)
    response = django_app.get("/agent-admin/manage/access/")
    assert [PyQuery(td).text() for td in response.pyquery("#with-role td:nth-child(1)")] == [
        "AGENT\nAdmin",
        "AGENT\nNotifications",
        "AGENT\nSupport",
    ]
    assert [
        PyQuery(opt).text()
        for opt in response.pyquery("#with-role td:nth-child(2) option[selected]")
    ] == ["Admin", "Notifications", "Support"]
    last_login = date_format(agent.proconnect_last_login, "d/m/Y\nà H\\Hi")
    assert [PyQuery(td).text() for td in response.pyquery("#without-role td:nth-child(1)")] == [
        "AGENT\nSimple"
    ]
    assert [PyQuery(td).text() for td in response.pyquery("#without-role td:nth-child(2)")] == [
        last_login
    ]
    assert [
        PyQuery(opt).text()
        for opt in response.pyquery("#without-role td:nth-child(3) option[selected]")
    ] == ["---------"]


@pytest.mark.django_db
def test_manage_access_for_form_submission(
    django_app, agent: Agent, support_agent: Agent, notifications_agent: Agent, admin_agent: Agent
) -> None:
    django_app.set_user(admin_agent.user)
    response = django_app.get("/agent-admin/manage/access/")
    response.form["authorized-1-role"].value = ""
    response.form["authorized-2-role"].value = "notifications"
    response.form["unauthorized-0-role"].value = "support"
    response = response.form.submit()
    assert "/agent-admin/manage/access/" in response.headers["location"]
    agent.refresh_from_db()
    assert agent.role == Agent.Role.SUPPORT
    support_agent.refresh_from_db()
    assert support_agent.role == Agent.Role.NOTIFICATIONS
    notifications_agent.refresh_from_db()
    assert notifications_agent.role is None
    admin_agent.refresh_from_db()
    assert admin_agent.role == Agent.Role.ADMIN


@pytest.mark.django_db
def test_manage_access_without_agent_admin_auth(django_app) -> None:
    assert_query_fails_without_agent_admin_auth(django_app, "/agent-admin/manage/access/")
