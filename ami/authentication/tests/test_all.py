import datetime
from base64 import urlsafe_b64encode

import pytest

from ami.authentication.auth import generate_nonce, get_fc_scope


def test_generate_nonce(monkeypatch: pytest.MonkeyPatch) -> None:
    FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)
    FAKE_UUID = "fake-uuid"

    monkeypatch.setattr("ami.authentication.auth.uuid4", lambda: FAKE_UUID)
    monkeypatch.setattr("ami.authentication.auth.now", lambda: FAKE_TIME)
    assert generate_nonce() == urlsafe_b64encode(f"{FAKE_UUID}-{FAKE_TIME}".encode("utf8")).decode(
        "utf8"
    )


def test_get_fc_scope(settings) -> None:
    settings.API_PARTICULIER_QUOTIENT_ENABLED = False
    settings.API_PARTICULIER_STATUT_ETUDIANT_ENABLED = False

    assert get_fc_scope([]) == settings.FC_SCOPE
    assert get_fc_scope(["foo"]) == settings.FC_SCOPE
    assert get_fc_scope(["api_particulier_quotient"]) == settings.FC_SCOPE
    assert get_fc_scope(["api_particulier_statut_etudiant"]) == settings.FC_SCOPE

    settings.API_PARTICULIER_QUOTIENT_ENABLED = True
    settings.API_PARTICULIER_STATUT_ETUDIANT_ENABLED = True

    assert get_fc_scope([]) == settings.FC_SCOPE
    assert get_fc_scope(["foo"]) == settings.FC_SCOPE
    assert (
        get_fc_scope(["api_particulier_quotient"])
        == f"{settings.FC_SCOPE} {settings.API_PARTICULIER_QUOTIENT_SCOPE}"
    )
    assert (
        get_fc_scope(["api_particulier_statut_etudiant"])
        == f"{settings.FC_SCOPE} {settings.API_PARTICULIER_STATUT_ETUDIANT_SCOPE}"
    )
    assert (
        get_fc_scope(["foo", "api_particulier_quotient", "api_particulier_statut_etudiant"])
        == f"{settings.FC_SCOPE} {settings.API_PARTICULIER_QUOTIENT_SCOPE} {settings.API_PARTICULIER_STATUT_ETUDIANT_SCOPE}"
    )
