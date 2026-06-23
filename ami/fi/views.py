import logging
import uuid
from secrets import token_urlsafe
from typing import cast
from urllib.parse import urlencode

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render

from ami.fi.forms import AuthorizeForm, AuthorizeUserDataForm
from ami.fi.models import FISession

logger = logging.getLogger(__name__)


def authorize(request):
    if request.method == "POST":
        form = AuthorizeUserDataForm(data=request.POST)
        if not form.is_valid():
            logger.error("Missing user data", extra=form.errors)
            return HttpResponseBadRequest("missing-user-data")

        code = token_urlsafe(64)
        try:
            fi_session_id = uuid.UUID(form.cleaned_data["fi_session_id"])
        except ValueError:
            logger.error("Invalid FI Session")
            return HttpResponseBadRequest("invalid-fi-session")
        try:
            fi_session = FISession.objects.get(id=fi_session_id)
        except FISession.DoesNotExist:
            logger.error("Missing FI Session")
            return HttpResponseBadRequest("missing-fi-session")

        encoded_user_data = form.cleaned_data["encoded_user_data"]
        decoded_user_data = jwt.decode(
            encoded_user_data, options={"verify_signature": False}, algorithms=["ES256"]
        )

        fi_session.user_data = decoded_user_data
        fi_session.code = make_password(code, settings.FI_HASH_SALT)
        fi_session.save()

        redirect_uri = f"{settings.FI_REDIRECT_URI}?code={code}&state={fi_session.state}"
        if settings.PUBLIC_FC_PROXY_BASE_URL:
            params = {
                "redirect_uri": redirect_uri,
            }
            redirect_uri = f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-callback/?{urlencode(params)}"
        return redirect(redirect_uri)

    form = AuthorizeForm(data=request.GET)
    if not form.is_valid():
        logger.error("Wrong parameters", extra=form.errors)
        return HttpResponseBadRequest("wrong-parameters")

    data: dict = cast(dict, form.cleaned_data)

    if settings.USERINFO_COOKIE_JWT_NAME not in request.COOKIES:
        logger.error("Missing cookie")
        return HttpResponseForbidden("missing-cookie")

    encoded_user_data = request.COOKIES[settings.USERINFO_COOKIE_JWT_NAME]
    fi_session = FISession.objects.create(
        user_data={},
        state=data["state"],
        nonce=data["nonce"],
    )

    form = AuthorizeUserDataForm(
        initial={
            "fi_session_id": fi_session.id,
            "encoded_user_data": encoded_user_data,
        }
    )
    context = {"form": form}
    return render(request, "fi/authorize.html", context)
