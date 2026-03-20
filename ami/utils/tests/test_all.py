from typing import Any

from django.conf import settings
from pytest_httpx import HTTPXMock


def test_ping(django_app) -> None:
    response = django_app.head("/ping")
    assert response.status_code == 200


def test_get_sector_identifier_url(
    django_app,
) -> None:
    settings.CONFIG["PUBLIC_SECTOR_IDENTIFIER_URL"] = "http://example.com\nhttp://foobar.com"
    response = django_app.get("/sector_identifier_url")
    assert response.status_code == 200
    assert response.json == ["http://example.com", "http://foobar.com"]


def test_recipient_fc_hash(django_app) -> None:
    params = {
        "given_name": "Angela Claire Louise",
        "family_name": "DUBOIS",
        "birthdate": "1962-08-24",
        "gender": "female",
        "birthplace": "75107",
        "birthcountry": "99100",
    }
    response = django_app.get("/dev-utils/recipient-fc-hash", params=params)
    assert response.text == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"

    params.pop("birthplace")
    response = django_app.get("/dev-utils/recipient-fc-hash", params=params)
    assert response.text == "7e74df2cbebae761eccedbc24b7fe589bb83137f7808a2930031f52c73d75efe"


def test_review_apps(django_app, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls?state=open&sort=created&per_page=100",
        json=TRUNCATED_GITHUB_JSON_RESPONSE,
    )
    response = django_app.get("/dev-utils/review-apps")
    json_data = response.json
    assert len(json_data) == 2  # Staging + the PR returned in GITHUB_JSON_RESPONSE
    assert json_data[0]["title"] == "Staging"


def test_review_apps_github_failure(django_app, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls?state=open&sort=created&per_page=100",
        status_code=400,
    )
    response = django_app.get("/dev-utils/review-apps")
    json_data = response.json
    assert len(json_data) == 1  # Only the hardcoded Staging
    assert json_data[0]["title"] == "Staging"


TRUNCATED_GITHUB_JSON_RESPONSE: list[dict[str, Any]] = [
    {
        "url": "https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls/83",
        "id": 2759929411,
        "node_id": "PR_kwDOOSMCFs6kgS5D",
        "html_url": "https://github.com/numerique-gouv/ami-notifications-api/pull/83",
        "diff_url": "https://github.com/numerique-gouv/ami-notifications-api/pull/83.diff",
        "patch_url": "https://github.com/numerique-gouv/ami-notifications-api/pull/83.patch",
        "issue_url": "https://api.github.com/repos/numerique-gouv/ami-notifications-api/issues/83",
        "number": 83,
        "state": "open",
        "locked": False,
        "title": "Donne la possibilité d'avoir des noms de fichiers et non les valeurs …",
        "user": {},
        "body": "…dans les variables d'environnement de clé.",
        "created_at": "2025-08-20T14:00:11Z",
        "updated_at": "2025-08-27T13:14:35Z",
        "closed_at": None,
        "merged_at": None,
        "merge_commit_sha": None,
        "assignee": None,
        "assignees": [],
        "requested_reviewers": [],
        "requested_teams": [],
        "labels": [],
        "milestone": None,
        "draft": False,
        "commits_url": "https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls/83/commits",
        "review_comments_url": "https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls/83/comments",
        "review_comment_url": "https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls/comments{/number}",
        "comments_url": "https://api.github.com/repos/numerique-gouv/ami-notifications-api/issues/83/comments",
        "statuses_url": "https://api.github.com/repos/numerique-gouv/ami-notifications-api/statuses/b9c987327a8f8e45648c1508faacf062637584c6",
        "head": {},
        "base": {},
        "_links": {},
        "author_association": "COLLABORATOR",
        "auto_merge": None,
        "active_lock_reason": None,
    },
]
