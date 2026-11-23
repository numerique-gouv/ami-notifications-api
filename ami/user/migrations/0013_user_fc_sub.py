from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0012_personal_data_consent"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="fc_sub",
            field=models.CharField(null=True),
        ),
    ]
