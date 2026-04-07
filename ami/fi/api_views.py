import logging
import re
from secrets import token_urlsafe
from typing import cast

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.fi.api_exceptions import (
    FISessionExpired,
    FISessionNotFound,
    MissingAuthHeader,
    WrongFormatAuthHeader,
)
from ami.fi.models import FISession
from ami.fi.serializers import TokenSerializer
from ami.fi.utils import generate_id_token

logger = logging.getLogger(__name__)


@api_view(["GET"])
def authorize(request: Request) -> Response:
    return Response()


@api_view(["POST"])
def token(request: Request) -> JsonResponse:
    serializer = TokenSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as e:
        logging.exception(e)
        raise
    data: dict = cast(dict, serializer.validated_data)

    try:
        fi_session = FISession.objects.get(code=data["code"])
        if fi_session.is_expired:
            logger.error("Session de connexion à AMI-FI expirée")
            raise FISessionExpired
    except FISession.DoesNotExist:
        logger.error("Session de connexion à AMI-FI non trouvée")
        raise FISessionNotFound

    encoded_id_token = jwt.encode(
        generate_id_token(fi_session),
        data["client_secret"],
        algorithm="HS256",
    )

    access_token = token_urlsafe(64)
    fi_session.access_token = make_password(access_token, settings.FI_HASH_SALT)
    fi_session.save()

    return JsonResponse(
        {
            "access_token": access_token,
            "expires_in": 60,
            "id_token": encoded_id_token,
            "token_type": "Bearer",
        }
    )


@api_view(["GET"])
def userinfo(request: Request) -> JsonResponse:
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    if not auth_header:
        logger.error("Header d'authentification manquant")
        raise MissingAuthHeader

    pattern = re.compile(r"^Bearer\s([A-Z-a-z-0-9-_/-]+)$")
    if not pattern.match(auth_header):
        logger.error("Header d'authentification mal formé")
        raise WrongFormatAuthHeader

    auth_token = auth_header[7:]
    auth_token_hash = make_password(auth_token, settings.FI_HASH_SALT)
    try:
        fi_session = FISession.objects.get(access_token=auth_token_hash)
        if fi_session.is_expired:
            logger.error("Session de connexion à AMI-FI expirée")
            raise FISessionExpired
    except FISession.DoesNotExist:
        logger.error("Session de connexion à AMI-FI non trouvée")
        raise FISessionNotFound

    return JsonResponse(fi_session.user_data)


@api_view(["GET"])
def logout(request: Request) -> HttpResponseBadRequest | HttpResponseRedirect:
    redirect_uri = request.GET.get("post_logout_redirect_uri")
    if redirect_uri != f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_LOGOUT_CALLBACK_ENDPOINT}":
        return HttpResponseBadRequest()

    redirect_uri = f"{redirect_uri}?state={request.GET.get('state')}"

    return redirect(redirect_uri)
