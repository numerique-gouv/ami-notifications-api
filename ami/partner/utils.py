import urllib.parse

from django.conf import settings

from ami.partner.models import Partner


def is_allowed_url(url):
    if (
        url.startswith("/")
        or urllib.parse.urlparse(url).netloc
        == urllib.parse.urlparse(settings.PUBLIC_APP_URL).netloc
    ):
        # always allow local URIs
        return True
    partners = Partner.objects.all()
    if not partners:
        return True
    return any(partner.is_url_allowed(url) for partner in partners)
