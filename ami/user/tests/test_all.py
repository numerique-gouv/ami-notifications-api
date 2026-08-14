import base64
import datetime

import pytest
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import Consent, User


@pytest.mark.django_db
def test_get_consent(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    consent_datetime = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    Consent.objects.create(user=user, partner_id="psl", consent_datetime=consent_datetime)

    response = app.get(f"/api/v1/consent/{user.fc_hash}", headers=partner_auth)
    assert response.status_code == 200
    assert response.json == {"consent_datetime": "2020-12-25T17:05:55Z"}


@pytest.mark.django_db
def test_get_consent_with_date_null(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    consent_datetime = None
    Consent.objects.create(user=user, partner_id="psl", consent_datetime=consent_datetime)

    response = app.get(f"/api/v1/consent/{user.fc_hash}", headers=partner_auth, status=404)
    assert response.json == {"consent_datetime": "null"}


@pytest.mark.django_db
def test_get_consent_user_does_not_exist(
    app,
    partner_auth: dict[str, str],
) -> None:
    response = app.get("/api/v1/consent/fake-fc-hash", headers=partner_auth, status=404)
    assert response.status_code == 404
    assert response.json == {"consent_datetime": "null"}


@pytest.mark.django_db
def test_get_consent_user_has_not_consented(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    response = app.get(f"/api/v1/consent/{user.fc_hash}", headers=partner_auth, status=404)
    assert response.status_code == 404
    assert response.json == {"consent_datetime": "null"}


@pytest.mark.django_db
def test_get_consent_without_auth(app, settings) -> None:
    app.put("/api/v1/consent/fake-fc-hash", status=401)

    app.put("/api/v1/consent/fake-fc-hash", headers={"authorization": "foo"}, status=401)

    app.put("/api/v1/consent/fake-fc-hash", headers={"authorization": "Foo bar"}, status=401)

    app.put("/api/v1/consent/fake-fc-hash", headers={"authorization": "Basic bar"}, status=401)

    b64 = base64.b64encode(f"foo:{settings.PARTNERS_PSL_SECRET}".encode("utf8")).decode("utf8")
    app.put("/api/v1/consent/fake-fc-hash", headers={"authorization": f"Basic {b64}"}, status=401)

    b64 = base64.b64encode("psl:foo".encode("utf8")).decode("utf8")
    app.put("/api/v1/consent/fake-fc-hash", headers={"authorization": f"Basic {b64}"}, status=401)


@pytest.mark.django_db
def test_list_consents(app, user: User) -> None:
    login(app, user)

    consent_datetime = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    consent = Consent.objects.create(user=user, partner_id="psl", consent_datetime=consent_datetime)

    response = app.get("/api/v1/users/consents", status=200)
    consents = response.json
    assert len(consents) == 1
    assert set(response.json[0].keys()) == {"consent_datetime", "id", "partner_id", "user_id"}
    assert response.json[0]["id"] == str(consent.id)
    assert response.json[0]["user_id"] == str(consent.user.id)
    assert response.json[0]["partner_id"] == consent.partner_id
    assert response.json[0]["consent_datetime"] == "2020-12-25T17:05:55Z"


@pytest.mark.django_db
def test_list_consents_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/consents")


@pytest.mark.django_db
def test_consents_update_consent_datetime(
    user: User,
    app,
) -> None:
    login(app, user)

    consent_datetime_1 = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    consent_1 = Consent.objects.create(
        user=user, partner_id="psl", consent_datetime=consent_datetime_1
    )

    consent_datetime_2 = datetime.datetime(2020, 12, 26, 17, 5, 55, tzinfo=datetime.timezone.utc)
    consent_2 = Consent.objects.create(
        user=user, partner_id="dinum-rdvsp", consent_datetime=consent_datetime_2
    )

    expected_consent_datetime = datetime.datetime(
        2026, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc
    )
    payload = {
        "partner_id": "psl",
        "consent_datetime": "2026-12-25T17:05:55Z",
    }
    response = app.post("/api/v1/users/consents", payload)

    assert response.status_code == HTTP_200_OK
    consent_1.refresh_from_db()
    consent_2.refresh_from_db()
    assert consent_1.consent_datetime == expected_consent_datetime
    assert consent_2.consent_datetime == consent_datetime_2


@pytest.mark.django_db
def test_consents_create_consent_datetime_when_user_exists(
    user: User,
    app,
) -> None:
    login(app, user)

    consent_datetime_1 = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    Consent.objects.create(user=user, partner_id="psl", consent_datetime=consent_datetime_1)

    consent_datetime_2 = datetime.datetime(2020, 12, 26, 17, 5, 55, tzinfo=datetime.timezone.utc)
    Consent.objects.create(user=user, partner_id="dinum-rdvsp", consent_datetime=consent_datetime_2)

    expected_consent_datetime = datetime.datetime(
        2026, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc
    )
    payload = {
        "partner_id": "dinum-dn",
        "consent_datetime": "2026-12-25T17:05:55Z",
    }
    response = app.post("/api/v1/users/consents", payload)

    assert response.status_code == HTTP_201_CREATED
    consents = Consent.objects.all()
    assert len(consents) == 3
    assert consents[0].consent_datetime == consent_datetime_1
    assert consents[1].consent_datetime == consent_datetime_2
    assert consents[2].consent_datetime == expected_consent_datetime


@pytest.mark.django_db
def test_consents_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/consents", method="post")
