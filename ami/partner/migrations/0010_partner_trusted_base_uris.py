from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0009_partner_fill_authentication_identifier"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="trusted_base_uris",
            field=models.TextField(blank=True, null=True),
        ),
    ]
