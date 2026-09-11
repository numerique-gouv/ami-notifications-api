import ipaddress
import uuid

from django.conf import settings
from django.db import models


class Partner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slug = models.SlugField(unique=True)
    name = models.CharField()
    icon = models.CharField(blank=True)
    consent_is_enabled = models.BooleanField()
    ip_allow_list = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def secret(self):
        return settings.PARTNERS_SECRETS.get(self.slug.replace("_", "-")) or ""

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
