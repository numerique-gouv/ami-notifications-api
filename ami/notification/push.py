from webpush import WebPush

from ami.notification.models import Notification
from ami.settings import CONFIG


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=CONFIG["VAPID_PUBLIC_KEY"].encode(),
        private_key=CONFIG["VAPID_PRIVATE_KEY"].encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush


def push(notification: Notification, try_push: bool) -> None:
    # TODO: implement the push mechanism
    pass
