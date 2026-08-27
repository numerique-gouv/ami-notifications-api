from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0007_service_icon"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="partner_id",
            field=models.CharField(
                choices=[
                    ("psl", "PSL"),
                    ("dinum-dn", "demarche.numerique.gouv.fr"),
                    ("dinum-ami", "AMI"),
                    ("dinum-rdvsp", "RDV SP"),
                ],
                db_column="partner_id",
            ),
        ),
        migrations.RenameField(
            model_name="service",
            old_name="partner_id",
            new_name="partner_slug",
        ),
        migrations.AlterUniqueTogether(
            name="service",
            unique_together={("kind", "partner_slug", "item_type")},
        ),
    ]
