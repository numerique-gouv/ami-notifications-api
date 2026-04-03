from django.contrib.auth.models import User

from ami.agent.models import Agent


def assert_query_fails_without_agent_auth(
    app,
    tested_url: str,
    method: str = "get",
) -> None:
    response = getattr(app, method)(tested_url, status=302)
    assert "/agent-admin/login/?next=/agent-admin/" in response.headers["location"]

    user = User.objects.create(username="simple-user")
    app.set_user(user)
    response = getattr(app, method)(tested_url, status=302)
    assert "/agent-admin/login/?next=/agent-admin/" in response.headers["location"]


def assert_query_fails_without_agent_support_auth(
    app,
    tested_url: str,
    method: str = "get",
) -> None:
    assert_query_fails_without_agent_auth(app, tested_url, method=method)

    user = User.objects.create(username="agent-user")
    Agent.objects.create(user=user)
    app.set_user(user)
    response = getattr(app, method)(tested_url, status=302)
    assert "/agent-admin/access-denied/" in response.headers["location"]


def assert_query_fails_without_agent_notifications_auth(
    app,
    tested_url: str,
    method: str = "get",
) -> None:
    assert_query_fails_without_agent_support_auth(app, tested_url, method=method)

    agent = Agent.objects.get()

    agent.role = Agent.Role.SUPPORT
    agent.save()
    response = getattr(app, method)(tested_url, status=302)
    assert "/agent-admin/access-denied/" in response.headers["location"]


def assert_query_fails_without_agent_admin_auth(
    app,
    tested_url: str,
    method: str = "get",
) -> None:
    assert_query_fails_without_agent_notifications_auth(app, tested_url, method=method)

    agent = Agent.objects.get()

    agent.role = Agent.Role.NOTIFICATIONS
    agent.save()
    response = getattr(app, method)(tested_url, status=302)
    assert "/agent-admin/access-denied/" in response.headers["location"]
