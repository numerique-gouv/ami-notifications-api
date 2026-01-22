import os

from litestar import Controller, Response, get
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK

from app import env, models, schemas
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
    ) -> Response[schemas.PartnerResponse]:
        partner_url = env.PUBLIC_OTV_URL

        if env.PUBLIC_OTV_URL.endswith("caller={token-jwt}"):
            if preferred_username is None:
                preferred_username = ""
            if email is None:
                email = ""
            if address_city is None:
                address_city = ""
            if address_postcode is None:
                address_postcode = ""
            if address_name is None:
                address_name = ""

            identity_token = generate_identity_token(
                preferred_username,
                email,
                address_city,
                address_postcode,
                address_name,
                current_user.fc_hash,
            )
            partner_url = partner_url.replace("{token-jwt}", identity_token)

        response_data = schemas.PartnerResponse.model_validate(
            {
                "partner_url": partner_url,
            }
        )
        return Response(content=response_data, status_code=HTTP_200_OK)
