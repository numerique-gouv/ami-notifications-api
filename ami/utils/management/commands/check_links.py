import asyncio

import markdown
import pyquery
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils.text import Truncator

from ami.checklist.models import CheckList
from ami.page.models import Section
from ami.service.models import Service
from ami.utils import httpx


class Command(BaseCommand):
    help = "Check links"

    def add_arguments(self, parser):
        parser.add_argument("--send", action="store_true")

    def handle(self, verbosity=1, **options):
        # collect links
        urls = set()
        links = []

        def collect_link(origin, url):
            if not url or url.startswith("/") or url.startswith("mailto:"):
                return
            if url in urls:
                return
            links.append({"origin": origin, "url": url})
            urls.add(url)

        for service_title, service_url in Service.objects.all().values_list("title", "url"):
            collect_link(f"Service « {service_title} »", service_url)

        for checklist in CheckList.objects.all():
            for item in checklist.definition.get("items") or []:
                source = (
                    f"Liste d’étapes « {checklist.title} - {Truncator(item['text']).chars(30)} »"
                )
                for link in item.get("links") or []:
                    collect_link(source, link["url"])

        for section in Section.objects.all().select_related("page"):
            source = f"Page « {section.page.title} - {section.title} »"
            for a_tag in pyquery.PyQuery(markdown.markdown(section.text)).find("a[href]"):
                collect_link(source, a_tag.attrib["href"])

        errors = asyncio.run(self.check_links(links, verbosity))
        if errors:
            msg = f"Erreur(s) détectée(s) :\n\n{errors}\n"
        else:
            msg = "Pas d’erreur détectée\n"

        if options.get("send"):
            subject = "[AMI] Scan des liens"
            send_mail(
                subject, msg, from_email=None, recipient_list=[settings.LINK_CHECKER_REPORT_EMAIL]
            )
        else:
            self.stdout.write(msg)

    async def check_links(self, links, verbosity):
        headers = {
            "User-Agent": f"AMI/0.0 (link checker, {settings.LINK_CHECKER_REPORT_EMAIL})",
        }

        async def check_link(link):
            async with httpx.httpxAsyncClient() as client:
                try:
                    resp = await client.get(link["url"], headers=headers)
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    link["success"] = False
                    link["error"] = str(e)
                    if isinstance(e, httpx.HTTPStatusError):
                        link["error"] = f"statut HTTP {e.response.status_code}"
                else:
                    link["success"] = True
            return link["url"]

        await asyncio.gather(*(check_link(link) for link in links))

        return "\n".join(
            f"* {link['url']} de {link['origin']} : {link['error']}"
            for link in links
            if link.get("error")
        )
