import uuid
from typing import Annotated

from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Response, delete, get, post
from litestar.exceptions import NotFoundException
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)
from pydantic import TypeAdapter
from webpush import WebPushSubscription

from app import models, schemas
from app.services.registration import RegistrationService
from app.services.user import UserService


class RegistrationController(Controller):
    dependencies = {
        "registrations_service": providers.create_service_provider(RegistrationService),
        "users_service": providers.create_service_provider(UserService),
        "users_with_registrations_service": providers.create_service_provider(
            UserService, load=[models.User.registrations]
        ),
    }

    @post("/api/v1/registrations")
    async def register(
        self,
        registrations_service: RegistrationService,
        users_service: UserService,
        data: Annotated[
            schemas.RegistrationCreate,
            Body(
                title="Register to receive notifications",
                description="Register with a push subscription and an email to receive notifications",
            ),
        ],
    ) -> Response[schemas.Registration]:
        WebPushSubscription.model_validate(data.subscription)
        user: models.User | None = await users_service.get_one_or_none(id=data.user_id)
        if user is None:
            raise NotFoundException(detail="User not found")

        existing_registration: (
            models.Registration | None
        ) = await registrations_service.get_one_or_none(subscription=data.subscription, user=user)
        if existing_registration is not None:
            # This registration already exists, don't duplicate it.
            return Response(
                registrations_service.to_schema(
                    existing_registration, schema_type=schemas.Registration
                ),
                status_code=HTTP_200_OK,
            )

        registration: models.Registration = await registrations_service.create(
            models.Registration(**data.model_dump())
        )
        return Response(
            registrations_service.to_schema(registration, schema_type=schemas.Registration),
            status_code=HTTP_201_CREATED,
        )

    @get("/api/v1/users/{user_id:uuid}/registrations")
    async def list_registrations(
        self,
        registrations_service: RegistrationService,
        users_with_registrations_service: UserService,
        user_id: uuid.UUID,
    ) -> list[schemas.Registration]:
        user: models.User | None = await users_with_registrations_service.get_one_or_none(
            id=user_id
        )
        if user is None:
            raise NotFoundException(detail="User not found")
        # We could do:
        # return registrations_service.to_schema(user.registrations, schema_type=schemas.Registration)
        # But it adds pagination.
        # For the moment, just return a list of dict
        type_adapter = TypeAdapter(list[schemas.Registration])
        return type_adapter.validate_python(user.registrations)

    @delete("/api/v1/registrations/{registration_id:uuid}")
    async def unregister(
        self, registrations_service: RegistrationService, registration_id: uuid.UUID
    ) -> None:
        await registrations_service.delete(registration_id)
