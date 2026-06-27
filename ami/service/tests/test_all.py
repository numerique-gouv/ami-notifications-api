import datetime
from unittest import mock

import pytest

from ami.service.schemas import ServicesItem, ServicesSource, ServicesSourceStatus
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_services(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login(app, user)

    internal_source = ServicesSource(
        status=ServicesSourceStatus.SUCCESS,
        items=[
            ServicesItem(
                partner_id="psl",
                item_type="OperationTranquilliteVacances",
                title="Opération Tranquillité Vacances",
                short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
                description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
                url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
                with_silent_login=True,
                created_at=datetime.datetime(2026, 2, 23, 17, 24, tzinfo=datetime.timezone.utc),
                updated_at=datetime.datetime(2026, 2, 24, 17, 24, tzinfo=datetime.timezone.utc),
            ),
            ServicesItem(
                partner_id="dinum-dn",
                item_type="ContacterAMI",
                title="Contacter l'équipe AMI",
                short_description="Faites-nous votre retour",
                description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
                url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
                with_silent_login=False,
                created_at=datetime.datetime(2026, 1, 26, 17, 24, tzinfo=datetime.timezone.utc),
                updated_at=datetime.datetime(2026, 1, 27, 17, 24, tzinfo=datetime.timezone.utc),
            ),
        ],
    )
    internal_mock = mock.Mock(return_value=internal_source)
    monkeypatch.setattr("ami.service.api_views.get_internal_source", internal_mock)
    duration_mock = mock.Mock(
        return_value=datetime.datetime(2026, 2, 14, 11, 16, tzinfo=datetime.timezone.utc)
    )
    monkeypatch.setattr(
        "ami.service.api_views.DurationExpiration.compute_expires_at", duration_mock
    )

    response = app.get("/api/v1/users/data/services", status=200)
    assert response.json == {
        "internal": {
            "status": "success",
            "items": [
                {
                    "partner_id": "psl",
                    "item_type": "OperationTranquilliteVacances",
                    "title": "Opération Tranquillité Vacances",
                    "short_description": "Inscrivez-vous pour protéger votre domicile pendant votre absence",
                    "description": "Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
                    "url": "https://localhost:8000/mademarche/demarcheGenerique/"
                    "?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
                    "with_silent_login": True,
                    "created_at": "2026-02-23T17:24:00Z",
                    "updated_at": "2026-02-24T17:24:00Z",
                },
                {
                    "partner_id": "dinum-dn",
                    "item_type": "ContacterAMI",
                    "title": "Contacter l'équipe AMI",
                    "short_description": "Faites-nous votre retour",
                    "description": "Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
                    "url": "https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
                    "with_silent_login": False,
                    "created_at": "2026-01-26T17:24:00Z",
                    "updated_at": "2026-01-27T17:24:00Z",
                },
            ],
            "expires_at": "2026-02-14T11:16:00Z",
        }
    }


@pytest.mark.django_db
def test_get_services_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/data/services")
