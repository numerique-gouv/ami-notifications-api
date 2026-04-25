import uuid

import pytest
from django.utils.formats import date_format

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth
from ami.user.models import User


@pytest.mark.django_db
def test_search_user(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/user/")
    assert "Gestion des usagers" in response


@pytest.mark.django_db
def test_search_user_submit_user_not_found(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/user/")
    response.forms["search-user"]["fc_hash"] = "unknown"
    response = response.forms["search-user"].submit()
    assert response.forms["search-user"]["fc_hash"].value == "unknown"
    assert response.context["form"].errors == {"fc_hash": ["Utilisateur non trouvé"]}


@pytest.mark.django_db
def test_search_user_submit_success(app, admin_agent: Agent, user: User):
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/user/")
    response.forms["search-user"]["fc_hash"] = user.fc_hash
    response = response.forms["search-user"].submit()
    assert f"/agent-admin/manage/user/{user.id}/" in response.headers["location"]


@pytest.mark.django_db
def test_search_user_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/user/")


@pytest.mark.django_db
def test_detail_user(app, admin_agent: Agent, user: User):
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/user/{user.id}/")
    assert "Gestion des usagers" in response
    assert response.forms["search-user"]["fc_hash"].value == user.fc_hash
    assert response.forms["search-user"].action == "/agent-admin/manage/user/"
    last_logged_in = date_format(user.last_logged_in, "d/m/Y à H\\Hi")
    assert response.pyquery("p.user-details").text() == f"dernier login\xa0:\n{last_logged_in}"


@pytest.mark.django_db
def test_detail_user_never_seen(app, admin_agent: Agent, never_seen_user: User):
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/user/{never_seen_user.id}/")
    assert "Gestion des usagers" in response
    assert response.forms["search-user"]["fc_hash"].value == never_seen_user.fc_hash
    assert response.forms["search-user"].action == "/agent-admin/manage/user/"
    assert response.pyquery("p.user-details").text() == "dernier login\xa0:\nnon inscrit"


@pytest.mark.django_db
def test_detail_user_not_found(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    app.get(f"/agent-admin/manage/user/{uuid.uuid4()}/", status=404)


@pytest.mark.django_db
def test_detail_user_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(
        app, f"/agent-admin/manage/user/{uuid.uuid4()}/delete/"
    )


@pytest.mark.django_db
def test_delete_user(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    response = app.post(f"/agent-admin/manage/user/{uuid.uuid4()}/delete/")
    assert "/agent-admin/manage/user/" in response.headers["location"]

    app.get(f"/agent-admin/manage/user/{uuid.uuid4()}/delete/", status=405)


@pytest.mark.django_db
def test_delete_user_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(
        app, f"/agent-admin/manage/user/{uuid.uuid4()}/delete/", method="post"
    )
