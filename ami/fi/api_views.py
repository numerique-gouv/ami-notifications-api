from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def authorize(request: Request) -> Response:
    return Response()


@api_view(["POST"])
def token(request: Request) -> Response:
    return Response()


@api_view(["GET"])
def userinfo(request: Request) -> Response:
    return Response()


@api_view(["GET"])
def logout(request: Request) -> HttpResponseBadRequest | HttpResponseRedirect:
    redirect_uri = request.GET.get("post_logout_redirect_uri")
    if redirect_uri != f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_LOGOUT_CALLBACK_ENDPOINT}":
        return HttpResponseBadRequest()

    redirect_uri = f"{redirect_uri}?state={request.GET.get('state')}"

    return redirect(redirect_uri)
