from django.db import migrations


def forward(apps, schema_editor):
    Partner = apps.get_model("partner", "Partner")
    Partner.objects.filter(slug="psl").update(link="https://www.service-public.gouv.fr/")
    Partner.objects.filter(slug="dinum-dn").update(link="https://demarche.numerique.gouv.fr/")
    Partner.objects.filter(slug="dinum-ami").update(link="")
    Partner.objects.filter(slug="dinum-rdvsp").update(name="RDV Service Public")
    Partner.objects.filter(slug="dinum-rdvsp").update(link="https://rdv.anct.gouv.fr/")


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0004_partner"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
