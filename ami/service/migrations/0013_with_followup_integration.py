from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0012_service_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="with_followup_integration",
            field=models.BooleanField(default=False),
        ),
    ]
