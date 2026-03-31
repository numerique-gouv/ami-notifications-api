import pytest

from ami.agent.models import Agent


@pytest.mark.django_db
def test_logout(settings, django_app, admin_agent: Agent) -> None:
    django_app.set_user(admin_agent.user)
    response = django_app.get("/agent-admin/")
    assert "/agent-admin/oidc/logout/" in response
    response = response.forms["logout-form"].submit()
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(settings.OIDC_OP_LOGOUT_ENDPOINT)


@pytest.mark.django_db
def test_logout_on_login_page(settings, django_app) -> None:
    response = django_app.get("/agent-admin/login/")
    assert "/agent-admin/oidc/logout/" not in response
