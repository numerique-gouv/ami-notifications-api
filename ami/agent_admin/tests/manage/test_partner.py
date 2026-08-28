import uuid

import pytest

from ami.agent.models import Agent
from ami.agent_admin.models import AuditEntry
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth
from ami.partner.models import Partner


@pytest.mark.django_db
def test_list_partners(
    app, admin_agent: Agent, partner: Partner, partner_psl: Partner, partner_dn: Partner
) -> None:
    Partner.objects.exclude(slug__in=["dinum-ami", "dinum-dn", "psl"]).delete()
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/partner/")
    assert response.pyquery("table").text().strip() == (
        "AMI\ndinum-ami\nmodifier\n"
        "Démarche Numérique\ndinum-dn\nmodifier\n"
        "Service Public\npsl\nmodifier"
    )


@pytest.mark.django_db
def test_list_partners_empty(app, admin_agent: Agent) -> None:
    Partner.objects.all().delete()
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/partner/")
    assert "Gestion des partenaires" in response.pyquery("main").text()
    assert response.pyquery("table").text().strip() == ""


@pytest.mark.django_db
def test_list_partners_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/partner/")


@pytest.mark.django_db
def test_add_partner(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/partner/add/")
    assert "Ajouter un partenaire" in response.pyquery("main").text()

    assert response.forms["partner-form"]["slug"].value == ""
    assert response.forms["partner-form"]["name"].value == ""
    assert response.forms["partner-form"]["icon"].value == ""
    assert response.forms["partner-form"]["consent_is_enabled"].value is None


@pytest.mark.django_db
def test_add_partner_submit_validation_errors(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/partner/add/")
    response = response.forms["partner-form"].submit()
    assert response.context["form"].errors == {
        "slug": ["Ce champ est obligatoire."],
        "name": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_add_partner_submit_success(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    Partner.objects.all().delete()
    response = app.get("/agent-admin/manage/partner/add/")
    assert Partner.objects.count() == 0

    response.forms["partner-form"]["slug"] = "new-partner"
    response.forms["partner-form"]["name"] = "New Partner !"
    response.forms["partner-form"]["icon"] = "icon"
    response.forms["partner-form"]["consent_is_enabled"] = True

    response = response.forms["partner-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/partner/"
    assert Partner.objects.count() == 1
    partner = Partner.objects.get()
    assert partner.slug == "new-partner"
    assert partner.name == "New Partner !"
    assert partner.icon == "icon"
    assert partner.consent_is_enabled is True

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "Le partenaire a bien été ajouté."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "partners"
    assert ae1.action_code == "partner-added"
    assert ae1.extra_data == {
        "partner_name": "New Partner !",
        "partner_slug": "new-partner",
        "partner_consent_is_enabled": True,
    }


@pytest.mark.django_db
def test_add_partner_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/partner/add/")


@pytest.mark.django_db
def test_edit_service(app, admin_agent: Agent, partner: Partner) -> None:
    partner.icon = "fr-icon-smartphone-line"
    partner.save()
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/partner/{partner.id}/")
    assert "Modifier un partenaire" in response.pyquery("main").text()

    assert "slug" not in response.context["form"].fields
    assert response.forms["partner-form"]["name"].value == "AMI"
    assert response.forms["partner-form"]["icon"].value == "fr-icon-smartphone-line"
    assert response.forms["partner-form"]["consent_is_enabled"].value == "on"


@pytest.mark.django_db
def test_edit_partner_unknown_id(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/partner/{uuid.uuid4()}/", status=404)


@pytest.mark.django_db
def test_edit_partner_submit_validation_errors(app, admin_agent: Agent, partner: Partner) -> None:
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/partner/{partner.id}/")
    response.forms["partner-form"]["name"].value = ""
    response.forms["partner-form"]["icon"].value = ""
    response.forms["partner-form"]["consent_is_enabled"].value = ""
    response = response.forms["partner-form"].submit()
    assert response.context["form"].errors == {"name": ["Ce champ est obligatoire."]}


@pytest.mark.django_db
def test_edit_service_submit_success(app, admin_agent: Agent, partner: Partner) -> None:
    Partner.objects.exclude(slug="dinum-ami").delete()
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/partner/{partner.id}/")

    response.forms["partner-form"]["name"] = "New AMI"
    response.forms["partner-form"]["icon"] = "icon"
    response.forms["partner-form"]["consent_is_enabled"] = False

    response = response.forms["partner-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/partner/"
    assert Partner.objects.count() == 1
    partner.refresh_from_db()
    assert partner.name == "New AMI"
    assert partner.icon == "icon"
    assert partner.consent_is_enabled is False

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "Le partenaire a bien été modifié."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "partners"
    assert ae1.action_code == "partner-updated"
    assert ae1.extra_data == {
        "partner_name": "New AMI",
        "partner_slug": "dinum-ami",
        "partner_consent_is_enabled": False,
        "old_partner_values_name": "AMI",
        "old_partner_values_slug": "dinum-ami",
        "old_partner_values_consent_is_enabled": True,
    }
