import base64
import datetime

import pytest

from ami.user.models import User


@pytest.mark.django_db
def test_get_consent(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    user.consent_datetime = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    user.save()

    response = app.get(f"/api/v1/consent/{user.fc_hash}", headers=partner_auth)
    assert response.status_code == 200
    assert response.json == {"Consent": "OK"}


@pytest.mark.django_db
def test_get_consent_user_does_not_exist(
    app,
    partner_auth: dict[str, str],
) -> None:
    response = app.get("/api/v1/consent/fake-fc-hash", headers=partner_auth, status=404)
    assert response.status_code == 404
    assert response.json == {"detail": "No User matches the given query."}


@pytest.mark.django_db
def test_get_consent_user_has_not_consented(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    response = app.get(f"/api/v1/consent/{user.fc_hash}", headers=partner_auth, status=404)
    assert response.status_code == 404
    assert response.json == {"detail": "No User matches the given query."}


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
