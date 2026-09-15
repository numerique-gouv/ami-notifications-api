import pytest

from ami.page.models import Page, Section
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_page(app, user: User):
    login(app, user)

    page = Page.objects.create(title="Accessibilité", slug="accessibilite")
    Section.objects.create(
        title="Déclaration", slug="declaration", page=page, order=0, text="# title\n\ntext"
    )
    Section.objects.create(title="Recours", slug="recours", page=page, order=1)

    response = app.get("/api/v1/page/accessibilite", status=200)
    assert response.json == {
        "slug": "accessibilite",
        "title": "Accessibilité",
        "sections": [
            {"slug": "declaration", "title": "Déclaration", "text": "# title\n\ntext"},
            {"slug": "recours", "title": "Recours", "text": ""},
        ],
    }


@pytest.mark.django_db
def test_get_page_without_auth(app, user: User):
    Page.objects.create(title="Accessibilité", slug="accessibilite")
    assert_query_fails_without_auth(app, "/api/v1/page/accessibilite")
