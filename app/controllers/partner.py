import os

from litestar import Controller, Response, get
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK

from app import env, models
from app.services.user import provide_user
from app.utils import generate_identity_token

PUBLIC_OTV_URL = os.getenv("PUBLIC_OTV_URL", "")


class PartnerController(Controller):
    dependencies = {
        "current_user": Provide(provide_user),
    }

    @get("/api/v1/partner/otv/url")
    async def generate_partner_url(
        self,
        current_user: models.User,
        preferred_username: str | None = None,
        email: str | None = None,
        address_city: str | None = None,
        address_postcode: str | None = None,
        address_name: str | None = None,
    ) -> Response[dict[str, str]]:
        partner_url = env.PUBLIC_OTV_URL

        if partner_url.endswith("caller={token-jwt}"):
            otv_private_key = os.getenv("OTV_PRIVATE_KEY")
            if otv_private_key is not None:
                identity_token = generate_identity_token(
                    preferred_username or "",
                    email or "",
                    address_city or "",
                    address_postcode or "",
                    address_name or "",
                    current_user.fc_hash,
                )
                partner_url = partner_url.replace("{token-jwt}", identity_token)

        return Response(content={"partner_url": partner_url}, status_code=HTTP_200_OK)
