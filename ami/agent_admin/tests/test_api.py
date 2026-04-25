import pytest

from ami.agent.models import Agent
from ami.agent_admin.tests.utils import assert_query_fails_without_agent_notifications_auth
from ami.user.models import User


@pytest.mark.django_db
def test_list_users(app, notifications_agent: Agent) -> None:
    app.set_user(notifications_agent.user)

    response = app.get("/agent-admin/api/users/")
    assert response.json == {"data": []}

    response = app.get("/agent-admin/api/users/", params={"q": "abc"})
    assert response.json == {"data": []}

    for i in range(20):
        User.objects.create(fc_hash="abcdefghijklmnopqrstuvwxyz"[: i + 1])

    response = app.get("/agent-admin/api/users/", params={"q": "abc"})
    assert response.json == {
        "data": [
            {"value": "abc"},
            {"value": "abcd"},
            {"value": "abcde"},
            {"value": "abcdef"},
            {"value": "abcdefg"},
            {"value": "abcdefgh"},
            {"value": "abcdefghi"},
            {"value": "abcdefghij"},
            {"value": "abcdefghijk"},
            {"value": "abcdefghijkl"},
        ]
    }


@pytest.mark.django_db
def test_list_users_without_agent_notifications_auth(app) -> None:
    assert_query_fails_without_agent_notifications_auth(app, "/agent-admin/api/users/")
