from django.contrib.auth.models import User


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
