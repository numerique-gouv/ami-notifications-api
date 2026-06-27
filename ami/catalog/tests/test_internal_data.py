import datetime
from unittest import mock

import pytest
from pytest_httpx import HTTPXMock

from ami.catalog.data.internal import get_internal_catalog, get_internal_data
from ami.catalog.models import Procedure
from ami.catalog.schemas import (
    CatalogItem,
    CatalogItems,
    CatalogItemsStatus,
)


@pytest.mark.django_db
def test_get_internal_data(
    httpx_mock: HTTPXMock,
) -> None:
    procedure1 = Procedure.objects.create(
        partner_id="psl",
        external_item_type="OperationTranquilliteVacances",
        title="Opération Tranquillité Vacances",
        short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
        description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
        external_url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
        with_silent_login=True,
    )
    procedure2 = Procedure.objects.create(
        partner_id="dinum-dn",
        external_item_type="ContacterAMI",
        title="Contacter l'équipe AMI",
        short_description="Faites-nous votre retour",
        description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
        external_url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
    )
    result = get_internal_data()
    assert result == [
        CatalogItem(
            partner_id="dinum-dn",
            external_item_type="ContacterAMI",
            title="Contacter l'équipe AMI",
            short_description="Faites-nous votre retour",
            description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
            external_url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
            with_silent_login=False,
            created_at=procedure2.created_at,
            updated_at=procedure2.updated_at,
        ),
        CatalogItem(
            partner_id="psl",
            external_item_type="OperationTranquilliteVacances",
            title="Opération Tranquillité Vacances",
            short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
            description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
            external_url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
            with_silent_login=True,
            created_at=procedure1.created_at,
            updated_at=procedure1.updated_at,
        ),
    ]


def test_get_internal_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    items = [
        CatalogItem(
            partner_id="psl",
            external_item_type="OperationTranquilliteVacances",
            title="Opération Tranquillité Vacances",
            short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
            description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
            external_url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
            with_silent_login=True,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
        CatalogItem(
            partner_id="dinum-dn",
            external_item_type="ContacterAMI",
            title="Contacter l'équipe AMI",
            short_description="Faites-nous votre retour",
            description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
            external_url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
            with_silent_login=False,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    ]
    data_mock = mock.Mock(return_value=items)
    monkeypatch.setattr("ami.catalog.data.internal.get_internal_data", data_mock)
    result = get_internal_catalog()
    assert result == CatalogItems(status=CatalogItemsStatus.SUCCESS, items=items)
