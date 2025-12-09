from typing import Any

import jwt
from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Request, Response, get

from app import env, models
from app.auth import jwt_cookie_auth
from app.httpx import httpxClient
from app.services.user import UserService
from app.utils import build_fc_hash


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
        response = httpxClient.get(
            f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_USERINFO_ENDPOINT}",
            headers={"authorization": request.headers["authorization"]},
        )

        userinfo_jws = response.text
        decoded_userinfo = jwt.decode(
            userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"]
        )
        fc_hash = build_fc_hash(
            given_name=decoded_userinfo["given_name"],
            family_name=decoded_userinfo["family_name"],
            birthdate=decoded_userinfo["birthdate"],
            gender=decoded_userinfo["gender"],
            birthplace=decoded_userinfo["birthplace"],
            birthcountry=decoded_userinfo["birthcountry"],
        )

        user: models.User | None = await users_service.get_one_or_none(fc_hash=fc_hash)
        if user is None:
            user = await users_service.create(models.User(fc_hash=fc_hash))
        else:
            user = await users_service.update({"already_seen": True}, item_id=user.id)
        result: dict[str, Any] = {
            "user_id": user.id,
            "user_data": userinfo_jws,
        }

        return jwt_cookie_auth.login(
            identifier=str(user.id), response_body=result, response_status_code=response.status_code
        )
