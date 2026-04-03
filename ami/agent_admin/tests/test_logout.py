import pytest

from ami.agent.models import Agent


@pytest.mark.django_db
def test_logout(settings, app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/")
    assert "/agent-admin/oidc/logout/" in response
    response = response.forms["logout-form"].submit()
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(settings.OIDC_OP_LOGOUT_ENDPOINT)


@pytest.mark.django_db
def test_logout_on_login_page(settings, app) -> None:
    response = app.get("/agent-admin/login/")
    assert "/agent-admin/oidc/logout/" not in response
