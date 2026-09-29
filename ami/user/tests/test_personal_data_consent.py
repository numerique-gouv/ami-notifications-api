import datetime

import pytest
from django.utils.timezone import now

from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import PersonalDataConsent, User


@pytest.mark.django_db
def test_get_personal_data_consent(app, user: User) -> None:
    login(app, user)

    consent_datetime = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    personal_data_consent = PersonalDataConsent.objects.create(
        user=user, consent_datetime=consent_datetime
    )

    response = app.get("/api/v1/users/personal-data-consent", status=200)
    assert set(response.json.keys()) == {"consent_datetime", "id"}
    assert response.json["id"] == str(personal_data_consent.id)
    assert response.json["consent_datetime"] == "2020-12-25T17:05:55Z"


@pytest.mark.django_db
def test_get_personal_data_consent_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/personal-data-consent")


@pytest.mark.django_db
def test_post_personal_data_consent(app, two_users: list[User]) -> None:
    login(app, two_users[0])

    PersonalDataConsent.objects.create(user=two_users[0], consent_datetime=None)
    PersonalDataConsent.objects.create(user=two_users[1], consent_datetime=now())

    data = {"consent": True}
    response = app.post_json("/api/v1/users/personal-data-consent", data)
    assert response.json == {"message": "Personal data consent given"}
    assert PersonalDataConsent.objects.count() == 2
    personal_data_consent = PersonalDataConsent.objects.latest("updated_at")
    assert personal_data_consent.user == two_users[0]
    assert personal_data_consent.consent_datetime is not None

    data = {"consent": False}
    response = app.post_json("/api/v1/users/personal-data-consent", data)
    assert response.json == {"message": "Personal data consent withdrawn"}
    assert PersonalDataConsent.objects.count() == 2
    personal_data_consent.refresh_from_db()
    assert personal_data_consent.user == two_users[0]
    assert personal_data_consent.consent_datetime is None


@pytest.mark.django_db
def test_post_personal_data_consent_user_consent_invalid(app, user: User) -> None:
    login(app, user)

    data = {}
    response = app.post_json("/api/v1/users/personal-data-consent", data, status=400)
    assert response.json == {"consent": ["Ce champ est obligatoire."]}
    assert PersonalDataConsent.objects.count() == 0
    assert User.objects.count() == 1

    data = {"consent": "invalid"}
    response = app.post_json("/api/v1/users/personal-data-consent", data, status=400)
    assert response.json == {"consent": ["Doit être un booléen valide."]}
    assert PersonalDataConsent.objects.count() == 0
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_post_personal_data_consent_without_auth(app, settings) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/personal-data-consent", method="post")
