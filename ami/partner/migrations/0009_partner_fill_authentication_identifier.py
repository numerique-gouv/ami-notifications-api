from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0008_partner_authentication_identifier"),
    ]

    operations = [
        migrations.RunSQL("UPDATE partner_partner SET authentication_identifier = slug", ""),
    ]
