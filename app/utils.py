from litestar import Response
from litestar.response.redirect import Redirect

from app import env


def retry_fc_later(error_dict: dict[str, str] | None = None) -> Response[dict[str, str]]:
    if not error_dict:
        error_dict = {}
    params: dict[str, str] = {
        "error": "Erreur lors de la France Connexion, veuillez réessayer plus tard.",
        "error_type": "FranceConnect",
        **error_dict,
    }
    return Redirect(f"{env.PUBLIC_APP_URL}/", query_params=params)
