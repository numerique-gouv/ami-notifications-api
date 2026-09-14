import uuid

import pytest

from ami.agent.models import Agent
from ami.agent_admin.models import AuditEntry
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth
from ami.page.models import Page, Section


@pytest.mark.django_db
def test_list_pages(app, admin_agent: Agent) -> None:
    Page.objects.create(title="Accessibilité", slug="accessibilite")
    Page.objects.create(title="Données personnelles", slug="donnees-personnelles")
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/page/")
    assert (
        response.pyquery("table").text().strip()
        == "Accessibilité\naccessibilite\nmodifier\nDonnées personnelles\ndonnees-personnelles\nmodifier"
    )


@pytest.mark.django_db
def test_list_pages_empty(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/page/")
    assert "Gestion des pages" in response.pyquery("main").text()
    assert response.pyquery("table").text().strip() == ""


@pytest.mark.django_db
def test_list_pages_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/page/")


@pytest.mark.django_db
def test_add_page(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/page/add/")
    assert "Ajouter une page" in response.pyquery("main").text()

    assert response.forms["page-form"]["slug"].value == ""
    assert response.forms["page-form"]["title"].value == ""


@pytest.mark.django_db
def test_add_page_submit_validation_errors(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/page/add/")
    response = response.forms["page-form"].submit()
    assert response.context["form"].errors == {
        "slug": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_add_page_submit_success(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    Page.objects.all().delete()
    response = app.get("/agent-admin/manage/page/add/")
    assert Page.objects.count() == 0

    response.forms["page-form"]["slug"] = "new-page"
    response.forms["page-form"]["title"] = "New Page"

    response = response.forms["page-form"].submit()
    assert Page.objects.count() == 1
    page = Page.objects.get()
    assert page.slug == "new-page"
    assert page.title == "New Page"
    assert response.headers["location"] == f"/agent-admin/manage/page/{page.id}/"

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La page a bien été ajoutée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "pages"
    assert ae1.action_code == "page-added"
    assert ae1.extra_data == {
        "page_slug": "new-page",
        "page_title": "New Page",
    }


@pytest.mark.django_db
def test_add_page_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/page/add/")


@pytest.mark.django_db
def test_edit_page_unknown_id(app, admin_agent: Agent) -> None:
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/page/{uuid.uuid4()}/", status=404)


@pytest.mark.django_db
def test_edit_page_submit_validation_errors(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/")
    response.forms["page-form"]["title"].value = ""
    response = response.forms["page-form"].submit()
    assert response.context["form"].errors == {"title": ["Ce champ est obligatoire."]}


@pytest.mark.django_db
def test_edit_page_submit_success(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/")

    response.forms["page-form"]["title"] = "Changed title"

    response = response.forms["page-form"].submit()
    assert response.headers["location"] == "/agent-admin/manage/page/"
    assert Page.objects.count() == 1
    page.refresh_from_db()
    assert page.title == "Changed title"

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La page a bien été modifiée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "pages"
    assert ae1.action_code == "page-updated"
    assert ae1.extra_data == {
        "page_title": "Changed title",
        "page_slug": "accessibilite",
        "old_page_values_title": "Accessibilité",
        "old_page_values_slug": "accessibilite",
    }


@pytest.mark.django_db
def test_delete_page(app, admin_agent: Agent):
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    app.set_user(admin_agent.user)
    response = app.post(f"/agent-admin/manage/page/{page.id}/delete/")
    assert response.headers["location"] == "/agent-admin/manage/page/"
    assert Page.objects.count() == 0

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La page a bien été supprimée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "pages"
    assert ae1.action_code == "page-removed"
    assert ae1.extra_data == {"page_slug": "accessibilite", "page_title": "Accessibilité"}


@pytest.mark.django_db
def test_add_section_submit_validation_errors(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/add-section/")
    response = response.forms["section-form"].submit()
    assert response.context["form"].errors == {
        "slug": ["Ce champ est obligatoire."],
        "title": ["Ce champ est obligatoire."],
        "order": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_add_section_submit_success(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/add-section/")
    response.forms["section-form"]["slug"] = "new-section"
    response.forms["section-form"]["title"] = "New Section"
    response.forms["section-form"]["order"] = "2"
    response.forms["section-form"]["text"] = "text"
    response = response.forms["section-form"].submit()
    response = response.follow()
    assert response.pyquery("table").text().strip() == "New Section\nnew-section\nmodifier"


@pytest.mark.django_db
def test_edit_section_unknown_id(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    section = Section.objects.create(title="Déclaration", slug="declaration", page=page, order=0)
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/page/{page.id}/{uuid.uuid4()}/", status=404)
    app.get(f"/agent-admin/manage/page/{uuid.uuid4()}/{section.id}/", status=404)


@pytest.mark.django_db
def test_edit_section_submit_validation_errors(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    section = Section.objects.create(title="Déclaration", slug="declaration", page=page, order=0)
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/{section.id}/")
    response.forms["section-form"]["title"] = ""
    response = response.forms["section-form"].submit()
    assert response.context["form"].errors == {"title": ["Ce champ est obligatoire."]}


@pytest.mark.django_db
def test_edit_section_submit_success(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    section = Section.objects.create(title="Déclaration", slug="declaration", page=page, order=0)
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/{section.id}/")
    response.forms["section-form"]["title"] = "New title"
    response = response.forms["section-form"].submit()
    assert Section.objects.count() == 1
    section.refresh_from_db()
    assert section.title == "New title"

    assert response.headers["location"] == f"/agent-admin/manage/page/{page.id}/"
    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La section a bien été modifiée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "pages"
    assert ae1.action_code == "section-updated"
    assert ae1.extra_data == {
        "old_section_values_page_id": str(page.id),
        "old_section_values_page_slug": "accessibilite",
        "section_page_id": str(page.id),
        "section_page_slug": "accessibilite",
        "section_slug": "declaration",
        "section_text": "",
        "section_order": 0,
        "section_title": "New title",
        "old_section_values_slug": "declaration",
        "old_section_values_text": "",
        "old_section_values_order": 0,
        "old_section_values_title": "Déclaration",
    }


@pytest.mark.django_db
def test_edit_section_submit_and_continue(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    section = Section.objects.create(title="Déclaration", slug="declaration", page=page, order=0)
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/{section.id}/")
    response.forms["section-form"]["save-and-continue"] = "save-and-continue"
    response.forms["section-form"]["title"] = "New title"
    response = response.forms["section-form"].submit()
    assert Section.objects.count() == 1
    section.refresh_from_db()
    assert section.title == "New title"

    # stay on same page
    assert response.headers["location"] == f"/agent-admin/manage/page/{page.id}/{section.id}/"
    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La section a bien été modifiée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "pages"
    assert ae1.action_code == "section-updated"
    assert ae1.extra_data == {
        "old_section_values_page_id": str(page.id),
        "old_section_values_page_slug": "accessibilite",
        "section_page_id": str(page.id),
        "section_page_slug": "accessibilite",
        "section_slug": "declaration",
        "section_text": "",
        "section_order": 0,
        "section_title": "New title",
        "old_section_values_slug": "declaration",
        "old_section_values_text": "",
        "old_section_values_order": 0,
        "old_section_values_title": "Déclaration",
    }


@pytest.mark.django_db
def test_section_markdown_rendering(app, admin_agent: Agent) -> None:
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    section = Section.objects.create(
        title="Déclaration", slug="declaration", page=page, order=0, text="# title\n\ntext"
    )
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/page/{page.id}/{section.id}/")
    assert response.pyquery("#section-preview h1").text() == "title"
    assert response.pyquery("#section-preview p").text() == "text"


@pytest.mark.django_db
def test_delete_section(app, admin_agent: Agent):
    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    section = Section.objects.create(
        title="Déclaration", slug="declaration", page=page, order=0, text="# title\n\ntext"
    )
    app.set_user(admin_agent.user)
    response = app.post(f"/agent-admin/manage/page/{page.id}/{section.id}/delete/")
    assert response.headers["location"] == f"/agent-admin/manage/page/{page.id}/"
    assert Section.objects.count() == 0

    response = response.follow()
    assert response.pyquery(".fr-notice.success").text() == "La section a bien été supprimée."

    assert AuditEntry.objects.count() == 1
    ae1 = AuditEntry.objects.get()

    assert ae1.author == admin_agent
    assert ae1.author_first_name == "Admin"
    assert ae1.author_last_name == "AGENT"
    assert ae1.author_email == "admin@agent.com"
    assert ae1.author_proconnect_sub == "admin"
    assert ae1.action_type == "pages"
    assert ae1.action_code == "section-removed"
    assert ae1.extra_data == {
        "section_page_id": str(page.id),
        "section_page_slug": page.slug,
        "section_slug": "declaration",
        "section_text": "# title\n\ntext",
        "section_order": 0,
        "section_title": "Déclaration",
    }
