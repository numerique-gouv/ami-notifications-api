import pytest

from ami.agent.models import Agent


@pytest.mark.django_db
def test_agent_has_role(
    agent: Agent, support_agent: Agent, notifications_agent: Agent, admin_agent: Agent
) -> None:
    assert agent.has_role_admin is False
    assert agent.has_role_notifications is False
    assert agent.has_role_support is False

    assert support_agent.has_role_admin is False
    assert support_agent.has_role_notifications is False
    assert support_agent.has_role_support is True

    assert notifications_agent.has_role_admin is False
    assert notifications_agent.has_role_notifications is True
    assert notifications_agent.has_role_support is True

    assert admin_agent.has_role_admin is True
    assert admin_agent.has_role_notifications is True
    assert admin_agent.has_role_support is True
