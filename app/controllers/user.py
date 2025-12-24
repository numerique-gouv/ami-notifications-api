import datetime
from typing import Any

import jwt
from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Request, Response, get

from app import env, models
from app.auth import jwt_cookie_auth
from app.httpx import httpxClient
from app.services.scheduled_notification import ScheduledNotificationService
from app.services.user import UserService
from app.utils import build_fc_hash


class UserController(Controller):
    dependencies = {
        "users_service": providers.create_service_provider(UserService),
        "scheduled_notifications_service": providers.create_service_provider(
            ScheduledNotificationService
        ),
    }

    @get(path="/fc_userinfo", include_in_schema=False)
    async def get_fc_userinfo(
        self,
        users_service: UserService,
        scheduled_notifications_service: ScheduledNotificationService,
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
        create_welcome = False
        now = datetime.datetime.now(datetime.timezone.utc)
        if user is None:
            user = await users_service.create(models.User(fc_hash=fc_hash, last_logged_in=now))
            create_welcome = True
        else:
            create_welcome = user.last_logged_in is None
            user = await users_service.update({"last_logged_in": now}, item_id=user.id)
        if create_welcome:
            await scheduled_notifications_service.create_welcome_scheduled_notification(user)
        result: dict[str, Any] = {
            "user_id": user.id,
            "user_data": userinfo_jws,
            "user_first_login": create_welcome,
        }

        return jwt_cookie_auth.login(
            identifier=str(user.id), response_body=result, response_status_code=response.status_code
        )
