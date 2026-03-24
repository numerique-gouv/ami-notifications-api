import pytest
from django.contrib.auth.models import User
from django.utils.timezone import now

from ami.agent.models import Agent


@pytest.fixture
def agent():
    user = User.objects.create(
        username="agent-user",
        first_name="Simple",
        last_name="AGENT",
        email="simple@agent.com",
    )
    return Agent.objects.create(
        user=user,
        proconnect_sub="no-role",
        proconnect_last_login=now(),
    )


@pytest.fixture
def support_agent():
    user = User.objects.create(
        username="agent-support-user",
        first_name="Support",
        last_name="AGENT",
        email="support@agent.com",
    )
    return Agent.objects.create(
        user=user,
        role=Agent.Role.SUPPORT,
        proconnect_sub="support",
        proconnect_last_login=now(),
    )


@pytest.fixture
def notifications_agent():
    user = User.objects.create(
        username="agent-notifications-user",
        first_name="Notifications",
        last_name="AGENT",
        email="notifications@agent.com",
    )
    return Agent.objects.create(
        user=user,
        role=Agent.Role.NOTIFICATIONS,
        proconnect_sub="notifications",
        proconnect_last_login=now(),
    )


@pytest.fixture
def admin_agent():
    user = User.objects.create(
        username="agent-admin-user",
        first_name="Admin",
        last_name="AGENT",
        email="admin@agent.com",
    )
    return Agent.objects.create(
        user=user,
        role=Agent.Role.ADMIN,
        proconnect_sub="admin",
        proconnect_last_login=now(),
    )
