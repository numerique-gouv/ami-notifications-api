import base64
import json
import logging
import re
import uuid
from secrets import token_urlsafe
from typing import cast
from urllib.parse import urlencode, urlparse

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core import signing
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.exceptions import InvalidAuthenticationResponse, InvalidRegistrationResponse
from webauthn.helpers.structs import (
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
)

from ami.authentication.decorators import ami_login_required
from ami.fi.api_exceptions import (
    FISessionExpired,
    FISessionNotFound,
    MissingAuthHeader,
    WrongFormatAuthHeader,
)
from ami.fi.models import FISession, UserPasskey
from ami.fi.serializers import TokenSerializer
from ami.fi.utils import generate_id_token
from ami.user.utils import build_fc_hash

logger = logging.getLogger(__name__)


@api_view(["POST"])
def token(request: Request) -> Response:
    if not settings.FI_SILENT_LOGIN_ENABLED:
        raise Http404
    serializer = TokenSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as e:
        logging.exception(e)
        raise
    data: dict = cast(dict, serializer.validated_data)

    try:
        code_hash = make_password(data["code"], settings.FI_HASH_SALT)
        fi_session = FISession.objects.get(code=code_hash)
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

    return Response(
        {
            "access_token": access_token,
            "expires_in": 60,
            "id_token": encoded_id_token,
            "token_type": "Bearer",
        }
    )


@api_view(["GET"])
def userinfo(request: Request) -> Response:
    if not settings.FI_SILENT_LOGIN_ENABLED:
        raise Http404
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

    return Response(fi_session.user_data)


@api_view(["GET"])
def logout(request: Request) -> HttpResponseBadRequest | HttpResponseRedirect:
    if not settings.FI_SILENT_LOGIN_ENABLED:
        raise Http404
    redirect_uri = request.GET.get("post_logout_redirect_uri")
    if redirect_uri != f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_LOGOUT_CALLBACK_ENDPOINT}":
        return HttpResponseBadRequest()

    redirect_uri = f"{redirect_uri}?state={request.GET.get('state')}"

    return redirect(redirect_uri)


@api_view(["POST"])
@ami_login_required
def passkey_generate_registration_options(request):
    if not request.data.get("displayName"):
        return Response({"error": "missing-display-name"}, status=400)

    options = generate_registration_options(
        rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
        rp_name=settings.PASSKEY_RP_NAME,
        user_name=request.data.get("displayName"),
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            resident_key=ResidentKeyRequirement.REQUIRED,
        ),
    )
    challenge = base64.urlsafe_b64encode(options.challenge).decode()
    request.session["passkey_registration_challenge"] = challenge

    return Response(json.loads(options_to_json(options)))


@api_view(["POST"])
@ami_login_required
def passkey_verify_registration(request):
    challenge = request.session.pop("passkey_registration_challenge", "")
    if not challenge:
        logger.error("Missing challenge")
        return Response({"error": "missing-challenge"}, status=400)
    try:
        registration_verification = verify_registration_response(
            credential=request.data,
            expected_challenge=base64.urlsafe_b64decode(challenge.encode()),
            expected_origin=settings.PUBLIC_APP_URL,
            expected_rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
            require_user_verification=True,
        )
    except InvalidRegistrationResponse as e:
        logger.exception("Invalid registration response")
        return Response(
            {"error": "invalid-registration-response", "error-details": str(e)}, status=400
        )

    credential_id = (
        base64.urlsafe_b64encode(registration_verification.credential_id).decode().rstrip("=")
    )
    public_key = base64.urlsafe_b64encode(registration_verification.credential_public_key).decode()
    UserPasskey.objects.create(
        user=request.ami_user, credential_id=credential_id, credential_public_key=public_key
    )
    return Response({"verified": registration_verification.user_verified})


@api_view(["GET"])
def passkey_generate_authentication_options(request):
    options = generate_authentication_options(
        rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
    )
    challenge = base64.urlsafe_b64encode(options.challenge).decode()
    request.session["passkey_authentication_challenge"] = challenge
    return Response(json.loads(options_to_json(options)))


@api_view(["POST"])
def passkey_verify_authentication(request):
    fi_session_id = request.session.pop("fi_session_id", "")
    challenge = request.session.pop("passkey_authentication_challenge", "")
    if not fi_session_id:
        logger.error("Missing FI Session")
        return Response({"error": "missing-fi-session"}, status=400)
    try:
        fi_session_id = uuid.UUID(fi_session_id)
    except ValueError:
        logger.error("Invalid FI Session")
        return Response({"error": "invalid-fi-session"}, status=400)
    try:
        fi_session = FISession.objects.get(id=fi_session_id)
    except FISession.DoesNotExist:
        logger.error("Unknown FI Session")
        return Response({"error": "unknown-fi-session"}, status=400)
    if settings.USERINFO_COOKIE_NAME not in request.COOKIES:
        logger.error("Missing cookie")
        return Response({"error": "missing-cookie"}, status=403)

    try:
        decoded_user_data = signing.loads(request.COOKIES[settings.USERINFO_COOKIE_NAME])
    except signing.BadSignature:
        return Response({"error": "invalid-signature"}, status=403)

    # put fi_session_id back into session as further errors will be recoverable by user
    # (selecting another passkey for example)
    request.session["fi_session_id"] = str(fi_session_id)

    if not challenge:
        logger.error("Missing challenge")
        return Response({"error": "missing-challenge", "retry": True}, status=400)

    try:
        credential_id = request.data["id"]
    except KeyError:
        logger.error("Missing credential ID")
        return Response({"error": "missing-credential-id", "retry": True}, status=400)
    try:
        user_passkey = UserPasskey.objects.get(credential_id=credential_id)
    except UserPasskey.DoesNotExist:
        logger.error("Unknown credential ID")
        return Response({"error": "unknown-credential-id", "retry": True}, status=400)
    try:
        authentication_verification = verify_authentication_response(
            credential=request.data,
            expected_challenge=base64.urlsafe_b64decode(challenge.encode()),
            expected_origin=settings.PUBLIC_APP_URL,
            expected_rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
            credential_public_key=base64.urlsafe_b64decode(
                user_passkey.credential_public_key.encode()
            ),
            credential_current_sign_count=0,
            require_user_verification=True,
        )
    except InvalidAuthenticationResponse as e:
        logger.exception("Invalid authentication response")
        return Response(
            {"error": "invalid-authentication-response", "error-details": str(e), "retry": True},
            status=400,
        )
    code = token_urlsafe(64)
    # check that user associated with passkey matches with données pivot
    fc_hash = build_fc_hash(
        given_name=decoded_user_data.get("given_name") or "",
        family_name=decoded_user_data.get("family_name") or "",
        birthdate=decoded_user_data.get("birthdate") or "",
        gender=decoded_user_data.get("gender") or "",
        birthplace=decoded_user_data.get("birthplace") or "",
        birthcountry=decoded_user_data.get("birthcountry") or "",
    )
    if fc_hash != user_passkey.user.fc_hash:
        logger.error("Difference in FC hash")
        return Response({"error": "difference-in-fc-hash", "retry": True}, status=403)
    if request.ami_user and request.ami_user != user_passkey.user:
        # check if user associated with passkey is request.ami_user if not None
        logger.error("User is not AMI user'")
        return Response({"error": "user-is-not-ami-user", "retry": True}, status=403)
    fi_session.user_data = decoded_user_data
    fi_session.code = make_password(code, settings.FI_HASH_SALT)
    fi_session.save()
    redirect_uri = f"{settings.FI_REDIRECT_URI}?code={code}&state={fi_session.state}"
    if settings.PUBLIC_FC_PROXY_BASE_URL:
        params = {
            "redirect_uri": redirect_uri,
        }
        redirect_uri = (
            f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-callback/?{urlencode(params)}"
        )
    request.session.pop("fi_session_id")
    return Response(
        {"verified": authentication_verification.user_verified, "redirect_uri": redirect_uri}
    )
