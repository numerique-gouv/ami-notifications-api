from django.db import migrations

from ami.partner.models import partners


def forward(apps, schema_editor):
    Notification = apps.get_model("notification", "Notification")
    Notification.objects.filter(partner_id__isnull=False).exclude(partner_id="").filter(
        content_icon="fr-icon-mail-star-line"
    ).update(content_icon=None)
    for partner in partners.values():
        Notification.objects.filter(partner_id=partner.id).filter(content_icon=partner.icon).update(
            content_icon=None
        )


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0013_item_is_archived"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
