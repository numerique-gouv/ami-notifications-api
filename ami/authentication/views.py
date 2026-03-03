from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from ami.authentication.auth import generate_nonce
from ami.authentication.models import Nonce


@require_GET
def login_france_connect(request):
    try:
        NONCE = generate_nonce()
        nonce = Nonce.objects.create(nonce=NONCE)

        params = {
            "scope": settings.PUBLIC_FC_SCOPE,
            "redirect_uri": settings.PUBLIC_FC_PROXY or settings.PUBLIC_FC_AMI_REDIRECT_URL,
            "response_type": "code",
            "client_id": settings.PUBLIC_FC_AMI_CLIENT_ID,
            "state": (
                f"{settings.PUBLIC_FC_AMI_REDIRECT_URL}?state={nonce.id}"
                if settings.PUBLIC_FC_PROXY
                else str(nonce.id)
            ),
            "nonce": NONCE,
            "acr_values": "eidas1",
            "prompt": "login",
        }

        login_url = (
            f"{settings.PUBLIC_FC_BASE_URL}{settings.PUBLIC_FC_AUTHORIZATION_ENDPOINT}"
            f"?{urlencode(params)}"
        )
        return redirect(login_url)
    except Exception:
        return redirect(f"{settings.PUBLIC_APP_URL}/#/technical-error")
