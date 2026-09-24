import pytest

from ami.checklist.models import CheckList
from ami.partner.models import Partner
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_checklist(app, user: User, partner_psl: Partner):
    login(app, user)

    CheckList.objects.create(
        partner=partner_psl,
        external_id="F16225",
        title="Je deviens parent",
        icon="icon",
        definition={
            "title": "Je deviens parent",
            "sections": [
                {"title": "Pendant la grossesse", "id": "pendant-la-grossesse"},
            ],
            "items": [
                {
                    "text": "**Avant la fin du 3e mois** de grossesse : passer le **1<sup>er</sup> examen prénatal**, "
                    "qui permet de faire la **déclaration de grossesse**",
                    "id": "e59ab105e3f3",
                    "section": "pendant-la-grossesse",
                },
            ],
        },
    )

    response = app.get("/api/v1/users/data/checklist/F16225")
    assert response.json == {
        "icon": "icon",
        "definition": {
            "title": "Je deviens parent",
            "sections": [
                {"title": "Pendant la grossesse", "id": "pendant-la-grossesse"},
            ],
            "items": [
                {
                    "text": "**Avant la fin du 3e mois** de grossesse : passer le **1<sup>er</sup> examen prénatal**, "
                    "qui permet de faire la **déclaration de grossesse**",
                    "id": "e59ab105e3f3",
                    "section": "pendant-la-grossesse",
                },
            ],
        },
    }


@pytest.mark.django_db
def test_get_checklist_not_found(app, user: User):
    login(app, user)

    app.get("/api/v1/users/data/checklist/F3109", status=404)


@pytest.mark.django_db
def test_get_checklist_without_auth(app, partner_psl: Partner):
    CheckList.objects.create(
        partner=partner_psl,
        external_id="F16225",
        title="Je deviens parent",
        definition={"title": "Je deviens parent"},
    )
    assert_query_fails_without_auth(app, "/api/v1/users/data/checklist/F16225")
