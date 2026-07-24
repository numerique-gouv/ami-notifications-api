import datetime
from unittest import mock

import pytest
from pytest_httpx import HTTPXMock

from ami.service.data.internal import get_internal_data, get_internal_source
from ami.service.models import Service
from ami.service.schemas import (
    ServicesItem,
    ServicesSource,
    ServicesSourceStatus,
)
from ami.user.models import User


@pytest.mark.django_db
def test_get_internal_data(
    user: User,
    httpx_mock: HTTPXMock,
) -> None:
    service1 = Service.objects.create(
        partner_id="psl",
        item_type="OperationTranquilliteVacances",
        title="Opération Tranquillité Vacances",
        short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
        description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
        url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
        with_silent_login=True,
    )
    service2 = Service.objects.create(
        partner_id="dinum-dn",
        item_type="ContacterAMI",
        title="Contacter l'équipe AMI",
        short_description="Faites-nous votre retour",
        description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
        url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
        restricted_to=f"{user.fc_hash} another-fake-fc-hash",
    )
    Service.objects.create(
        partner_id="dinum-dn",
        item_type="Restricted",
        title="Démarche restreinte",
        short_description="Non publiée",
        description="Cette démarche n'est pas encore visible pour tout le monde",
        url="https://localhost:8000/",
        restricted_to="another-fake-fc-hash",
    )
    result = get_internal_data(current_user=user)
    assert result == [
        ServicesItem(
            partner_id="dinum-dn",
            item_type="ContacterAMI",
            title="Contacter l'équipe AMI",
            short_description="Faites-nous votre retour",
            description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
            url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
            with_silent_login=False,
            created_at=service2.created_at,
            updated_at=service2.updated_at,
        ),
        ServicesItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            title="Opération Tranquillité Vacances",
            short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
            description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
            url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
            with_silent_login=True,
            created_at=service1.created_at,
            updated_at=service1.updated_at,
        ),
    ]


@pytest.mark.django_db
def test_get_internal_source(
    user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    items = [
        ServicesItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            title="Opération Tranquillité Vacances",
            short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
            description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
            url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
            with_silent_login=True,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
        ServicesItem(
            partner_id="dinum-dn",
            item_type="ContacterAMI",
            title="Contacter l'équipe AMI",
            short_description="Faites-nous votre retour",
            description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
            url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
            with_silent_login=False,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    ]
    data_mock = mock.Mock(return_value=items)
    monkeypatch.setattr("ami.service.data.internal.get_internal_data", data_mock)
    result = get_internal_source(current_user=user)
    assert result == ServicesSource(status=ServicesSourceStatus.SUCCESS, items=items)
