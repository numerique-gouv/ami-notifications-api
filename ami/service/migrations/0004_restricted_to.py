from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0003_charfields"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="restricted_to",
            field=models.CharField(
                blank=True,
                null=True,
                help_text="fc_hash des utilisateurs autorisés à voir cette démarche dans le catalogue de démarches, séparés par un espace. "
                "Laisser vide pour un accès à tous les utilisateurs.",
            ),
        ),
    ]
