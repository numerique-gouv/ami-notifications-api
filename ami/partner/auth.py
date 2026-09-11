import secrets

from django.conf import settings
from drf_spectacular.authentication import BasicScheme
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from ami.partner.models import Partner


class PartnerBasicAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request):  # type: ignore[reportIncompatibleMethodOverride]
        request.ami_partner = None
        try:
            partner = Partner.objects.get(slug=userid)
        except Partner.DoesNotExist:
            raise AuthenticationFailed("Invalid username.")
        if not secrets.compare_digest(partner.secret, password):
            raise AuthenticationFailed("Invalid username/password.")

        if not partner.is_ip_allowed(request.environ.get(settings.ORIGINATING_IP_ADDRESS_ENV)):
            raise AuthenticationFailed("Invalid source IP")

        request.ami_partner = partner


class IsPartnerAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(getattr(request, "ami_partner", None))


class PartnerBasicScheme(BasicScheme):
    target_class = "ami.partner.auth.PartnerBasicAuthentication"
