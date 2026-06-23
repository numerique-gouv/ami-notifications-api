import logging
from secrets import token_urlsafe
from typing import cast
from urllib.parse import urlencode

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect

from ami.fi.forms import AuthorizeForm
from ami.fi.models import FISession

logger = logging.getLogger(__name__)


def authorize(request):
    if request.method == "POST":
        raise

    form = AuthorizeForm(data=request.GET)
    if not form.is_valid():
        logger.error("Wrong parameters", extra=form.errors)
        return HttpResponseBadRequest("wrong-parameters")

    data: dict = cast(dict, form.cleaned_data)

    if settings.USERINFO_COOKIE_JWT_NAME not in request.COOKIES:
        logger.error("Missing cookie")
        return HttpResponseForbidden("missing-cookie")

    encoded_user_data = request.COOKIES[settings.USERINFO_COOKIE_JWT_NAME]
    decoded_user_data = jwt.decode(
        encoded_user_data, options={"verify_signature": False}, algorithms=["ES256"]
    )

    code = token_urlsafe(64)
    fi_session = FISession.objects.create(
        user_data=decoded_user_data,
        state=data["state"],
        nonce=data["nonce"],
        code=make_password(code, settings.FI_HASH_SALT),
    )

    redirect_uri = f"{data['redirect_uri']}?code={code}&state={fi_session.state}"
    if settings.PUBLIC_FC_PROXY_BASE_URL:
        params = {
            "redirect_uri": redirect_uri,
        }
        redirect_uri = (
            f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-callback/?{urlencode(params)}"
        )
    return redirect(redirect_uri)
