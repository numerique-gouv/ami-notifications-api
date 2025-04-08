import os
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Annotated

import requests
from litestar import Litestar, get, post
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
class Notification:
    subscription: WebPushSubscription
    message: str


@get("/notification/key")
async def get_application_key() -> str:
    with open("applicationServerKey", "r") as applicationServerKey:
        return applicationServerKey.read()


@post("/notification/send")
async def notify(
    data: Annotated[
        Notification,
        Body(
            title="Send a notification", description="Send the notification message to a push url"
        ),
    ],
) -> Notification:
    subscription = WebPushSubscription.model_validate(data.subscription)

    message = wp.get(message=data.message, subscription=subscription)

    response = requests.post(subscription.endpoint, data=message.encrypted, headers=message.headers)
    print("response", response)
    return data


@get("/notifications/{email:str}")
async def get_notifications(email: str) -> list[str]:
    return []


app = Litestar(
    route_handlers=[
        create_static_files_router(
            path="/",
            directories=[HTML_DIR],
            html_mode=True,
        ),
        get_application_key,
        notify,
        get_notifications,
    ]
)
