from typing import Annotated

from litestar import Controller, Response, get, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)
from webpush import WebPushSubscription

from app import models as m
from app import schemas as s
from app.repositories.registration import RegistrationRepository, provide_registrations_repo
from app.repositories.user import (
    UserRepository,
    provide_users_repo,
    provide_users_with_registrations_repo,
)


class RegistrationController(Controller):
    dependencies = {
        "registrations_repo": Provide(provide_registrations_repo),
        "users_repo": Provide(provide_users_repo),
        "users_with_registrations_repo": Provide(provide_users_with_registrations_repo),
    }
    return_dto = s.RegistrationDTO

    @post("/api/v1/registrations")
    async def register(
        self,
        registrations_repo: RegistrationRepository,
        users_repo: UserRepository,
        data: Annotated[
            s.RegistrationCreate,
            Body(
                title="Register to receive notifications",
                description="Register with a push subscription and an email to receive notifications",
            ),
        ],
    ) -> Response[m.Registration]:
        WebPushSubscription.model_validate(data.subscription)
        user: m.User | None = await users_repo.get_one_or_none(id=data.user_id)
        if user is None:
            raise NotFoundException(detail="User not found")

        existing_registration: m.Registration | None = await registrations_repo.get_one_or_none(
            subscription=data.subscription, user=user
        )
        if existing_registration is not None:
            # This registration already exists, don't duplicate it.
            return Response(existing_registration, status_code=HTTP_200_OK)

        registration: m.Registration = await registrations_repo.add(
            m.Registration(**data.model_dump())
        )
        await registrations_repo.session.commit()
        return Response(registration, status_code=HTTP_201_CREATED)

    @get("/api/v1/users/{user_id:int}/registrations")
    async def list_registrations(
        self,
        users_with_registrations_repo: UserRepository,
        user_id: int,
    ) -> list[m.Registration]:
        user: m.User | None = await users_with_registrations_repo.get_one_or_none(id=user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        return user.registrations
