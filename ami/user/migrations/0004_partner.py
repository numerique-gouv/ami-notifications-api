from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_consent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consent",
            name="partner_id",
            field=models.CharField(db_column="partner_id", max_length=100),
        ),
        migrations.RenameField(
            model_name="consent",
            old_name="partner_id",
            new_name="partner_slug",
        ),
        migrations.AlterUniqueTogether(
            name="consent",
            unique_together={("user", "partner_slug")},
        ),
    ]
