from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.core.management import CommandError, call_command
from django.utils.timezone import now

from ami.agent.models import Agent


@pytest.mark.django_db
def test_command():
    User.objects.create(username="no-agent", email="no-agent@user.com")

    with pytest.raises(CommandError) as e:
        call_command("promote-agent-to-admin", "no-agent@user.com")
    assert str(e.value) == 'Agent with email "no-agent@user.com" does not exist'

    user = User.objects.create(
        username="simple-agent",
        email="simple-agent@user.com",
        first_name="Simple",
        last_name="AGENT",
    )
    agent = Agent.objects.create(
        user=user,
        proconnect_sub="sub",
        proconnect_last_login=now(),
    )

    with pytest.raises(CommandError) as e:
        call_command("promote-agent-to-admin", "unkown@user.com")
    assert str(e.value) == 'Agent with email "unkown@user.com" does not exist'

    last_updated_at = agent.updated_at
    out = StringIO()
    call_command("promote-agent-to-admin", "simple-agent@user.com", stdout=out)
    assert (
        'Successfully promoted agent "Simple AGENT (simple-agent@user.com)" to admin'
        in out.getvalue()
    )
    agent.refresh_from_db()
    assert agent.role == Agent.Role.ADMIN
    assert agent.updated_at > last_updated_at
