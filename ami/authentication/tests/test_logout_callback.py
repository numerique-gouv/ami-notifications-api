import urllib.parse

import pytest

from ami.authentication.models import Nonce


@pytest.mark.django_db
def test_logout_callback(app):
    nonce = Nonce.objects.create(context={"user_does_not_match": True})
    response = app.get(f"/logout-callback?state={nonce.id}")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    parsed_redirected_url_query = urllib.parse.parse_qs(
        urllib.parse.urlparse(redirected_url).query, keep_blank_values=True
    )
    assert "user_does_not_match" in parsed_redirected_url_query
    assert parsed_redirected_url_query.get("redirect_to_hash") == [""]
    assert Nonce.objects.count() == 0


@pytest.mark.django_db
def test_logout_callback_redirect_to_hash(app):
    nonce = Nonce.objects.create(context={"user_does_not_match": True, "login_from_hash": "/test"})
    response = app.get(f"/logout-callback?state={nonce.id}")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173/?")
    parsed_redirected_url_query = urllib.parse.parse_qs(
        urllib.parse.urlparse(redirected_url).query, keep_blank_values=True
    )
    assert "user_does_not_match" in parsed_redirected_url_query
    assert parsed_redirected_url_query.get("redirect_to_hash") == ["/test"]
    assert Nonce.objects.count() == 0


@pytest.mark.parametrize(
    "state", [None, "", "some random nonce", "b4dca26a-206f-4156-931f-da3c0b2f47ba"]
)
@pytest.mark.django_db
def test_logout_callback_bad_state(state, app):
    if state is None:
        response = app.get("/logout-callback")
    else:
        Nonce.objects.create(nonce=state)
        response = app.get(f"/logout-callback?state={state}")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.endswith("#/login")


@pytest.mark.django_db
def test_logout_callback_empty_nonce(app):
    nonce = Nonce.objects.create()
    response = app.get(f"/logout-callback?state={nonce.id}")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.endswith("#/login")
    assert Nonce.objects.count() == 0
