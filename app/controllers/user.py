from typing import Any

import httpx
import jwt
from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Request, Response, get

from app import env, models, schemas
from app.services.user import UserService


class UserController(Controller):
    dependencies = {
        "users_service": providers.create_service_provider(UserService),
    }

    @get(path="/fc_userinfo", include_in_schema=False)
    async def get_fc_userinfo(
        self,
        users_service: UserService,
        request: Request[Any, Any, Any],
    ) -> Response[Any]:
        """This endpoint "forwards" the request coming from the frontend (the app).

        FranceConnect doesn't implement CORS, so the app can't directly query it for the user info.
        We thus have this endpoint to act as some kind of proxy.

        """
        response = httpx.get(
            f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_USERINFO_ENDPOINT}",
            headers={"authorization": request.headers["authorization"]},
        )

        userinfo_jws = response.text
        decoded_userinfo = jwt.decode(
            userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"]
        )
        userinfo: schemas.FCUserInfo = schemas.FCUserInfo(**decoded_userinfo)

        user: models.User | None = await users_service.get_one_or_none(**userinfo.model_dump())
        if user is None:
            user = await users_service.create(
                models.User(**userinfo.model_dump()),
                auto_commit=True,
            )
        result: dict[str, Any] = {
            "user_id": user.id,
            "user_data": userinfo_jws,
        }

        return Response(result, status_code=response.status_code)
