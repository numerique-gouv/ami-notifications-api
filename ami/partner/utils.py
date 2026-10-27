from ami.partner.models import Partner


def is_allowed_url(url):
    partners = Partner.objects.all()
    if not partners:
        return True
    return any(partner.is_url_allowed(url) for partner in partners)
