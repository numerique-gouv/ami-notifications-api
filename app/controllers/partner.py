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

        if partner_url.endswith("caller={token-jwt}"):
            otv_private_key = os.getenv("OTV_PRIVATE_KEY")
            if otv_private_key is not None:
                identity_token = generate_identity_token(
                    preferred_username or "",
                    email or "",
                    address_city or "",
                    address_postcode or "",
                    address_name or "",
                    current_user.fc_hash or "",
                )
                partner_url = partner_url.replace("{token-jwt}", identity_token)

        response_data = schemas.PartnerResponse.model_validate(
            {
                "partner_url": partner_url,
            }
        )
        return Response(content=response_data, status_code=HTTP_200_OK)

    @get("/api/v1/partner/otv/public_key")
    async def get_partner_public_key(self) -> Response[schemas.PartnerPublicKeyResponse]:
        public_key = env.PUBLIC_OTV_PUBLIC_KEY

        response_data = schemas.PartnerPublicKeyResponse.model_validate(
            {
                "public_key": public_key,
            }
        )
        return Response(content=response_data, status_code=HTTP_200_OK)
