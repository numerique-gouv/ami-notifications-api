import pytest

from ami.agent.models import Agent
from ami.agent_admin.utils import audit


@pytest.mark.django_db
def test_audit(app, agent: Agent, admin_agent: Agent):
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

    ae1.refresh_from_db()
    ae2.refresh_from_db()
    ae3.refresh_from_db()

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
    assert ae2.action_code == "role-updated"
    assert ae2.extra_data == {
        "agent_id": str(agent.id),
        "agent_email": "simple@agent.com",
        "agent_last_name": "AGENT",
        "agent_first_name": "Simple",
        "agent_proconnect_sub": "no-role",
        "old_role": "admin",
        "old_role_name": "Admin",
        "new_role": "support",
        "new_role_name": "Support",
    }

    assert ae3.author == admin_agent
    assert ae3.author_first_name == "Admin"
    assert ae3.author_last_name == "AGENT"
    assert ae3.author_email == "admin@agent.com"
    assert ae3.author_proconnect_sub == "admin"
    assert ae3.action_type == "access"
    assert ae3.action_code == "role-removed"
    assert ae3.extra_data == {
        "agent_id": str(agent.id),
        "agent_email": "simple@agent.com",
        "agent_last_name": "AGENT",
        "agent_first_name": "Simple",
        "agent_proconnect_sub": "no-role",
        "old_role": "notifications",
        "old_role_name": "Notifications",
    }
