import pytest
from django.contrib.auth.models import User

from ami.agent.models import Agent


@pytest.fixture
def agent():
    user = User.objects.create(username="agent-user")
    return Agent.objects.create(user=user)
