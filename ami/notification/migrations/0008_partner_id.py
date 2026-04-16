from django.db import migrations


def forward(apps, schema_editor):
    Notification = apps.get_model("notification", "Notification")
    Notification.objects.filter(partner_id__isnull=True).update(partner_id="dinum-ami")
    Notification.objects.filter(partner_id="").update(partner_id="dinum-ami")


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0007_internal_url"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
