import uuid
from collections.abc import Sequence
from typing import Annotated

from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Response, delete, get, post
from litestar.di import Provide
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
from app.services.user import provide_user


class RegistrationController(Controller):
    dependencies = {
        "current_user": Provide(provide_user),
        "registrations_service": providers.create_service_provider(RegistrationService),
    }

    @post("/api/v1/users/registrations")
    async def register(
        self,
        registrations_service: RegistrationService,
        current_user: models.User,
        data: Annotated[
            schemas.RegistrationCreate,
            Body(
                title="Register to receive notifications",
                description="Register with a push subscription and an email to receive notifications",
            ),
        ],
    ) -> Response[schemas.Registration]:
        WebPushSubscription.model_validate(data.subscription)

        existing_registration: (
            models.Registration | None
        ) = await registrations_service.get_one_or_none(
            subscription=data.subscription, user=current_user
        )
        if existing_registration is not None:
            # This registration already exists, don't duplicate it.
            return Response(
                registrations_service.to_schema(
                    existing_registration, schema_type=schemas.Registration
                ),
                status_code=HTTP_200_OK,
            )

        registration: models.Registration = await registrations_service.create(
            models.Registration(user=current_user, **data.model_dump())
        )
        return Response(
            registrations_service.to_schema(registration, schema_type=schemas.Registration),
            status_code=HTTP_201_CREATED,
        )

    @get("/api/v1/users/registrations")
    async def list_registrations(
        self,
        registrations_service: RegistrationService,
        current_user: models.User,
    ) -> list[schemas.Registration]:
        # We could do:
        # return registrations_service.to_schema(user.registrations, schema_type=schemas.Registration)
        # But it adds pagination.
        # For the moment, just return a list of dict
        registrations: Sequence[models.Registration] = await registrations_service.list(
            user=current_user,
        )
        type_adapter = TypeAdapter(list[schemas.Registration])
        return type_adapter.validate_python(registrations)

    @delete("/api/v1/users/registrations/{registration_id:uuid}")
    async def unregister(
        self,
        registrations_service: RegistrationService,
        current_user: models.User,
        registration_id: uuid.UUID,
    ) -> None:
        registration: models.Registration | None = await registrations_service.get_one_or_none(
            id=registration_id,
            user=current_user,
        )
        if registration is None:
            raise NotFoundException(detail="Registration not found")
        await registrations_service.delete(registration_id)
