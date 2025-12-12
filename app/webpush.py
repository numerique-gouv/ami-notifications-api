from webpush import WebPush

from app import env


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=env.VAPID_PUBLIC_KEY.encode(),
        private_key=env.VAPID_PRIVATE_KEY.encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush
