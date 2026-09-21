import pytest

from ami.checklist.models import CheckList
from ami.partner.models import Partner
from ami.service.models import Service


@pytest.fixture
def service(partner_dn: Partner) -> Service:
    return Service.objects.create(
        partner=partner_dn,
        item_type="ContacterAMI",
        title="Contacter l'équipe AMI",
        service_name="Faites-nous votre retour",
        description="Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
        url="https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}",
        restricted_to="fake-fc-hash",
    )


@pytest.fixture
def services(service: Service, partner_dn: Partner, partner_psl: Partner) -> list[Service]:
    service2 = Service.objects.create(
        partner=partner_psl,
        item_type="OperationTranquilliteVacances",
        title="Opération Tranquillité Vacances",
        service_name="Inscrivez-vous pour protéger votre domicile pendant votre absence",
        description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
        url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
        with_silent_login=True,
    )
    service3 = Service.objects.create(
        kind="sos",
        partner=partner_dn,
        item_type="Démarche3",
        title="Démarche 3",
        service_name="Short description 3",
        description="Description 3",
        url="https://localhost:8000/service3",
    )
    service4 = Service.objects.create(
        kind="steps",
        partner=partner_dn,
        item_type="Démarche4",
        title="Démarche 4",
        service_name="Short description 4",
        description="Description 4",
        url="https://localhost:8000/service4",
    )
    return [service, service2, service3, service4]


@pytest.fixture
def checklist(partner_dn: Partner) -> CheckList:
    return CheckList.objects.create(
        partner=partner_dn,
        external_id="F16225",
        title="Je deviens parent",
        definition={},
    )
