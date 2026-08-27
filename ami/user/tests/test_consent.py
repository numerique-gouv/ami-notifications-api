import base64
import datetime

import pytest
from django.utils.timezone import now

from ami.partner.models import Partner
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import Consent, User


@pytest.mark.django_db
def test_get_consent(
    app,
    two_users: list[User],
    partner: Partner,
    partner_psl: Partner,
    partner_auth: dict[str, str],
) -> None:
    consent_datetime = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    Consent.objects.create(user=two_users[0], partner=partner, consent_datetime=consent_datetime)
    Consent.objects.create(user=two_users[0], partner=partner_psl, consent_datetime=now())
    Consent.objects.create(user=two_users[1], partner=partner, consent_datetime=now())

    response = app.get(f"/api/v1/consent/{two_users[0].fc_hash}", headers=partner_auth)
    assert response.status_code == 200
    assert response.json == {"consent_datetime": "2020-12-25T17:05:55Z"}


@pytest.mark.django_db
def test_get_consent_with_date_null(
    app,
    user: User,
    partner: Partner,
    partner_auth: dict[str, str],
) -> None:
    Consent.objects.create(user=user, partner=partner, consent_datetime=None)

    response = app.get(f"/api/v1/consent/{user.fc_hash}", headers=partner_auth, status=404)
    assert response.json == {"consent_datetime": None}


@pytest.mark.django_db
def test_get_consent_user_does_not_exist(
    app,
    partner_auth: dict[str, str],
) -> None:
    response = app.get("/api/v1/consent/unknown_hash", headers=partner_auth, status=404)
    assert response.status_code == 404
    assert response.json == {"consent_datetime": None}


@pytest.mark.django_db
def test_get_consent_user_has_not_consented(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    response = app.get(f"/api/v1/consent/{user.fc_hash}", headers=partner_auth, status=404)
    assert response.status_code == 404
    assert response.json == {"consent_datetime": None}


@pytest.mark.django_db
def test_get_consent_without_auth(app, settings, partner: Partner) -> None:
    response = app.get("/api/v1/consent/fake-fc-hash", status=401)
    assert response.json == {"detail": "Informations d'authentification non fournies."}

    response = app.get("/api/v1/consent/fake-fc-hash", headers={"authorization": "foo"}, status=401)
    assert response.json == {"detail": "Informations d'authentification non fournies."}

    response = app.get(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": "Foo bar"}, status=401
    )
    assert response.json == {"detail": "Informations d'authentification non fournies."}

    response = app.get(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": "Basic bar"}, status=401
    )
    assert response.json == {
        "detail": "En-tête « basic » non valide. Encodage base64 des informations d'identification incorrect."
    }

    b64 = base64.b64encode(f"foo:{settings.PARTNERS_DINUM_AMI_SECRET}".encode("utf8")).decode(
        "utf8"
    )
    response = app.get(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": f"Basic {b64}"}, status=401
    )
    assert response.json == {"detail": "Invalid username."}

    b64 = base64.b64encode("dinum-ami:foo".encode("utf8")).decode("utf8")
    response = app.get(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": f"Basic {b64}"}, status=401
    )
    assert response.json == {"detail": "Invalid username/password."}


@pytest.mark.django_db
def test_post_consent(
    app,
    two_users: list[User],
    partner: Partner,
    partner_psl: Partner,
    partner_auth: dict[str, str],
) -> None:
    Consent.objects.create(user=two_users[0], partner=partner_psl, consent_datetime=now())
    Consent.objects.create(user=two_users[1], partner=partner, consent_datetime=now())

    data = {"consent": True}
    response = app.post_json(f"/api/v1/consent/{two_users[0].fc_hash}", data, headers=partner_auth)
    assert response.json == {"message": "Consent given"}
    assert Consent.objects.count() == 3
    consent = Consent.objects.latest("created_at")
    assert consent.user == two_users[0]
    assert consent.partner == partner
    assert consent.consent_datetime is not None

    data = {"consent": False}
    response = app.post_json(f"/api/v1/consent/{two_users[0].fc_hash}", data, headers=partner_auth)
    assert response.json == {"message": "Consent withdrawn"}
    assert Consent.objects.count() == 3
    consent.refresh_from_db()
    assert consent.user == two_users[0]
    assert consent.partner == partner
    assert consent.consent_datetime is None


@pytest.mark.django_db
def test_post_consent_user_does_not_exist(
    app,
    partner_auth: dict[str, str],
) -> None:
    data = {"consent": True}
    response = app.post_json("/api/v1/consent/unknown_hash", data, headers=partner_auth)
    assert response.json == {"message": "Consent given"}
    assert User.objects.count() == 1
    user = User.objects.get()
    assert user.fc_hash == "unknown_hash"
    assert user.last_logged_in is None
    assert Consent.objects.count() == 1
    consent = Consent.objects.get()
    assert consent.user == user
    assert consent.consent_datetime is not None

    data = {"consent": False}
    response = app.post_json("/api/v1/consent/unknown_hash", data, headers=partner_auth)
    assert response.json == {"message": "Consent withdrawn"}
    assert Consent.objects.count() == 1
    consent.refresh_from_db()
    assert consent.consent_datetime is None


@pytest.mark.django_db
def test_post_consent_user_consent_invalid(
    app,
    partner_auth: dict[str, str],
) -> None:
    data = {}
    response = app.post_json("/api/v1/consent/unknown_hash", data, headers=partner_auth, status=400)
    assert response.json == {"consent": ["Ce champ est obligatoire."]}
    assert Consent.objects.count() == 0
    assert User.objects.count() == 0

    data = {"consent": "invalid"}
    response = app.post_json("/api/v1/consent/unknown_hash", data, headers=partner_auth, status=400)
    assert response.json == {"consent": ["Must be a valid boolean."]}
    assert Consent.objects.count() == 0
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_post_consent_without_auth(app, settings, partner: Partner) -> None:
    response = app.post("/api/v1/consent/fake-fc-hash", status=401)
    assert response.json == {"detail": "Informations d'authentification non fournies."}

    response = app.post(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": "foo"}, status=401
    )
    assert response.json == {"detail": "Informations d'authentification non fournies."}

    response = app.post(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": "Foo bar"}, status=401
    )
    assert response.json == {"detail": "Informations d'authentification non fournies."}

    response = app.post(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": "Basic bar"}, status=401
    )
    assert response.json == {
        "detail": "En-tête « basic » non valide. Encodage base64 des informations d'identification incorrect."
    }

    b64 = base64.b64encode(f"foo:{settings.PARTNERS_DINUM_AMI_SECRET}".encode("utf8")).decode(
        "utf8"
    )
    response = app.post(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": f"Basic {b64}"}, status=401
    )
    assert response.json == {"detail": "Invalid username."}

    b64 = base64.b64encode("dinum-ami:foo".encode("utf8")).decode("utf8")
    response = app.post(
        "/api/v1/consent/fake-fc-hash", headers={"authorization": f"Basic {b64}"}, status=401
    )
    assert response.json == {"detail": "Invalid username/password."}


@pytest.mark.django_db
def test_get_consents(app, user: User, partner_psl: Partner) -> None:
    login(app, user)

    consent_datetime = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    consent = Consent.objects.create(
        user=user, partner=partner_psl, consent_datetime=consent_datetime
    )

    response = app.get("/api/v1/users/consents", status=200)
    consents = response.json
    assert len(consents) == 1
    assert set(response.json[0].keys()) == {"consent_datetime", "id", "partner_id"}
    assert response.json[0]["id"] == str(consent.id)
    assert response.json[0]["partner_id"] == consent.partner.slug
    assert response.json[0]["consent_datetime"] == "2020-12-25T17:05:55Z"


@pytest.mark.django_db
def test_get_consents_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/consents")


@pytest.mark.django_db
def test_post_consents(
    app,
    two_users: list[User],
    partner: Partner,
    partner_psl: Partner,
) -> None:
    login(app, two_users[0])

    Consent.objects.create(user=two_users[0], partner=partner_psl, consent_datetime=now())
    Consent.objects.create(user=two_users[1], partner=partner, consent_datetime=now())

    data = {"partner_id": "dinum-ami", "consent": True}
    response = app.post_json("/api/v1/users/consents", data)
    assert response.json == {"message": "Consent given"}
    assert Consent.objects.count() == 3
    consent = Consent.objects.latest("created_at")
    assert consent.user == two_users[0]
    assert consent.partner == partner
    assert consent.consent_datetime is not None

    data = {"partner_id": "dinum-ami", "consent": False}
    response = app.post_json("/api/v1/users/consents", data)
    assert response.json == {"message": "Consent withdrawn"}
    assert Consent.objects.count() == 3
    consent.refresh_from_db()
    assert consent.user == two_users[0]
    assert consent.partner == partner
    assert consent.consent_datetime is None


@pytest.mark.django_db
def test_post_consents_user_consent_invalid(
    app,
    user: User,
    partner: Partner,
) -> None:
    login(app, user)

    data = {"partner_id": "dinum-ami"}
    response = app.post_json("/api/v1/users/consents", data, status=400)
    assert response.json == {"consent": ["Ce champ est obligatoire."]}
    assert Consent.objects.count() == 0
    assert User.objects.count() == 1

    data = {"partner_id": "dinum-ami", "consent": "invalid"}
    response = app.post_json("/api/v1/users/consents", data, status=400)
    assert response.json == {"consent": ["Must be a valid boolean."]}
    assert Consent.objects.count() == 0
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_post_consents_user_partner_id_unknown(
    app,
    user: User,
) -> None:
    login(app, user)

    data = {"partner_id": "unknown", "consent": True}
    response = app.post_json("/api/v1/users/consents", data, status=400)
    assert response.json == {"partner_id": ["'partner_id' inconnu."]}
    assert Consent.objects.count() == 0
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_post_consents_without_auth(app, settings) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/consents", method="post")
