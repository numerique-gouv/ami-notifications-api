import pytest

from ami.partner.models import Partner


@pytest.mark.django_db
def test_partner_secret():
    partner = Partner.objects.create(slug="new", name="New", consent_is_enabled=True)
    assert partner.secret == ""  # no error
