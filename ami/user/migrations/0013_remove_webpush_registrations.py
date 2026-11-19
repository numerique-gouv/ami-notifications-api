from django.db import migrations


def forward(apps, schema_editor):
    Registration = apps.get_model("user", "Registration")

    for registration in Registration.objects.all():
        if not registration.device_id:
            registration.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0012_personal_data_consent"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
