import pytest
from django.core.management import call_command
from pytest_httpx import HTTPXMock

from ami.annuaire_sp.models import Mairie


@pytest.mark.django_db
def test_management_command_init_annuaire(
    app,
    httpx_mock: HTTPXMock,
):
    fake_mairie_data = [
        {
            "nom": "Mairie 1",
            "code_insee_commune": "00001",
            "id": "id1",
            "url_service_public": "url1",
        },
        {
            "nom": "Mairie 2",
            "code_insee_commune": "00002",
            "id": "id2",
            "url_service_public": "url2",
        },
        {
            "nom": "Mairie 3",
            "code_insee_commune": "00003",
            "id": "id3",
            "url_service_public": "url3",
        },
        {
            "nom": "Mairie annexe",  # ignored
            "code_insee_commune": "00004",
            "id": "id4",
            "url_service_public": "url4",
        },
        {
            "nom": "Mairie antenne",  # ignored
            "code_insee_commune": "00005",
            "id": "id5",
            "url_service_public": "url5",
        },
        {
            "nom": "Mairie (encore annexe)",  # ignored
            "code_insee_commune": "00006",
            "id": "id6",
            "url_service_public": "url6",
        },
        {
            "nom": "Mairie délégué",  # ignored
            "code_insee_commune": "00007",
            "id": "id7",
            "url_service_public": "url7",
        },
    ]

    httpx_mock.add_response(
        json=fake_mairie_data,
    )

    assert Mairie.objects.count() == 0

    call_command("init_annuaire")

    assert Mairie.objects.count() == 3
    assert list(
        Mairie.objects.values_list("code_insee_commune", flat=True).order_by("code_insee_commune")
    ) == ["00001", "00002", "00003"]


@pytest.mark.django_db
def test_management_command_init_annuaire_update(
    app,
    httpx_mock: HTTPXMock,
):
    mairie1 = Mairie.objects.create(
        nom="Mairie 11",
        code_insee_commune="00001",
        id_service_local="id1",
        url_service_public="url1",
    )
    mairie2 = Mairie.objects.create(
        nom="Mairie 2",
        code_insee_commune="00002",
        id_service_local="id22",
        url_service_public="url1",
    )
    mairie3 = Mairie.objects.create(
        nom="Mairie 3",
        code_insee_commune="00003",
        id_service_local="id3",
        url_service_public="url33",
    )
    mairie4 = Mairie.objects.create(
        nom="Mairie 4",
        code_insee_commune="00004",
        id_service_local="id4",
        url_service_public="url4",
    )

    fake_mairie_data = [
        {
            "nom": "Mairie 1",
            "code_insee_commune": "00001",
            "id": "id1",
            "url_service_public": "url1",
        },
        {
            "nom": "Mairie 2",
            "code_insee_commune": "00002",
            "id": "id2",
            "url_service_public": "url2",
        },
        {
            "nom": "Mairie 3",
            "code_insee_commune": "00003",
            "id": "id3",
            "url_service_public": "url3",
        },
        {
            "nom": "Mairie 4",
            "code_insee_commune": "00004",
            "id": "id4",
            "url_service_public": "url4",
        },
    ]

    httpx_mock.add_response(
        json=fake_mairie_data,
    )

    call_command("init_annuaire")

    assert Mairie.objects.count() == 4
    assert list(
        Mairie.objects.values_list("code_insee_commune", flat=True).order_by("code_insee_commune")
    ) == ["00001", "00002", "00003", "00004"]

    new_mairie1 = Mairie.objects.get(code_insee_commune="00001")
    assert new_mairie1.updated_at > mairie1.updated_at
    assert new_mairie1.created_at == mairie1.created_at
    new_mairie2 = Mairie.objects.get(code_insee_commune="00002")
    assert new_mairie2.updated_at > mairie2.updated_at
    assert new_mairie2.created_at == mairie2.created_at
    new_mairie3 = Mairie.objects.get(code_insee_commune="00003")
    assert new_mairie3.updated_at > mairie3.updated_at
    assert new_mairie3.created_at == mairie3.created_at
    new_mairie4 = Mairie.objects.get(code_insee_commune="00004")
    assert new_mairie4.updated_at == mairie4.updated_at
    assert new_mairie4.created_at == mairie4.created_at


@pytest.mark.django_db
def test_management_command_init_annuaire_delete(
    app,
    httpx_mock: HTTPXMock,
):
    Mairie.objects.create(
        nom="Mairie 99",
        code_insee_commune="00099",
        id_service_local="id99",
        url_service_public="url99",
    )

    fake_mairie_data = [
        {
            "nom": "Mairie 1",
            "code_insee_commune": "00001",
            "id": "id1",
            "url_service_public": "url1",
        },
        {
            "nom": "Mairie 2",
            "code_insee_commune": "00002",
            "id": "id2",
            "url_service_public": "url2",
        },
    ]

    httpx_mock.add_response(
        json=fake_mairie_data,
    )

    call_command("init_annuaire")

    assert Mairie.objects.count() == 2
    assert list(
        Mairie.objects.values_list("code_insee_commune", flat=True).order_by("code_insee_commune")
    ) == ["00001", "00002"]


@pytest.mark.django_db
def test_management_command_init_annuaire_paris(
    app,
    httpx_mock: HTTPXMock,
):
    fake_mairie_data = [
        {
            "nom": "Mairie Paris-Centre ",
            "code_insee_commune": "75103",
            "id": "id75103",
            "url_service_public": "url75103",
        },
    ]

    httpx_mock.add_response(
        json=fake_mairie_data,
    )

    call_command("init_annuaire")

    assert Mairie.objects.count() == 4
    assert list(
        Mairie.objects.values_list("code_insee_commune", flat=True).order_by("code_insee_commune")
    ) == ["75101", "75102", "75103", "75104"]
