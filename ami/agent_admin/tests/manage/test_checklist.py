import json
import uuid

import pytest

from ami.agent.models import Agent
from ami.agent_admin.models import AuditEntry
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth
from ami.checklist.models import CheckList
from ami.partner.models import Partner


@pytest.mark.django_db
def test_list_checklists(app, admin_agent: Agent, checklist: CheckList) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/checklist/")
    assert response.pyquery("table").text().strip() == "F16225\nJe deviens parent\nmodifier"


@pytest.mark.django_db
def test_list_checklists_empty(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/checklist/")
    assert "Gestion des listes d’étapes" in response.pyquery("main").text()
    assert response.pyquery("table").text().strip() == ""


@pytest.mark.django_db
def test_list_checklists_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/checklist/")


@pytest.mark.django_db
def test_add_checklist(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/checklist/add/")
    assert "Ajouter une liste d’étapes" in response.pyquery("main").text()

    assert response.forms["checklist-form"]["partner"].value == ""
    assert response.forms["checklist-form"]["external_id"].value == ""
    assert response.forms["checklist-form"]["definition"].value == "{}"


@pytest.mark.django_db
def test_add_checklist_submit_validation_errors(app, admin_agent: Agent, partner: Partner) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/checklist/add/")
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "external_id": ["Ce champ est obligatoire."],
        "definition": ["Ce champ est obligatoire."],
    }

    response.forms["checklist-form"]["definition"].value = "{}"
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "external_id": ["Ce champ est obligatoire."],
        "definition": ["Ce champ est obligatoire."],
    }

    response.forms["checklist-form"]["partner"] = partner.id
    response.forms["checklist-form"]["external_id"] = "F16225"
    response.forms["checklist-form"]["definition"].value = "invalid"
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "definition": ["Saisissez du contenu JSON valide."],
    }

    response.forms["checklist-form"]["definition"].value = json.dumps({"foo": "bar"})
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "definition": [
            "Format invalide: le titre de la liste d’étapes n’a pas été trouvé dans la définition."
        ],
    }


@pytest.mark.django_db
def test_add_checklist_submit_success(app, admin_agent: Agent, partner: Partner) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/checklist/add/")
    assert CheckList.objects.count() == 0

    response.forms["checklist-form"]["partner"] = partner.id
    response.forms["checklist-form"]["external_id"] = "F16225"
    response.forms["checklist-form"]["definition"] = json.dumps({"title": "Je deviens parent"})

    response = response.forms["checklist-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/checklist/"
    assert CheckList.objects.count() == 1
    checklist = CheckList.objects.get()
    assert checklist.partner == partner
    assert checklist.external_id == "F16225"
    assert checklist.title == "Je deviens parent"
    assert checklist.definition == {"title": "Je deviens parent"}

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La liste d’étapes a bien été ajoutée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "checklists"
    assert ae1.action_code == "checklist-added"
    assert ae1.extra_data == {
        "checklist_external_id": "F16225",
        "checklist_partner_id": "dinum-ami",
    }


@pytest.mark.django_db
def test_add_checklist_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/checklist/add/")


@pytest.mark.django_db
def test_edit_checklist(app, admin_agent: Agent, checklist: CheckList, partner_dn: Partner) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/checklist/{checklist.id}/")
    assert "Modifier une liste d’étape" in response.pyquery("main").text()

    assert response.forms["checklist-form"]["partner"].value == str(partner_dn.id)
    assert response.forms["checklist-form"]["external_id"].value == "F16225"
    assert response.forms["checklist-form"]["definition"].value == "{}"


@pytest.mark.django_db
def test_edit_checklist_unknown_id(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/checklist/{uuid.uuid4()}/", status=404)


@pytest.mark.django_db
def test_edit_checklist_submit_validation_errors(
    app, admin_agent: Agent, checklist: CheckList, partner: Partner
) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/checklist/{checklist.id}/")
    response.forms["checklist-form"]["partner"].value = ""
    response.forms["checklist-form"]["external_id"].value = ""
    response.forms["checklist-form"]["definition"].value = ""
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "external_id": ["Ce champ est obligatoire."],
        "definition": ["Ce champ est obligatoire."],
    }

    response.forms["checklist-form"]["definition"].value = "{}"
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "partner": ["Ce champ est obligatoire."],
        "external_id": ["Ce champ est obligatoire."],
        "definition": ["Ce champ est obligatoire."],
    }

    response.forms["checklist-form"]["partner"] = partner.id
    response.forms["checklist-form"]["external_id"] = "F16225bis"
    response.forms["checklist-form"]["definition"].value = "invalid"
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "definition": ["Saisissez du contenu JSON valide."],
    }

    response.forms["checklist-form"]["definition"].value = json.dumps({"foo": "bar"})
    response = response.forms["checklist-form"].submit()
    assert response.context["form"].errors == {
        "definition": [
            "Format invalide: le titre de la liste d’étapes n’a pas été trouvé dans la définition."
        ],
    }


@pytest.mark.django_db
def test_edit_checklist_submit_success(
    app, admin_agent: Agent, checklist: CheckList, partner: Partner
) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/checklist/{checklist.id}/")

    response.forms["checklist-form"]["partner"] = partner.id
    response.forms["checklist-form"]["external_id"] = "F16225bis"
    response.forms["checklist-form"]["definition"] = json.dumps({"title": "Je déménage"})

    response = response.forms["checklist-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/checklist/"
    assert CheckList.objects.count() == 1
    checklist.refresh_from_db()
    assert checklist.partner == partner
    assert checklist.external_id == "F16225bis"
    assert checklist.title == "Je déménage"
    assert checklist.definition == {"title": "Je déménage"}

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La liste d’étapes a bien été modifiée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "checklists"
    assert ae1.action_code == "checklist-updated"
    assert ae1.extra_data == {
        "checklist_external_id": "F16225bis",
        "checklist_partner_id": "dinum-ami",
        "old_checklist_values_external_id": "F16225",
        "old_checklist_values_partner_id": "dinum-dn",
    }


@pytest.mark.django_db
def test_edit_checklist_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(
        app, f"/agent-admin/manage/checklist/{uuid.uuid4()}/"
    )


@pytest.mark.django_db
def test_delete_checklist(app, admin_agent: Agent, checklist: CheckList):
    app.set_user(admin_agent.user)
    response = app.post(f"/agent-admin/manage/checklist/{checklist.id}/delete/")
    assert response.headers["location"] == "/agent-admin/manage/checklist/"
    assert CheckList.objects.count() == 0

    response = response.follow()
    assert (
        response.pyquery(".fr-notice.success").text() == "La liste d’étapes a bien été supprimée."
    )

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "checklists"
    assert ae1.action_code == "checklist-removed"
    assert ae1.extra_data == {
        "checklist_external_id": "F16225",
        "checklist_partner_id": "dinum-dn",
    }


@pytest.mark.django_db
def test_delete_checklist_not_found(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    app.post(f"/agent-admin/manage/checklist/{uuid.uuid4()}/delete/", status=404)


@pytest.mark.django_db
def test_delete_user_method_not_allowed(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/checklist/{uuid.uuid4()}/delete/", status=405)


@pytest.mark.django_db
def test_delete_user_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(
        app, f"/agent-admin/manage/checklist/{uuid.uuid4()}/delete/", method="post"
    )
