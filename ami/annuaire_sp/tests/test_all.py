import datetime
from unittest import mock

import pytest

from ami.annuaire_sp.models import Mairie
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_mairie(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
):
    login(app, user)

    duration_mock = mock.Mock(
        return_value=datetime.datetime(2026, 2, 14, 11, 16, tzinfo=datetime.timezone.utc)
    )
    monkeypatch.setattr(
        "ami.annuaire_sp.api_views.DurationExpiration.compute_expires_at", duration_mock
    )

    Mairie.objects.create(
        nom="Mairie 1",
        code_insee_commune="00001",
        id_service_local="id1",
        url_service_public="url1",
    )

    resp = app.get("/api/v1/users/data/mairie/00001")
    assert resp.json == {
        "nom": "Mairie 1",
        "url_service_public": "url1",
        "expires_at": "2026-02-14T11:16:00Z",
    }


@pytest.mark.django_db
def test_get_mairie_not_found(app, user: User):
    login(app, user)

    app.get("/api/v1/users/data/mairie/00001", status=404)


@pytest.mark.django_db
def test_get_mairie_without_auth(app):
    Mairie.objects.create(
        nom="Mairie 1",
        code_insee_commune="00001",
        id_service_local="id1",
        url_service_public="url1",
    )
    assert_query_fails_without_auth(app, "/api/v1/users/data/mairie/00001")
