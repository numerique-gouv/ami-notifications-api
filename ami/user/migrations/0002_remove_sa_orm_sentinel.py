from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="registration",
            name="sa_orm_sentinel",
        ),
        migrations.RemoveField(
            model_name="user",
            name="sa_orm_sentinel",
        ),
    ]
