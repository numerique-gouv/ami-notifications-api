import pytest
from rest_framework.test import APIRequestFactory

from ami.partner.auth import AuthenticationFailed, PartnerBasicAuthentication
from ami.partner.models import Partner


@pytest.mark.django_db
def test_partner_authentication_success(settings, caplog):
    caplog.set_level("ERROR")

    partner = Partner.objects.create(
        slug="test", authentication_identifier="test", name="Partner", consent_is_enabled=True
    )
    settings.PARTNERS_SECRETS = {"test": "test"}
    request = APIRequestFactory().get("/")
    PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert getattr(request, "ami_partner") == partner
    assert not caplog.messages


@pytest.mark.django_db
def test_partner_authentication_unknown_partner(settings, caplog):
    caplog.set_level("ERROR")

    request = APIRequestFactory().get("/")
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert caplog.messages == ["API call with unknown partner authentication identifier"]


@pytest.mark.django_db
def test_partner_authentication_no_identifier(settings, caplog):
    caplog.set_level("ERROR")

    Partner.objects.create(
        slug="test", authentication_identifier="", name="Partner", consent_is_enabled=True
    )
    request = APIRequestFactory().get("/")
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("", "", request)
    assert caplog.messages == ["API call with empty partner authentication identifier"]


@pytest.mark.django_db
def test_partner_authentication_unconfigured_password(settings, caplog):
    caplog.set_level("ERROR")

    Partner.objects.create(
        slug="test", authentication_identifier="test", name="Partner", consent_is_enabled=True
    )
    request = APIRequestFactory().get("/")
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert caplog.messages == ["API call to unconfigured partner"]


@pytest.mark.django_db
def test_partner_authentication_wrong_password(settings, caplog):
    caplog.set_level("ERROR")

    Partner.objects.create(
        slug="test", authentication_identifier="test", name="Partner", consent_is_enabled=True
    )
    settings.PARTNERS_SECRETS = {"test": "test2"}
    request = APIRequestFactory().get("/")
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert caplog.messages == ["API call with invalid partner authentication password"]


@pytest.mark.django_db
def test_partner_authentication_ip_allow_list(settings, caplog):
    caplog.set_level("ERROR")

    partner = Partner.objects.create(
        slug="test", authentication_identifier="test", name="Partner", consent_is_enabled=True
    )
    settings.PARTNERS_SECRETS = {"test": "test"}

    request = APIRequestFactory().get("/")
    partner.ip_allow_list = "198.51.100.12"
    partner.save()
    caplog.clear()
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert caplog.messages == ["API call from invalid partner IP"]

    request = APIRequestFactory().get("/")
    partner.ip_allow_list = "127.0.0.1"
    partner.save()
    PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert getattr(request, "ami_partner") == partner


@pytest.mark.django_db
def test_partner_authentication_ip_allow_list_custom_header(settings, caplog):
    caplog.set_level("ERROR")

    partner = Partner.objects.create(
        slug="test", authentication_identifier="test", name="Partner", consent_is_enabled=True
    )
    settings.PARTNERS_SECRETS = {"test": "test"}

    settings.ORIGINATING_IP_ADDRESS_ENV = "HTTP_X_REAL_IP"

    request = APIRequestFactory().get("/")
    partner.ip_allow_list = "198.51.100.12"
    partner.save()
    caplog.clear()
    with pytest.raises(AuthenticationFailed):
        PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert caplog.messages == ["API call from invalid partner IP"]

    request = APIRequestFactory().get("/", headers={"X-Real-IP": "198.51.100.12"})
    partner.ip_allow_list = "198.51.100.12"
    partner.save()
    PartnerBasicAuthentication().authenticate_credentials("test", "test", request)
    assert getattr(request, "ami_partner") == partner
