import pytest

from ami.agent.models import Agent


@pytest.mark.django_db
def test_login_pro_connect(
    settings,
    django_app,
) -> None:
    response = django_app.get("/agent-admin/login/")
    response = response.click(href="/agent-admin/oidc/authenticate/")
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(settings.OIDC_OP_AUTHORIZATION_ENDPOINT)


@pytest.mark.django_db
def test_login_pro_connect_with_auth(
    django_app,
    agent: Agent,
) -> None:
    django_app.set_user(agent.user)
    response = django_app.get("/agent-admin/login/")
    assert "/agent-admin/oidc/authenticate/" not in response
