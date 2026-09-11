import pytest

from ami.partner.models import Partner


@pytest.mark.django_db
def test_partner_secret():
    partner = Partner.objects.create(slug="new", name="New", consent_is_enabled=True)
    assert partner.secret == ""  # no error


def test_partnet_is_ip_allowed():
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
