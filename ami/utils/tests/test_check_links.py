from io import StringIO
from unittest import mock

from django.core.management import call_command

from ami.checklist.models import CheckList
from ami.page.models import Page, Section
from ami.service.models import Service
from ami.utils.httpx import URL, ReadTimeout


def test_management_command_check_links(db, httpx_mock):
    out = StringIO()
    call_command("check_links", stdout=out)
    assert out.getvalue() == "Pas d’erreur détectée\n"


def test_management_command_check_links_errors_in_services(db, httpx_mock, partner):
    httpx_mock.add_response(url=URL("http://www.example.org"), status_code=200, is_reusable=True)
    httpx_mock.add_response(
        url=URL("http://www.example.org/not-found"), status_code=404, is_reusable=True
    )
    httpx_mock.add_exception(
        ReadTimeout("Unable to read within timeout"), url=URL("http://www.example.com")
    )

    Service.objects.create(
        title="test1", item_type="a", url="http://www.example.org", partner=partner
    )
    Service.objects.create(
        title="test2", item_type="b", url="http://www.example.org/not-found", partner=partner
    )
    Service.objects.create(
        title="test3", item_type="c", url="http://www.example.com", partner=partner
    )

    out = StringIO()
    call_command("check_links", stdout=out)
    assert out.getvalue().startswith("Erreur(s) détectée(s) :")
    assert "http://www.example.org/ok" not in out.getvalue()
    assert (
        "* http://www.example.org/not-found de Service « test2 » : statut HTTP 404"
        in out.getvalue()
    )
    assert (
        "* http://www.example.com de Service « test3 » : Unable to read within timeout"
        in out.getvalue()
    )


def test_management_command_check_links_errors_in_checklists(db, httpx_mock, partner):
    httpx_mock.add_response(url=URL("http://www.example.org"), status_code=200, is_reusable=True)
    httpx_mock.add_response(
        url=URL("http://www.example.org/not-found"), status_code=404, is_reusable=True
    )
    httpx_mock.add_exception(
        ReadTimeout("Unable to read within timeout"), url=URL("http://www.example.com")
    )

    CheckList.objects.create(
        partner=partner,
        external_id="F16225",
        title="liste étapes",
        icon="icon",
        definition={
            "title": "Titre",
            "items": [
                {
                    "text": "**Avant la fin du 3e mois** de grossesse : passer le 1er examen",
                    "id": "e59ab105e3f3",
                    "section": "pendant-la-grossesse",
                    "links": [
                        {
                            "text": "link1",
                            "url": "http://www.example.org",
                        },
                        {
                            "text": "link2",
                            "url": "http://www.example.org/not-found",
                        },
                        {
                            "text": "link3",
                            "url": "http://www.example.com",
                        },
                    ],
                },
            ],
        },
    )

    out = StringIO()
    call_command("check_links", stdout=out)
    assert out.getvalue().startswith("Erreur(s) détectée(s) :")
    assert "http://www.example.org/ok" not in out.getvalue()
    assert (
        "* http://www.example.org/not-found de Liste d’étapes « liste étapes - **Avant la fin du 3e mois** d… » : statut HTTP 404"
        in out.getvalue()
    )
    assert (
        "* http://www.example.com de Liste d’étapes « liste étapes - **Avant la fin du 3e mois** d… » : Unable to read within timeout"
        in out.getvalue()
    )


def test_management_command_check_links_errors_in_pages(db, httpx_mock, partner):
    httpx_mock.add_response(url=URL("http://www.example.org/ok"), status_code=200, is_reusable=True)
    httpx_mock.add_response(
        url=URL("http://www.example.org/not-found"), status_code=404, is_reusable=True
    )
    httpx_mock.add_exception(
        ReadTimeout("Unable to read within timeout"), url=URL("http://www.example.com")
    )

    page = Page.objects.create(slug="test", title="test")
    Section.objects.create(
        page=page,
        slug="section",
        title="section",
        order=0,
        text="""
[test1](http://www.example.org/ok)
[test2](http://www.example.org/not-found)
[test3](http://www.example.com)
                           """,
    )

    out = StringIO()
    call_command("check_links", stdout=out)
    assert out.getvalue().startswith("Erreur(s) détectée(s) :")
    assert "http://www.example.org/ok" not in out.getvalue()
    assert (
        "* http://www.example.org/not-found de Page « test - section » : statut HTTP 404"
        in out.getvalue()
    )
    assert (
        "* http://www.example.com de Page « test - section » : Unable to read within timeout"
        in out.getvalue()
    )


def test_management_command_check_links_errors_send_mail(db, httpx_mock):
    out = StringIO()
    with mock.patch("ami.utils.management.commands.check_links.send_mail") as mock_send:
        mock_send.return_value = None
        call_command("check_links", stdout=out, send=True)
        assert mock_send.call_args[0] == ("[AMI] Scan des liens", "Pas d’erreur détectée\n")
