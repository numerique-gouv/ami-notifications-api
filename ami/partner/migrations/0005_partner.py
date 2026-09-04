from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0004_add_ip_allow_list"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="link",
            field=models.CharField(blank=True, null=True),
        ),
    ]
