import uuid

import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_admin_auth


@pytest.mark.django_db
def test_search_user(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    response = app.get("/agent-admin/manage/user/")
    assert "Gestion des usagers" in response


@pytest.mark.django_db
def test_search_user_without_agent_admin_auth(app) -> None:
    assert_query_fails_without_agent_admin_auth(app, "/agent-admin/manage/user/")


@pytest.mark.django_db
def test_detail_user(app, admin_agent: Agent):
    app.set_user(admin_agent.user)
    response = app.get(f"/agent-admin/manage/user/{uuid.uuid4()}/")
    assert "Gestion des usagers" in response


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
