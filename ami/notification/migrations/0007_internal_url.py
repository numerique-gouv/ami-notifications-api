from django.db import migrations


def forward(apps, schema_editor):
    ScheduledNotification = apps.get_model("notification", "ScheduledNotification")
    Notification = apps.get_model("notification", "Notification")

    for notification in Notification.objects.filter(internal_url="/#/procedure"):
        notification.internal_url = "/procedure"
        notification.save()

    for scheduled_notification in ScheduledNotification.objects.filter(internal_url="/#/procedure"):
        scheduled_notification.internal_url = "/procedure"
        scheduled_notification.save()


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0006_remove_sender"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
