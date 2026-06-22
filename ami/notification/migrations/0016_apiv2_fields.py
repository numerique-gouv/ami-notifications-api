from django.db import migrations, models


def forward(apps, schema_editor):
    Notification = apps.get_model("notification", "Notification")
    Notification.objects.filter(
        event_date__isnull=True,
        send_date__isnull=False,
    ).update(event_date=models.F("send_date"))
    Notification.objects.filter(
        content_link__isnull=True,
        item_external_url__isnull=False,
    ).update(content_link=models.F("item_external_url"))


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0015_apiv2_fields"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
