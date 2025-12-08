import hashlib

from litestar import Response
from litestar.response.redirect import Redirect

from app import env


def retry_fc_later(error_dict: dict[str, str] | None = None) -> Response[dict[str, str]]:
    if not error_dict:
        error_dict = {}
    params: dict[str, str] = {
        "error": "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.",
        "error_type": "FranceConnect",
        **error_dict,
    }
    return Redirect(f"{env.PUBLIC_APP_URL}/", query_params=params)


def error_from_response(response: Response[str], ami_details: str | None = None) -> Response[str]:
    details = response.json()  # type: ignore[reportUnknownVariableType]
    if ami_details is not None:
        details["ami_details"] = ami_details
    return Response(details, status_code=response.status_code)  # type: ignore[reportUnknownVariableType]


def error_from_message(
    message: dict[str, str], status_code: int | None
) -> Response[dict[str, str]]:
    return Response(message, status_code=status_code)


def ami_hash(
    *,
    given_name: str,
    family_name: str,
    birthdate: str,
    gender: str,
    birthplace: str,
    birthcountry: str,
) -> str:
    recipient_fc_hash = hashlib.sha256()
    recipient_fc_hash.update(
        f"{given_name}{family_name}{birthdate}{gender}{birthplace}{birthcountry}".encode("utf-8")
    )
    return recipient_fc_hash.hexdigest()
