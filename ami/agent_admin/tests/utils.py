from django.contrib.auth.models import User

from ami.agent.models import Agent


def assert_query_fails_without_agent_auth(
    django_app,
    tested_url: str,
    method: str = "get",
) -> None:
    response = getattr(django_app, method)(tested_url, status=302)
    assert "/agent-admin/login/?next=/agent-admin/" in response.headers["location"]

    user = User.objects.create(username="simple-user")
    django_app.set_user(user)
    response = getattr(django_app, method)(tested_url, status=302)
    assert "/agent-admin/login/?next=/agent-admin/" in response.headers["location"]


def assert_query_fails_without_agent_support_auth(
    django_app,
    tested_url: str,
    method: str = "get",
) -> None:
    assert_query_fails_without_agent_auth(django_app, tested_url, method=method)

    user = User.objects.create(username="agent-user")
    Agent.objects.create(user=user)
    django_app.set_user(user)
    response = getattr(django_app, method)(tested_url, status=302)
    assert "/agent-admin/access-denied/" in response.headers["location"]


def assert_query_fails_without_agent_notifications_auth(
    django_app,
    tested_url: str,
    method: str = "get",
) -> None:
    assert_query_fails_without_agent_support_auth(django_app, tested_url, method=method)

    agent = Agent.objects.get()

    agent.role = Agent.Role.SUPPORT
    agent.save()
    response = getattr(django_app, method)(tested_url, status=302)
    assert "/agent-admin/access-denied/" in response.headers["location"]


def assert_query_fails_without_agent_admin_auth(
    django_app,
    tested_url: str,
    method: str = "get",
) -> None:
    assert_query_fails_without_agent_notifications_auth(django_app, tested_url, method=method)

    agent = Agent.objects.get()

    agent.role = Agent.Role.NOTIFICATIONS
    agent.save()
    response = getattr(django_app, method)(tested_url, status=302)
    assert "/agent-admin/access-denied/" in response.headers["location"]
