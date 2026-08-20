from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0004_restricted_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="kind",
            field=models.CharField(
                choices=[
                    ("catalog", "Catalogue"),
                    ("sos", "SOS"),
                    ("steps", "Liste d’étapes"),
                ],
                default="catalog",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="partner_id",
            field=models.CharField(
                choices=[
                    ("psl", "PSL"),
                    ("dinum-dn", "demarche.numerique.gouv.fr"),
                    ("dinum-ami", "AMI"),
                    ("dinum-rdvsp", "RDV SP"),
                ]
            ),
        ),
    ]
