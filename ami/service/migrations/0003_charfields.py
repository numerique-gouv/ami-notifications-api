from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0002_service"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="short_description",
            field=models.CharField("Service"),
        ),
        migrations.AlterField(
            model_name="service",
            name="url",
            field=models.CharField(),
        ),
    ]
