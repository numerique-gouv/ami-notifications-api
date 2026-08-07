from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_remove_sa_orm_sentinel"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="consent_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
