import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, cast

import requests
from litestar import Litestar, get, post
from litestar.exceptions import NotFoundException
from litestar.params import Body
from litestar.static_files import create_static_files_router
from webpush import WebPush, WebPushSubscription

wp = WebPush(
    public_key=Path("./public_key.pem"),
    private_key=os.getenv("VAPID_PRIVATE_KEY", "").encode(),
    subscriber="mathieu@agopian.info",
)

HTML_DIR = "public"


@dataclass
class Registration:
    subscription: WebPushSubscription
    email: str


Registrations = dict[str, Registration]


@dataclass
class Notification:
    email: str
    message: str


@get("/notification/key")
async def get_application_key() -> str:
    with open("applicationServerKey", "r") as applicationServerKey:
        return applicationServerKey.read()


@post("/notification/register")
async def register(
    data: Annotated[
        Registration,
        Body(
            title="Register to receive notifications",
            description="Register with a push subscription and an email to receive notifications",
        ),
    ],
) -> Registration:
    WebPushSubscription.model_validate(data.subscription)
    # TODO: Store the registration in memory => change to store in database
    app.state.registrations[data.email] = data
    return data


@post("/notification/send")
async def notify(
    data: Annotated[
        Notification,
        Body(
            title="Send a notification",
            description="Send the notification message to a registered user",
        ),
    ],
) -> Notification:
    if app.state.registrations is None:
        app.state.registrations = {}
    registration: Registration | None = app.state.registrations.get(data.email)
    if registration is None:
        raise NotFoundException

    message = wp.get(message=data.message, subscription=registration.subscription)

    response = requests.post(
        registration.subscription.endpoint, data=message.encrypted, headers=message.headers
    )
    print("response", response)
    return data


@get("/notification/users")
async def list_users() -> Registrations:
    registrations: Registrations = app.state.registrations
    return registrations


@get("/notifications/{email:str}")
async def get_notifications(email: str) -> list[str]:
    return []


def in_memory_db(app: Litestar) -> Registrations:
    if not getattr(app.state, "registrations", None):
        app.state.registrations = {}
    return cast("Registrations", app.state.registrations)


app = Litestar(
    route_handlers=[
        create_static_files_router(
            path="/",
            directories=[HTML_DIR],
            html_mode=True,
        ),
        get_application_key,
        register,
        notify,
        list_users,
        get_notifications,
    ],
    on_startup=[in_memory_db],
)
