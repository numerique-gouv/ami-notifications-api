import secrets

from drf_spectacular.authentication import BasicScheme
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from ami.partner.models import partners


class PartnerBasicAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request):  # type: ignore[reportIncompatibleMethodOverride]
        request.ami_partner = None
        partner = partners.get(userid)
        if not (partner and secrets.compare_digest(partner.secret, password)):
            raise AuthenticationFailed("Invalid username/password.")

        request.ami_partner = partner


class IsPartnerAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(getattr(request, "ami_partner", None))


class PartnerBasicScheme(BasicScheme):
    target_class = "ami.partner.auth.PartnerBasicAuthentication"
