import pytest

from ami.agent.models import Agent
from ami.agent_admin.utils import audit
from ami.partner.models import Partner
from ami.service.models import Service
from ami.user.models import User


@pytest.mark.django_db
def test_audit(
    app,
    agent: Agent,
    admin_agent: Agent,
    user: User,
    services: list[Service],
    partner: Partner,
    partner_psl: Partner,
):
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
    ae4 = audit(
        "user:deleted",
        admin_agent,
        {
            "user": user,
        },
    )
    ae5 = audit(
        "user:seen",
        admin_agent,
        {
            "user": user,
        },
    )
    ae6 = audit(
        "services:service-added",
        admin_agent,
        {
            "service": services[0],
        },
    )
    ae7 = audit(
        "services:service-updated",
        admin_agent,
        {
            "service": services[0],
            "old_service_values": services[1],
        },
    )
    ae8 = audit(
        "services:service-removed",
        admin_agent,
        {
            "service": services[2],
        },
    )
    ae9 = audit(
        "partners:partner-added",
        admin_agent,
        {
            "partner": partner,
        },
    )
    ae10 = audit(
        "partners:partner-updated",
        admin_agent,
        {
            "partner": partner_psl,
            "old_partner_values": partner,
        },
    )

    ae1.refresh_from_db()
    ae2.refresh_from_db()
    ae3.refresh_from_db()
    ae4.refresh_from_db()
    ae5.refresh_from_db()
    ae6.refresh_from_db()
    ae7.refresh_from_db()
    ae8.refresh_from_db()
    ae9.refresh_from_db()
    ae10.refresh_from_db()

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

    assert ae4.author == admin_agent
    assert ae4.author_first_name == "Admin"
    assert ae4.author_last_name == "AGENT"
    assert ae4.author_email == "admin@agent.com"
    assert ae4.author_proconnect_sub == "admin"
    assert ae4.action_type == "user"
    assert ae4.action_code == "deleted"
    assert ae4.extra_data == {
        "user_id": str(user.id),
        "user_fc_hash": "c3cdbc4c175f4ebdb1b6d00175ae8732d41e76bb0a27aca8ffdc0006e25fda0d",
    }

    assert ae5.author == admin_agent
    assert ae5.author_first_name == "Admin"
    assert ae5.author_last_name == "AGENT"
    assert ae5.author_email == "admin@agent.com"
    assert ae5.author_proconnect_sub == "admin"
    assert ae5.action_type == "user"
    assert ae5.action_code == "seen"
    assert ae5.extra_data == {
        "user_id": str(user.id),
        "user_fc_hash": "c3cdbc4c175f4ebdb1b6d00175ae8732d41e76bb0a27aca8ffdc0006e25fda0d",
    }

    assert ae6.author == admin_agent
    assert ae6.author_first_name == "Admin"
    assert ae6.author_last_name == "AGENT"
    assert ae6.author_email == "admin@agent.com"
    assert ae6.author_proconnect_sub == "admin"
    assert ae6.action_type == "services"
    assert ae6.action_code == "service-added"
    assert ae6.extra_data == {
        "service_kind": "catalog",
        "service_item_type": "ContacterAMI",
        "service_partner_id": "dinum-dn",
    }

    assert ae7.author == admin_agent
    assert ae7.author_first_name == "Admin"
    assert ae7.author_last_name == "AGENT"
    assert ae7.author_email == "admin@agent.com"
    assert ae7.author_proconnect_sub == "admin"
    assert ae7.action_type == "services"
    assert ae7.action_code == "service-updated"
    assert ae7.extra_data == {
        "service_kind": "catalog",
        "service_item_type": "ContacterAMI",
        "service_partner_id": "dinum-dn",
        "old_service_values_kind": "catalog",
        "old_service_values_item_type": "OperationTranquilliteVacances",
        "old_service_values_partner_id": "psl",
    }

    assert ae8.author == admin_agent
    assert ae8.author_first_name == "Admin"
    assert ae8.author_last_name == "AGENT"
    assert ae8.author_email == "admin@agent.com"
    assert ae8.author_proconnect_sub == "admin"
    assert ae8.action_type == "services"
    assert ae8.action_code == "service-removed"
    assert ae8.extra_data == {
        "service_kind": "sos",
        "service_item_type": "Démarche3",
        "service_partner_id": "dinum-dn",
    }

    assert ae9.author == admin_agent
    assert ae9.author_first_name == "Admin"
    assert ae9.author_last_name == "AGENT"
    assert ae9.author_email == "admin@agent.com"
    assert ae9.author_proconnect_sub == "admin"
    assert ae9.action_type == "partners"
    assert ae9.action_code == "partner-added"
    assert ae9.extra_data == {
        "partner_name": "AMI",
        "partner_slug": "dinum-ami",
        "partner_consent_is_enabled": True,
    }

    assert ae10.author == admin_agent
    assert ae10.author_first_name == "Admin"
    assert ae10.author_last_name == "AGENT"
    assert ae10.author_email == "admin@agent.com"
    assert ae10.author_proconnect_sub == "admin"
    assert ae10.action_type == "partners"
    assert ae10.action_code == "partner-updated"
    assert ae10.extra_data == {
        "partner_name": "Service Public",
        "partner_slug": "psl",
        "partner_consent_is_enabled": False,
        "old_partner_values_name": "AMI",
        "old_partner_values_slug": "dinum-ami",
        "old_partner_values_consent_is_enabled": True,
    }
