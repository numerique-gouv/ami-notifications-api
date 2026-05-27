from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0002_remove_sa_orm_sentinel"),
    ]

    operations = [
        migrations.AddField(
            model_name="nonce",
            name="context",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
