import uuid

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


@pytest.mark.django_db
def test_add_service(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/add/")
    assert "Ajouter une démarche" in response.pyquery("main").text()

    assert response.forms["service-form"]["partner_id"].value == ""
    assert response.forms["service-form"]["item_type"].value == ""
    assert response.forms["service-form"]["title"].value == ""
    assert response.forms["service-form"]["short_description"].value == ""
    assert response.forms["service-form"]["description"].value == ""
    assert response.forms["service-form"]["url"].value == ""
    assert response.forms["service-form"]["with_silent_login"].value is None


@pytest.mark.django_db
def test_add_service_submit_validation_errors(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/add/")
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner_id": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_add_service_submit_success(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/add/")
    assert Service.objects.count() == 0

    response.forms["service-form"]["partner_id"] = "dinum-ami"
    response.forms["service-form"]["item_type"] = "JeDéménage"
    response.forms["service-form"]["title"] = "Je déménage"
    response.forms["service-form"]["short_description"] = "Démarche de changement d'adresse"
    response.forms["service-form"]["description"] = "**Démarche de changement d'adresse**"
    response.forms["service-form"]["url"] = "http://demarche-demenagement"
    response.forms["service-form"]["with_silent_login"] = True

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 1
    service = Service.objects.get()
    assert service.partner_id == "dinum-ami"
    assert service.item_type == "JeDéménage"
    assert service.title == "Je déménage"
    assert service.short_description == "Démarche de changement d'adresse"
    assert service.description == "**Démarche de changement d'adresse**"
    assert service.url == "http://demarche-demenagement"
    assert service.with_silent_login is True

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La démarche a bien été ajoutée."


@pytest.mark.django_db
def test_add_service_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/service/add/")


@pytest.mark.django_db
def test_edit_service(app, admin_agent: Agent, service: Service) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/service/{service.id}/")
    assert "Modifier une démarche" in response.pyquery("main").text()

    assert response.forms["service-form"]["partner_id"].value == "dinum-dn"
    assert response.forms["service-form"]["item_type"].value == "ContacterAMI"
    assert response.forms["service-form"]["title"].value == "Contacter l'équipe AMI"
    assert response.forms["service-form"]["short_description"].value == "Faites-nous votre retour"
    assert (
        response.forms["service-form"]["description"].value
        == "Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire"
    )
    assert (
        response.forms["service-form"]["url"].value
        == "https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}"
    )
    assert response.forms["service-form"]["with_silent_login"].value is None


@pytest.mark.django_db
def test_edit_service_unknown_id(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/service/{uuid.uuid4()}/", status=404)


@pytest.mark.django_db
def test_edit_service_submit_validation_errors(app, admin_agent: Agent, service: Service) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/service/{service.id}/")
    response.forms["service-form"]["partner_id"].value = ""
    response.forms["service-form"]["item_type"].value = ""
    response.forms["service-form"]["title"].value = ""
    response.forms["service-form"]["short_description"].value = ""
    response.forms["service-form"]["description"].value = ""
    response.forms["service-form"]["url"].value = ""
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner_id": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_edit_service_submit_success(app, admin_agent: Agent, service: Service) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/service/{service.id}/")

    response.forms["service-form"]["partner_id"] = "dinum-ami"
    response.forms["service-form"]["item_type"] = "JeDéménage"
    response.forms["service-form"]["title"] = "Je déménage"
    response.forms["service-form"]["short_description"] = "Démarche de changement d'adresse"
    response.forms["service-form"]["description"] = "**Démarche de changement d'adresse**"
    response.forms["service-form"]["url"] = "http://demarche-demenagement"
    response.forms["service-form"]["with_silent_login"] = True

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 1
    service.refresh_from_db()
    assert service.partner_id == "dinum-ami"
    assert service.item_type == "JeDéménage"
    assert service.title == "Je déménage"
    assert service.short_description == "Démarche de changement d'adresse"
    assert service.description == "**Démarche de changement d'adresse**"
    assert service.url == "http://demarche-demenagement"
    assert service.with_silent_login is True

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La démarche a bien été modifiée."


@pytest.mark.django_db
def test_edit_service_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, f"/agent-admin/manage/service/{uuid.uuid4()}/")


@pytest.mark.django_db
def test_delete_service(app, admin_agent: Agent, services: list[Service]):
    service = services[0]
    app.set_user(admin_agent.user)
    response = app.post(f"/agent-admin/manage/service/{service.id}/delete/")
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 1
    assert Service.objects.filter(id=service.id).exists() is False

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La démarche a bien été supprimée."


@pytest.mark.django_db
def test_delete_service_not_found(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    app.post(f"/agent-admin/manage/service/{uuid.uuid4()}/delete/", status=404)


@pytest.mark.django_db
def test_delete_user_method_not_allowed(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/service/{uuid.uuid4()}/delete/", status=405)


@pytest.mark.django_db
def test_delete_user_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(
        app, f"/agent-admin/manage/service/{uuid.uuid4()}/delete/", method="post"
    )
