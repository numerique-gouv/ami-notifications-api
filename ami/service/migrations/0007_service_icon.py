from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0006_service_kind"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="icon",
            field=models.CharField(default=""),
            preserve_default=False,
        ),
    ]
