import ipaddress
import secrets
import uuid

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import models

from ami.partner.schemas import PartnersItem


class Partner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slug = models.SlugField(unique=True)
    name = models.CharField()
    icon = models.CharField(blank=True)
    link = models.CharField(blank=True, null=True)
    consent_is_enabled = models.BooleanField()
    displayed_on_front = models.BooleanField(default=True)
    authentication_identifier = models.CharField(blank=True, null=True)
    ip_allow_list = models.TextField(blank=True, null=True)
    trusted_base_uris = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def dash_slug(self):
        return self.slug.replace("_", "-") or ""

    def has_password(self):
        return (
            self.dash_slug in settings.PARTNERS_SECRETS
            or self.dash_slug in settings.PARTNERS_SECRET_HASHS
        )

    def check_password(self, password):
        if self.dash_slug in settings.PARTNERS_SECRET_HASHS:
            encoded = settings.PARTNERS_SECRET_HASHS[self.dash_slug]
            return check_password(password, encoded)
        elif self.dash_slug in settings.PARTNERS_SECRETS:
            secret = settings.PARTNERS_SECRETS[self.dash_slug]
            return secrets.compare_digest(secret, password)
        return False

    def is_ip_allowed(self, ip_address_str):
        if not self.ip_allow_list:
            return True
        try:
            ip_address = ipaddress.ip_address(ip_address_str)
        except ValueError:
            return False
        for line_value in self.ip_allow_list.splitlines():
            if not line_value.strip() or line_value.startswith("#"):
                continue
            allowed_ip_network = ipaddress.ip_network(line_value)
            if ip_address in allowed_ip_network:
                return True
        return False

    def is_url_allowed(self, url):
        if not self.trusted_base_uris:
            return True
        for line_value in self.trusted_base_uris.splitlines():
            if not line_value.strip() or line_value.startswith("#"):
                continue
            if url.startswith(line_value):
                return True
        return False

    def to_partners_item(self):
        return PartnersItem(
            slug=self.slug,
            name=self.name,
            link=self.link,
        )
