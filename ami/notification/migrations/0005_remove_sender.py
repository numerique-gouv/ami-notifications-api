from django.db import migrations


def forward(apps, schema_editor):
    Notification = apps.get_model("notification", "Notification")
    for notification in Notification.objects.filter(sender="AMI", partner_id__isnull=True):
        notification.partner_id = "dinum-ami"
        notification.save()


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0004_remove_sa_orm_sentinel"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
