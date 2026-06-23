from django.db import migrations


def forward(apps, schema_editor):
    Registration = apps.get_model("user", "Registration")

    for registration in Registration.objects.all():
        subscription = registration.subscription
        if subscription.get("device_id"):
            registration.device_id = subscription["device_id"]
            registration.save()


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_device_id"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
