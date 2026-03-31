import pytest
from django.utils.formats import date_format
from pyquery import PyQuery

from ami.agent.models import Agent
from ami.agent_admin.models import AuditEntry
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth
from ami.agent_admin.utils import audit


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
    ] == ["Aucun"]


@pytest.mark.django_db
def test_manage_access_for_form_submission(
    django_app, agent: Agent, support_agent: Agent, notifications_agent: Agent, admin_agent: Agent
) -> None:
    django_app.set_user(admin_agent.user)
    response = django_app.get("/agent-admin/manage/access/")
    response.forms["agent-forms"]["authorized-1-role"].value = ""
    response.forms["agent-forms"]["authorized-2-role"].value = "notifications"
    response.forms["agent-forms"]["unauthorized-0-role"].value = "support"
    response = response.forms["agent-forms"].submit()
    assert "/agent-admin/manage/access/" in response.headers["location"]

    agent.refresh_from_db()
    assert agent.role == Agent.Role.SUPPORT
    support_agent.refresh_from_db()
    assert support_agent.role == Agent.Role.NOTIFICATIONS
    notifications_agent.refresh_from_db()
    assert notifications_agent.role is None
    admin_agent.refresh_from_db()
    assert admin_agent.role == Agent.Role.ADMIN

    assert AuditEntry.objects.count() == 3
    ae1, ae2, ae3 = AuditEntry.objects.all().order_by("created_at")

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "access"
    assert ae1.action_code == "role-added"
    assert ae1.extra_data == {
        "agent_id": str(agent.id),
        "agent_first_name": "Simple",
        "agent_last_name": "AGENT",
        "agent_email": "simple@agent.com",
        "agent_proconnect_sub": "no-role",
        "new_role": "support",
        "new_role_name": "Support",
    }

    assert ae2.author == admin_agent
    assert ae2.author_first_name == "Admin"
    assert ae2.author_last_name == "AGENT"
    assert ae2.author_email == "admin@agent.com"
    assert ae2.author_proconnect_sub == "admin"
    assert ae2.action_type == "access"
    assert ae2.action_code == "role-removed"
    assert ae2.extra_data == {
        "agent_id": str(notifications_agent.id),
        "agent_email": "notifications@agent.com",
        "agent_last_name": "AGENT",
        "agent_first_name": "Notifications",
        "agent_proconnect_sub": "notifications",
        "old_role": "notifications",
        "old_role_name": "Notifications",
    }

    assert ae3.author == admin_agent
    assert ae3.author_first_name == "Admin"
    assert ae3.author_last_name == "AGENT"
    assert ae3.author_email == "admin@agent.com"
    assert ae3.author_proconnect_sub == "admin"
    assert ae3.action_type == "access"
    assert ae3.action_code == "role-updated"
    assert ae3.extra_data == {
        "agent_id": str(support_agent.id),
        "agent_email": "support@agent.com",
        "agent_last_name": "AGENT",
        "agent_first_name": "Support",
        "agent_proconnect_sub": "support",
        "old_role": "support",
        "old_role_name": "Support",
        "new_role": "notifications",
        "new_role_name": "Notifications",
    }


@pytest.mark.django_db
def test_manage_access_for_logs(django_app, agent: Agent, admin_agent: Agent) -> None:
    django_app.set_user(admin_agent.user)
    response = django_app.get("/agent-admin/manage/access/")
    assert [PyQuery(tr).text() for tr in response.pyquery("#table-activity tr")] == [
        "Agent concerné\nRôle attribué\nDate",
    ]

    ae1 = audit(
        "access:role-added",
        admin_agent,
        {
            "agent": agent,
            "new_role": Agent.Role.SUPPORT,
        },
    )
    ae2 = audit(
        "access:role-updated",
        admin_agent,
        {
            "agent": agent,
            "old_role": Agent.Role.ADMIN,
            "new_role": Agent.Role.SUPPORT,
        },
    )
    ae3 = audit(
        "access:role-removed",
        admin_agent,
        {
            "agent": agent,
            "old_role": Agent.Role.NOTIFICATIONS,
        },
    )
    audit("unknown:unknown", admin_agent, {})  # ignored, bad action_type and action_code

    response = django_app.get("/agent-admin/manage/access/")
    ae1_date = date_format(ae1.created_at, "d/m/Y\nà H\\Hi")
    ae2_date = date_format(ae2.created_at, "d/m/Y\nà H\\Hi")
    ae3_date = date_format(ae3.created_at, "d/m/Y\nà H\\Hi")
    assert [PyQuery(tr).text() for tr in response.pyquery("#table-activity tr")] == [
        "Agent concerné\nRôle attribué\nDate",
        f"AGENT Simple\npar AGENT Admin\nAucun\nex : Notifications\n{ae3_date}",
        f"AGENT Simple\npar AGENT Admin\nSupport\nex : Admin\n{ae2_date}",
        f"AGENT Simple\npar AGENT Admin\nSupport\nex : Aucun\n{ae1_date}",
    ]


@pytest.mark.django_db
def test_manage_access_without_agent_admin_auth(django_app) -> None:
    assert_query_fails_without_agent_admin_auth(django_app, "/agent-admin/manage/access/")
