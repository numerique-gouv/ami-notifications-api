from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0007_displayed_on_front"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="authentication_identifier",
            field=models.CharField(blank=True, null=True),
        ),
    ]
