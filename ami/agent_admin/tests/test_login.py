import pytest


@pytest.mark.django_db
def test_login_pro_connect(
    settings,
    django_app,
) -> None:
    response = django_app.get("/agent-admin/login/")
    response = response.click(href="/agent-admin/oidc/authenticate/")
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(settings.OIDC_OP_AUTHORIZATION_ENDPOINT)
