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
def logout(request: Request) -> Response:
    return Response()
