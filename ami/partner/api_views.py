from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from ami.authentication.decorators import ami_login_required
from ami.utils import generate_identity_token


@extend_schema(
    responses=inline_serializer("PartnerUrlResponse", {"partner_url": serializers.CharField()})
)
@api_view(["GET"])
@ami_login_required
def generate_partner_url(request):
    preferred_username = request.query_params.get("preferred_username", "")
    email = request.query_params.get("email", "")
    address_city = request.query_params.get("address_city", "")
    address_postcode = request.query_params.get("address_postcode", "")
    address_name = request.query_params.get("address_name", "")
    current_user = request.ami_user

    partner_url = settings.CONFIG["PARTNERS_PSL_OTV_REQUEST_URL"]

    if partner_url.endswith("caller={token-jwt}"):
        otv_private_key = settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PFX_B64"]
        psl_otv_public_key = settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"]
        if otv_private_key and psl_otv_public_key:
            identity_token = generate_identity_token(
                preferred_username or "",
                email or "",
                address_city or "",
                address_postcode or "",
                address_name or "",
                current_user.fc_hash,
            )
            partner_url = partner_url.replace("{token-jwt}", identity_token)
        else:
            partner_url = partner_url.replace("caller={token-jwt}", "")

    return Response(
        data={"partner_url": partner_url},
        status=HTTP_200_OK,
    )


@extend_schema(
    responses=inline_serializer("PartnerPublicKeyResponse", {"public_key": serializers.CharField()})
)
@api_view(["GET"])
def get_partner_public_key(request) -> Response[dict[str, str]]:
    public_key = settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PUBLIC_KEY"]

    return Response(
        data={"public_key": public_key},
        status=HTTP_200_OK,
    )
