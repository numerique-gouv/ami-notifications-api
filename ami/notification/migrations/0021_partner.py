from django.db import migrations


def forward(apps, schema_editor):
    Notification = apps.get_model("notification", "Notification")
    Notification.objects.exclude(item_parent_partner_slug__isnull=True).exclude(
        item_parent_partner_slug__in=["", "psl", "dinum-ami", "dinum-dn", "dinum-rdvsp"]
    ).update(item_parent_partner_slug="dinum-ami")


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0020_partner"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
