import uuid

import pytest

from ami.agent.models import Agent
from ami.agent_admin.models import AuditEntry
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth
from ami.partner.models import Partner
from ami.service.models import Service


@pytest.mark.django_db
def test_list_services(app, admin_agent: Agent, services: list[Service]) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/")
    assert response.pyquery("table#catalog").text().strip() == (
        "Contacter l'équipe AMI\nFaites-nous votre retour\nmodifier\n"
        "Opération Tranquillité Vacances\nInscrivez-vous pour protéger votre domicile pendant votre absence\nmodifier"
    )
    assert response.pyquery("table#sos").text().strip() == (
        "Démarche 3\nShort description 3\nmodifier"
    )
    assert response.pyquery("table#steps").text().strip() == (
        "Démarche 4\nShort description 4\nmodifier"
    )


@pytest.mark.django_db
def test_list_services_empty(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/")
    assert "Gestion du catalogue de démarches" in response.pyquery("main").text()
    assert response.pyquery("table").text().strip() == ""


@pytest.mark.django_db
def test_list_services_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/service/")


@pytest.mark.django_db
def test_add_service(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/add/catalog/")
    assert "Ajouter une démarche" in response.pyquery("main").text()

    assert "kind" not in response.context["form"].fields
    assert "icon" not in response.context["form"].fields
    assert response.forms["service-form"]["partner"].value == ""
    assert response.forms["service-form"]["item_type"].value == ""
    assert response.forms["service-form"]["title"].value == ""
    assert response.forms["service-form"]["short_description"].value == ""
    assert response.forms["service-form"]["description"].value == ""
    assert response.forms["service-form"]["url"].value == ""
    assert response.forms["service-form"]["with_silent_login"].value is None
    assert response.forms["service-form"]["restricted_to"].value == ""

    response = app.get("/agent-admin/manage/service/add/sos/")
    assert "kind" not in response.context["form"].fields
    assert response.forms["service-form"]["icon"].value == ""

    response = app.get("/agent-admin/manage/service/add/steps/")
    assert "kind" not in response.context["form"].fields
    assert response.forms["service-form"]["icon"].value == ""


@pytest.mark.django_db
def test_add_service_submit_validation_errors(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/add/catalog/")
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }

    response = app.get("/agent-admin/manage/service/add/sos/")
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }

    response = app.get("/agent-admin/manage/service/add/steps/")
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_add_service_submit_success(app, admin_agent: Agent, partner: Partner) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/add/catalog/")
    assert Service.objects.count() == 0

    response.forms["service-form"]["partner"] = partner.id
    response.forms["service-form"]["item_type"] = "JeDéménage"
    response.forms["service-form"]["title"] = "Je déménage"
    response.forms["service-form"]["short_description"] = "Démarche de changement d'adresse"
    response.forms["service-form"]["description"] = "**Démarche de changement d'adresse**"
    response.forms["service-form"]["url"] = "http://demarche-demenagement"
    response.forms["service-form"]["with_silent_login"] = True
    response.forms["service-form"]["restricted_to"] = "fake-fc-hash another-fake-fc-hash"

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 1
    service = Service.objects.get()
    assert service.kind == Service.Kind.CATALOG
    assert service.partner == partner
    assert service.item_type == "JeDéménage"
    assert service.title == "Je déménage"
    assert service.short_description == "Démarche de changement d'adresse"
    assert service.description == "**Démarche de changement d'adresse**"
    assert service.url == "http://demarche-demenagement"
    assert service.icon == ""
    assert service.with_silent_login is True
    assert service.restricted_to == "another-fake-fc-hash fake-fc-hash"

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La démarche a bien été ajoutée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "services"
    assert ae1.action_code == "service-added"
    assert ae1.extra_data == {
        "service_kind": "catalog",
        "service_item_type": "JeDéménage",
        "service_partner_id": "dinum-ami",
    }

    response = app.get("/agent-admin/manage/service/add/sos/")

    response.forms["service-form"]["partner"] = partner.id
    response.forms["service-form"]["item_type"] = "JeDéménage"
    response.forms["service-form"]["title"] = "Je déménage"
    response.forms["service-form"]["short_description"] = "Démarche de changement d'adresse"
    response.forms["service-form"]["description"] = "**Démarche de changement d'adresse**"
    response.forms["service-form"]["url"] = "http://demarche-demenagement"
    response.forms["service-form"]["icon"] = "fr-icon-earth-line"
    response.forms["service-form"]["with_silent_login"] = True
    response.forms["service-form"]["restricted_to"] = "fake-fc-hash another-fake-fc-hash"

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 2
    service = Service.objects.latest("created_at")
    assert service.kind == Service.Kind.SOS
    assert service.partner == partner
    assert service.item_type == "JeDéménage"
    assert service.title == "Je déménage"
    assert service.short_description == "Démarche de changement d'adresse"
    assert service.description == "**Démarche de changement d'adresse**"
    assert service.url == "http://demarche-demenagement"
    assert service.icon == "fr-icon-earth-line"
    assert service.with_silent_login is True
    assert service.restricted_to == "another-fake-fc-hash fake-fc-hash"

    response = app.get("/agent-admin/manage/service/add/steps/")

    response.forms["service-form"]["partner"] = partner.id
    response.forms["service-form"]["item_type"] = "JeDéménage"
    response.forms["service-form"]["title"] = "Je déménage"
    response.forms["service-form"]["short_description"] = "Démarche de changement d'adresse"
    response.forms["service-form"]["description"] = "**Démarche de changement d'adresse**"
    response.forms["service-form"]["url"] = "http://demarche-demenagement"
    response.forms["service-form"]["icon"] = "fr-icon-earth-line"
    response.forms["service-form"]["with_silent_login"] = True
    response.forms["service-form"]["restricted_to"] = "fake-fc-hash another-fake-fc-hash"

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 3
    service = Service.objects.latest("created_at")
    assert service.kind == Service.Kind.STEPS
    assert service.partner == partner
    assert service.item_type == "JeDéménage"
    assert service.title == "Je déménage"
    assert service.short_description == "Démarche de changement d'adresse"
    assert service.description == "**Démarche de changement d'adresse**"
    assert service.url == "http://demarche-demenagement"
    assert service.icon == "fr-icon-earth-line"
    assert service.with_silent_login is True
    assert service.restricted_to == "another-fake-fc-hash fake-fc-hash"


@pytest.mark.django_db
def test_add_service_submit_success_duplicated_restricted_to(
    app, admin_agent: Agent, partner: Partner
) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/service/add/catalog/")
    assert Service.objects.count() == 0

    response.forms["service-form"]["partner"] = partner.id
    response.forms["service-form"]["item_type"] = "JeDéménage"
    response.forms["service-form"]["title"] = "Je déménage"
    response.forms["service-form"]["short_description"] = "Démarche de changement d'adresse"
    response.forms["service-form"]["description"] = "**Démarche de changement d'adresse**"
    response.forms["service-form"]["url"] = "http://demarche-demenagement"
    response.forms["service-form"]["with_silent_login"] = True
    response.forms["service-form"]["restricted_to"] = "duplicated-value duplicated-value"

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 1
    service = Service.objects.get()
    assert service.restricted_to == "duplicated-value"


@pytest.mark.django_db
def test_add_service_unknown_kind(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    app.get("/agent-admin/manage/service/add/unknown/", status=404)


@pytest.mark.django_db
def test_add_service_catalog_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/service/add/catalog/")


@pytest.mark.django_db
def test_add_service_sos_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/service/add/sos/")


@pytest.mark.django_db
def test_add_service_steps_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/service/add/steps/")


@pytest.mark.django_db
def test_edit_service(
    app, admin_agent: Agent, services: list[Service], partner_dn: Partner
) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/service/{services[0].id}/")
    assert "Modifier une démarche" in response.pyquery("main").text()

    assert "kind" not in response.context["form"].fields
    assert "icon" not in response.context["form"].fields
    assert response.forms["service-form"]["partner"].value == str(partner_dn.id)
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
    assert response.forms["service-form"]["restricted_to"].value == "fake-fc-hash"

    response = app.get(f"/agent-admin/manage/service/{services[2].id}/")
    assert "kind" not in response.context["form"].fields
    assert response.forms["service-form"]["icon"].value == ""

    response = app.get(f"/agent-admin/manage/service/{services[3].id}/")
    assert "kind" not in response.context["form"].fields
    assert response.forms["service-form"]["icon"].value == ""


@pytest.mark.django_db
def test_edit_service_unknown_id(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/service/{uuid.uuid4()}/", status=404)


@pytest.mark.django_db
def test_edit_service_submit_validation_errors(
    app, admin_agent: Agent, services: list[Service]
) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/service/{services[0].id}/")
    response.forms["service-form"]["partner"].value = ""
    response.forms["service-form"]["item_type"].value = ""
    response.forms["service-form"]["title"].value = ""
    response.forms["service-form"]["short_description"].value = ""
    response.forms["service-form"]["description"].value = ""
    response.forms["service-form"]["url"].value = ""
    response.forms["service-form"]["restricted_to"].value = ""
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }

    response = app.get(f"/agent-admin/manage/service/{services[2].id}/")
    response.forms["service-form"]["partner"].value = ""
    response.forms["service-form"]["item_type"].value = ""
    response.forms["service-form"]["title"].value = ""
    response.forms["service-form"]["short_description"].value = ""
    response.forms["service-form"]["description"].value = ""
    response.forms["service-form"]["url"].value = ""
    response.forms["service-form"]["icon"].value = ""
    response.forms["service-form"]["restricted_to"].value = ""
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }

    response = app.get(f"/agent-admin/manage/service/{services[3].id}/")
    response.forms["service-form"]["partner"].value = ""
    response.forms["service-form"]["item_type"].value = ""
    response.forms["service-form"]["title"].value = ""
    response.forms["service-form"]["short_description"].value = ""
    response.forms["service-form"]["description"].value = ""
    response.forms["service-form"]["url"].value = ""
    response.forms["service-form"]["icon"].value = ""
    response.forms["service-form"]["restricted_to"].value = ""
    response = response.forms["service-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "item_type": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "short_description": ["Ce champ est obligatoire."],
        "description": ["Ce champ est obligatoire."],
        "url": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_edit_service_submit_success(
    app, admin_agent: Agent, services: list[Service], partner: Partner
) -> None:
    app.set_user(admin_agent.user)
    service = services[0]
    response = app.get(f"/agent-admin/manage/service/{service.id}/")

    response.forms["service-form"]["partner"] = partner.id
    response.forms["service-form"]["item_type"] = "JeDéménage"
    response.forms["service-form"]["title"] = "Je déménage"
    response.forms["service-form"]["short_description"] = "Démarche de changement d'adresse"
    response.forms["service-form"]["description"] = "**Démarche de changement d'adresse**"
    response.forms["service-form"]["url"] = "http://demarche-demenagement"
    response.forms["service-form"]["with_silent_login"] = True
    response.forms["service-form"]["restricted_to"] = "fake-fc-hash another-fake-fc-hash"

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 4
    service.refresh_from_db()
    assert service.kind == Service.Kind.CATALOG
    assert service.partner == partner
    assert service.item_type == "JeDéménage"
    assert service.title == "Je déménage"
    assert service.short_description == "Démarche de changement d'adresse"
    assert service.description == "**Démarche de changement d'adresse**"
    assert service.url == "http://demarche-demenagement"
    assert service.icon == ""
    assert service.with_silent_login is True
    assert service.restricted_to == "another-fake-fc-hash fake-fc-hash"

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La démarche a bien été modifiée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "services"
    assert ae1.action_code == "service-updated"
    assert ae1.extra_data == {
        "service_kind": "catalog",
        "service_item_type": "JeDéménage",
        "service_partner_id": "dinum-ami",
        "old_service_values_kind": "catalog",
        "old_service_values_item_type": "ContacterAMI",
        "old_service_values_partner_id": "dinum-dn",
    }

    service = services[2]
    response = app.get(f"/agent-admin/manage/service/{service.id}/")
    response.forms["service-form"]["icon"] = "fr-icon-earth-line"
    response = response.forms["service-form"].submit()
    assert Service.objects.count() == 4
    service.refresh_from_db()
    assert service.icon == "fr-icon-earth-line"

    service = services[3]
    response = app.get(f"/agent-admin/manage/service/{service.id}/")
    response.forms["service-form"]["icon"] = "fr-icon-earth-line"
    response = response.forms["service-form"].submit()
    assert Service.objects.count() == 4
    service.refresh_from_db()
    assert service.icon == "fr-icon-earth-line"


@pytest.mark.django_db
def test_edit_service_submit_success_duplicated_value(
    app, admin_agent: Agent, service: Service
) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/service/{service.id}/")

    response.forms["service-form"]["restricted_to"] = "duplicated-value duplicated-value"

    response = response.forms["service-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 1
    service.refresh_from_db()
    assert service.restricted_to == "duplicated-value"


@pytest.mark.django_db
def test_edit_service_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, f"/agent-admin/manage/service/{uuid.uuid4()}/")


@pytest.mark.django_db
def test_delete_service(app, admin_agent: Agent, services: list[Service]):
    service = services[0]
    app.set_user(admin_agent.user)
    response = app.post(f"/agent-admin/manage/service/{service.id}/delete/")
    assert response.headers["location"] == "/agent-admin/manage/service/"
    assert Service.objects.count() == 3
    assert Service.objects.filter(id=service.id).exists() is False

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La démarche a bien été supprimée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "services"
    assert ae1.action_code == "service-removed"
    assert ae1.extra_data == {
        "service_kind": "catalog",
        "service_item_type": "ContacterAMI",
        "service_partner_id": "dinum-dn",
    }


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
