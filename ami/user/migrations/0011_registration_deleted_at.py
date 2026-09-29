from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0010_add_registration_user_id_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="deleted_at",
            field=models.DateTimeField(null=True),
        ),
    ]
