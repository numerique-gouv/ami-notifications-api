from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="nonce",
            name="sa_orm_sentinel",
        ),
        migrations.RemoveField(
            model_name="revokedauthtoken",
            name="sa_orm_sentinel",
        ),
    ]
