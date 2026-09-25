from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0011_partner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="short_description",
            field=models.CharField(db_column="short_description", verbose_name="Service"),
        ),
        migrations.RenameField(
            model_name="service",
            old_name="short_description",
            new_name="service_name",
        ),
    ]
