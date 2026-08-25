import logging
from typing import cast
from urllib.parse import urlencode

from django.conf import settings
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect

from ami.fi.forms import AuthorizeForm
from ami.fi.models import FISession

logger = logging.getLogger(__name__)


def authorize(request):
    if not settings.FI_SILENT_LOGIN_ENABLED:
        raise Http404

    form = AuthorizeForm(data=request.GET)
    if not form.is_valid():
        logger.error("Wrong parameters", extra=form.errors)
        return HttpResponseBadRequest("wrong-parameters")

    if request.ami_user and not request.ami_user.userpasskey_set.exists():
        return redirect("/#/relogin")

    data: dict = cast(dict, form.cleaned_data)

    fi_session = FISession.objects.create(
        user_data={},
        state=data["state"],
        nonce=data["nonce"],
    )
    request.session["fi_session_id"] = str(fi_session.id)

    from_hash = request.session.get("login_from_hash") or ""
    params = {
        "redirect_to_hash": from_hash,
    }
    return redirect(f"/?{urlencode(params)}#/passkey-authentication")
