import pytest
from django.test import RequestFactory

from ami.partner.auth import AuthenticationFailed, PartnerBasicAuthentication
from ami.partner.models import Partner


@pytest.mark.django_db
def test_basic_authentication(settings):
    request = RequestFactory().get("/")
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)

    partner = Partner.objects.create(slug="test", name="Partner", consent_is_enabled=True)
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)

    request = RequestFactory().get("/")
    settings.PARTNERS_SECRETS = {"test": "test"}
    PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert getattr(request, "ami_partner") == partner

    request = RequestFactory().get("/")
    partner.ip_allow_list = "198.51.100.12"
    partner.save()
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)

    request = RequestFactory().get("/")
    partner.ip_allow_list = "127.0.0.1"
    partner.save()
    PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert getattr(request, "ami_partner") == partner

    settings.ORIGINATING_IP_ADDRESS_ENV = "HTTP_X_REAL_IP"
    request = RequestFactory().get("/", headers={"X-Real-IP": "198.51.100.12"})
    partner.ip_allow_list = "198.51.100.12"
    partner.save()
    PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert getattr(request, "ami_partner") == partner
