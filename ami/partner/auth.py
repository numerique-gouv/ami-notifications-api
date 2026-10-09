import logging
import secrets

import sentry_sdk
from django.conf import settings
from drf_spectacular.authentication import BasicScheme
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from ami.partner.models import Partner

logger = logging.getLogger(__name__)


class PartnerBasicAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request):  # type: ignore[reportIncompatibleMethodOverride]
        request.ami_partner = None
        if not userid:
            bad_auth = True
            partner = Partner()
            logger.error("API call with empty partner authentication identifier")
        else:
            try:
                partner = Partner.objects.get(authentication_identifier=userid)
            except Partner.DoesNotExist:
                logger.error("API call with unknown partner authentication identifier")
                partner = Partner()
                bad_auth = True
            else:
                if not partner.secret:
                    bad_auth = True
                    logger.error("API call to unconfigured partner")
                else:
                    bad_auth = not secrets.compare_digest(partner.secret, password)
                    if bad_auth:
                        logger.error("API call with invalid partner authentication password")

        if not bad_auth:
            origin_ip = request.META.get(settings.ORIGINATING_IP_ADDRESS_ENV)

            sentry_sdk.set_tag("ami.partner_id", str(partner.id))
            sentry_sdk.set_tag("ami.partner_slug", partner.slug)
            sentry_sdk.set_tag("ami.partner_ip", origin_ip)

            if not partner.is_ip_allowed(origin_ip):
                logger.error("API call from invalid partner IP")
                bad_auth = True

        if bad_auth:
            raise AuthenticationFailed("Invalid authentication credentials")

        request.ami_partner = partner


class IsPartnerAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(getattr(request, "ami_partner", None))


class PartnerBasicScheme(BasicScheme):
    target_class = "ami.partner.auth.PartnerBasicAuthentication"
