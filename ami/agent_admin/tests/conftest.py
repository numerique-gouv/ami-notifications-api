import pytest

from ami.service.models import Service


@pytest.fixture
def service() -> Service:
    return Service.objects.create(
        partner_id="dinum-dn",
        item_type="ContacterAMI",
        title="Contacter l'équipe AMI",
        short_description="Faites-nous votre retour",
        description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
        url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
        restricted_to="fake-fc-hash",
    )


@pytest.fixture
def services(service) -> list[Service]:
    service2 = Service.objects.create(
        partner_id="psl",
        item_type="OperationTranquilliteVacances",
        title="Opération Tranquillité Vacances",
        short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
        description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
        url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
        with_silent_login=True,
    )
    return [service, service2]
