import pytest
from django.contrib.auth.hashers import make_password

from ami.partner.models import Partner


@pytest.mark.django_db
def test_partner_has_password(settings):
    partner = Partner.objects.create(slug="new", name="New", consent_is_enabled=True)
    assert not partner.has_password()

    settings.PARTNERS_SECRETS = {"new": "plop"}
    assert partner.has_password()

    settings.PARTNERS_SECRETS = {}
    settings.PARTNERS_SECRET_HASHS = {"new": "<hash of plop>"}
    assert partner.has_password()


@pytest.mark.django_db
def test_partner_check_password(settings):
    partner = Partner.objects.create(slug="new", name="New", consent_is_enabled=True)
    settings.PARTNERS_SECRETS = {"new": "plop"}
    assert partner.check_password("plop")


@pytest.mark.django_db
def test_partner_check_password_secret_hash(settings):
    partner = Partner.objects.create(slug="new", name="New", consent_is_enabled=True)
    settings.PARTNERS_SECRET_HASHS = {"new": make_password("plop")}
    assert partner.check_password("plop")


def test_partner_is_ip_allowed():
    partner = Partner()
    partner.ip_allow_list = None
    assert partner.is_ip_allowed("198.51.100.12") is True
    partner.ip_allow_list = "# comment"
    assert partner.is_ip_allowed("198.51.100.12") is False
    partner.ip_allow_list = "198.51.100.12"
    assert partner.is_ip_allowed("198.51.100.12") is True
    partner.ip_allow_list = "198.51.100.0/24"
    assert partner.is_ip_allowed("198.51.100.12") is True
    partner.ip_allow_list = "203.0.113.0/24\n198.51.100.0/24"
    assert partner.is_ip_allowed("198.51.100.12") is True
