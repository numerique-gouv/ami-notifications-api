from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0003_internal_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notification",
            name="sa_orm_sentinel",
        ),
        migrations.RemoveField(
            model_name="schedulednotification",
            name="sa_orm_sentinel",
        ),
    ]
