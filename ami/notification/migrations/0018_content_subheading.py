from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0017_apiv2_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="content_subheading",
            field=models.CharField(blank=True, null=True),
        ),
    ]
