import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ami.annuaire_sp.models import Mairie
from ami.utils.httpx import httpxClient

dir_path = os.path.dirname(os.path.realpath(__file__))


class Command(BaseCommand):
    def handle(self, **kwargs):
        with httpxClient() as httpx_client:
            response = httpx_client.get(
                f"{settings.API_ANNUNAIRE_SP_BASE_URL}{settings.API_ANNUNAIRE_SP_ENDPOINT}",
                params={
                    "select": "id,nom,code_insee_commune,url_service_public",
                    "where": """pivot LIKE '"type_service_local": "mairie"'""",
                    "order_by": "code_insee_commune,date_modification_datetime",
                },
            )
        if response.status_code != 200:
            raise CommandError(f"failed: response status code: {response.status_code}")

        existing_mairies = set(Mairie.objects.values_list("code_insee_commune", flat=True))

        def generate_mairie(code_insee_commune, nom, id_service_local, url_service_public):
            mairie, created = Mairie.objects.get_or_create(
                code_insee_commune=code_insee_commune,
                defaults={
                    "nom": nom,
                    "id_service_local": id_service_local,
                    "url_service_public": url_service_public,
                },
            )
            if created:
                self.stdout.write(f"Mairie {code_insee_commune} created")
            elif (
                mairie.nom != nom
                or mairie.id_service_local != id_service_local
                or mairie.url_service_public != url_service_public
            ):
                mairie.nom = nom
                mairie.id_service_local = id_service_local
                mairie.url_service_public = url_service_public
                mairie.save()
                self.stdout.write(f"Mairie {code_insee_commune} updated")

            return mairie

        seen_mairies = set()
        for data in response.json():
            code_insee_commune = data["code_insee_commune"]
            if not code_insee_commune:
                continue
            nom = data["nom"]
            if " délégué" in nom:  # ignore "Mairie déléguée" & "Mairie délégué - Lanneray"
                continue
            if " annexe" in nom:
                continue
            if " antenne" in nom.lower():
                continue
            id_service_local = data["id"]
            url_service_public = data["url_service_public"] or ""

            mairie = generate_mairie(code_insee_commune, nom, id_service_local, url_service_public)

            seen_mairies.add(mairie.code_insee_commune)

        # special case: Paris 1, 2, 3, 4
        try:
            mairie_paris_centre = Mairie.objects.get(code_insee_commune="75103")
            nom = mairie_paris_centre.nom
            id_service_local = mairie_paris_centre.id_service_local
            url_service_public = mairie_paris_centre.url_service_public
            for code_insee_commune in ["75101", "75102", "75104"]:
                mairie = generate_mairie(
                    code_insee_commune, nom, id_service_local, url_service_public
                )
                seen_mairies.add(mairie.code_insee_commune)
        except Mairie.DoesNotExist:
            pass

        for to_remove in existing_mairies - seen_mairies:
            Mairie.objects.filter(code_insee_commune=to_remove).delete()
            self.stdout.write(f"Mairie {to_remove} deleted")
