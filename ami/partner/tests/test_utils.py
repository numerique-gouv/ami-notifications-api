import pytest

from ami.partner.models import Partner
from ami.partner.utils import is_allowed_url


@pytest.mark.django_db
def test_is_allowed_url(partner, partner_dn):
    Partner.objects.exclude(slug__in=[partner.slug, partner_dn.slug]).delete()
    partner.trusted_base_uris = "https://example.org/test/"
    partner.save()
    partner_dn.trusted_base_uris = "https://example.net"
    partner_dn.save()
    assert not is_allowed_url("https://example.com/")
    assert is_allowed_url("https://example.org/test/")
    assert is_allowed_url("https://example.org/test/2/")
    assert is_allowed_url("https://example.net/test")


@pytest.mark.django_db
def test_is_allowed_url_empty(partner, partner_dn):
    partner.trusted_base_uris = "https://example.org/test/"
    partner.save()
    assert is_allowed_url("https://example.org")


@pytest.mark.django_db
def test_is_allowed_url_when_no_partner():
    assert is_allowed_url("https://example.org")
