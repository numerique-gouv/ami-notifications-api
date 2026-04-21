from importlib import import_module
from typing import cast
from unittest import mock

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.utils.timezone import now

from ami.agent.auth import AgentAuthenticationBackend
from ami.agent.models import Agent


@mock.patch("mozilla_django_oidc.auth.OIDCAuthenticationBackend._verify_jws")
@mock.patch("mozilla_django_oidc.auth.requests")
@pytest.mark.django_db
def test_agent_does_not_exist(
    request_mock,
    jws_mock,
    settings,
) -> None:
    settings.OIDC_USE_NONCE = False
    settings.OIDC_RP_SIGN_ALGO = "HS256"

    auth_request = RequestFactory().get("/foo", {"code": "foo", "state": "bar"})
    engine = import_module(settings.SESSION_ENGINE)
    auth_request.session = engine.SessionStore()

    assert User.objects.count() == 0

    jws_mock.return_value = {"nonce": "nonce"}
    get_json_mock = mock.Mock()
    get_json_mock.json.return_value = {
        "given_name": "Jean",
        "usual_name": "User",
        "email": "user@yopmail.com",
        "sub": "f0773fce-f744-4df3-bf97-1f382c252101",
    }
    get_json_mock.headers = {"content-type": "application/json"}
    request_mock.get.return_value = get_json_mock
    post_json_mock = mock.Mock(status_code=200)
    post_json_mock.json.return_value = {
        "id_token": "id_token",
        "access_token": "access_granted",
    }
    request_mock.post.return_value = post_json_mock

    backend = AgentAuthenticationBackend()
    result = backend.authenticate(request=auth_request)

    assert User.objects.count() == 1
    user = User.objects.get()
    assert result == user
    assert user.first_name == "Jean"
    assert user.last_name == "User"
    assert user.email == "user@yopmail.com"
    agent = cast(Agent, user.agent)  # type: ignore
    assert agent.role is None
    assert agent.proconnect_sub == "f0773fce-f744-4df3-bf97-1f382c252101"
    assert agent.proconnect_last_login is not None
    assert auth_request.session["django_timezone"] == "Europe/Paris"


@mock.patch("mozilla_django_oidc.auth.OIDCAuthenticationBackend._verify_jws")
@mock.patch("mozilla_django_oidc.auth.requests")
@pytest.mark.django_db
def test_agent_does_not_exist_but_user_exists(
    request_mock,
    jws_mock,
    settings,
) -> None:
    settings.OIDC_USE_NONCE = False
    settings.OIDC_RP_SIGN_ALGO = "HS256"

    auth_request = RequestFactory().get("/foo", {"code": "foo", "state": "bar"})
    engine = import_module(settings.SESSION_ENGINE)
    auth_request.session = engine.SessionStore()

    data = {
        "given_name": "Jean",
        "usual_name": "User",
        "email": "user@yopmail.com",
        "sub": "f0773fce-f744-4df3-bf97-1f382c252101",
    }

    jws_mock.return_value = {"nonce": "nonce"}
    get_json_mock = mock.Mock()
    get_json_mock.json.return_value = data
    get_json_mock.headers = {"content-type": "application/json"}
    request_mock.get.return_value = get_json_mock
    post_json_mock = mock.Mock(status_code=200)
    post_json_mock.json.return_value = {
        "id_token": "id_token",
        "access_token": "access_granted",
    }
    request_mock.post.return_value = post_json_mock

    backend = AgentAuthenticationBackend()
    username = backend.get_username(data)
    User.objects.create(username=username)
    assert User.objects.count() == 1
    assert Agent.objects.count() == 0

    result = backend.authenticate(request=auth_request)

    assert User.objects.count() == 1
    user = User.objects.get()
    assert result == user
    assert user.username == username
    assert user.first_name == "Jean"
    assert user.last_name == "User"
    assert user.email == "user@yopmail.com"
    agent = cast(Agent, user.agent)  # type: ignore
    assert agent.role is None
    assert agent.proconnect_sub == "f0773fce-f744-4df3-bf97-1f382c252101"
    assert agent.proconnect_last_login is not None


@mock.patch("mozilla_django_oidc.auth.OIDCAuthenticationBackend._verify_jws")
@mock.patch("mozilla_django_oidc.auth.requests")
@pytest.mark.django_db
def test_agent_exists(
    request_mock,
    jws_mock,
    settings,
) -> None:
    settings.OIDC_USE_NONCE = False
    settings.OIDC_RP_SIGN_ALGO = "HS256"

    auth_request = RequestFactory().get("/foo", {"code": "foo", "state": "bar"})
    engine = import_module(settings.SESSION_ENGINE)
    auth_request.session = engine.SessionStore()

    user = User.objects.create(username="username")
    agent = Agent.objects.create(
        user=user,
        role=Agent.Role.ADMIN,
        proconnect_sub="f0773fce-f744-4df3-bf97-1f382c252101",
        proconnect_last_login=now(),
    )
    proconnect_last_login = agent.proconnect_last_login

    jws_mock.return_value = {"nonce": "nonce"}
    get_json_mock = mock.Mock()
    get_json_mock.json.return_value = {
        "given_name": "Jean",
        "usual_name": "User",
        "email": "user@yopmail.com",
        "sub": "f0773fce-f744-4df3-bf97-1f382c252101",
    }
    get_json_mock.headers = {"content-type": "application/json"}
    request_mock.get.return_value = get_json_mock
    post_json_mock = mock.Mock(status_code=200)
    post_json_mock.json.return_value = {
        "id_token": "id_token",
        "access_token": "access_granted",
    }
    request_mock.post.return_value = post_json_mock

    backend = AgentAuthenticationBackend()
    result = backend.authenticate(request=auth_request)

    assert User.objects.count() == 1
    user.refresh_from_db()
    assert result == user
    assert user.username == "username"
    assert user.first_name == "Jean"
    assert user.last_name == "User"
    assert user.email == "user@yopmail.com"
    agent.refresh_from_db()
    assert agent.user == user
    assert agent.role == Agent.Role.ADMIN
    assert agent.proconnect_sub == "f0773fce-f744-4df3-bf97-1f382c252101"
    assert agent.proconnect_last_login > proconnect_last_login
