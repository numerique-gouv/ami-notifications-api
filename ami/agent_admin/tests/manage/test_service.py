import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth
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


@pytest.mark.django_db
def test_list_services(app, admin_agent: Agent, services: list[Service]) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/")
    assert response.pyquery("table").text() == (
        "Contacter l'équipe AMI\nFaites-nous votre retour\nmodifier\n"
        "Opération Tranquillité Vacances\nInscrivez-vous pour protéger votre domicile pendant votre absence\nmodifier"
    )


@pytest.mark.django_db
def test_list_services_empty(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/")
    assert "Gestion du catalogue de démarches" in response.pyquery("main").text()
    assert response.pyquery("table").text() == ""


@pytest.mark.django_db
def test_list_services_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/service/")
