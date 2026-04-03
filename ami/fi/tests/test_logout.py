from django.conf import settings

from ami.tests.utils import url_contains_param


def test_logout(
    django_app,
) -> None:
    redirect_uri = f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_LOGOUT_CALLBACK_ENDPOINT}"

    response = django_app.get(
        "/api/v1/fi/logout/", params={"post_logout_redirect_uri": redirect_uri}
    )
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(redirect_uri)
    assert url_contains_param(
        "state",
        "",
        redirected_url,
    )

    response = django_app.get(
        "/api/v1/fi/logout/",
        params={"post_logout_redirect_uri": redirect_uri, "state": "fake-state"},
    )
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(redirect_uri)
    assert url_contains_param(
        "state",
        "fake-state",
        redirected_url,
    )


def test_logout_bad_request_no_redirect_uri(
    django_app,
) -> None:
    django_app.get("/api/v1/fi/logout/", status=400)


def test_logout_bad_request_wrong_redirect_uri(
    django_app,
) -> None:
    django_app.get(
        "/api/v1/fi/logout/", params={"post_logout_redirect_uri": "wrong-uri"}, status=400
    )
