import datetime
import uuid
from unittest import mock

import pytest
from django.utils.timezone import now

from ami.agenda.data.marronniers import get_marronniers_data, get_marronniers_source
from ami.agenda.data.schemas import Marronnier
from ami.agenda.models import SpActuItem
from ami.agenda.schemas import (
    AgendaItem,
    AgendaItemKind,
    AgendaSource,
    AgendaSourceStatus,
)


@pytest.mark.django_db
def test_get_marronniers_data() -> None:
    SpActuItem.objects.create(
        title="Campagne de vaccination contre la grippe saisonnière",
        themes=["Social - Santé", "Famille - Scolarité"],
        date=datetime.date(2027, 1, 4),
        url="url",
        start_date=None,
        end_date=None,
        external_id=str(uuid.uuid4()),
        initial_publication_date=now(),
    )
    SpActuItem.objects.create(
        title="Inscription sur les listes électorales",
        themes=["Papiers - Citoyenneté - Élections"],
        date=None,
        start_date=datetime.date(2027, 1, 4),
        end_date=None,
        external_id=str(uuid.uuid4()),
        initial_publication_date=now(),
    )
    SpActuItem.objects.create(
        title="Information importante",
        themes=["inconnu"],
        date=None,
        start_date=None,
        end_date=datetime.date(2027, 1, 4),
        external_id=str(uuid.uuid4()),
        initial_publication_date=now(),
    )
    SpActuItem.objects.create(
        title="Information importante",
        themes=["inconnu"],
        date=None,
        start_date=datetime.date(2027, 1, 1),
        end_date=datetime.date(2027, 1, 4),
        external_id=str(uuid.uuid4()),
        initial_publication_date=now(),
    )

    result = get_marronniers_data()
    assert result == [
        Marronnier(
            kinds=[AgendaItemKind.CARE, AgendaItemKind.FAMILY],
            title="Campagne de vaccination contre la grippe saisonnière",
            date=datetime.date(2027, 1, 4),
            start_date=None,
            end_date=None,
            url="url",
        ),
        Marronnier(
            kinds=[AgendaItemKind.CITIZENSHIP],
            title="Inscription sur les listes électorales",
            date=None,
            start_date=datetime.date(2027, 1, 4),
            end_date=None,
        ),
        Marronnier(
            kinds=[AgendaItemKind.OTHER],
            title="Information importante",
            date=None,
            start_date=None,
            end_date=datetime.date(2027, 1, 4),
        ),
        Marronnier(
            kinds=[AgendaItemKind.OTHER],
            title="Information importante",
            date=None,
            start_date=datetime.date(2027, 1, 1),
            end_date=datetime.date(2027, 1, 4),
        ),
    ]


def test_get_marronniers_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marronniers = [
        Marronnier(
            kinds=[AgendaItemKind.CARE, AgendaItemKind.FAMILY],
            title="Campagne de vaccination contre la grippe saisonnière",
            date=datetime.date(2027, 1, 4),
            url="url",
        ),
        Marronnier(
            kinds=[AgendaItemKind.CITIZENSHIP],
            title="Inscription sur les listes électorales",
            start_date=datetime.date(2027, 2, 1),
        ),
        Marronnier(
            kinds=[AgendaItemKind.OTHER],
            title="Information importante",
            end_date=datetime.date(2027, 3, 1),
        ),
    ]
    data_mock = mock.Mock(return_value=marronniers)
    monkeypatch.setattr("ami.agenda.data.marronniers.get_marronniers_data", data_mock)
    result = get_marronniers_source()
    items = [
        AgendaItem(
            kinds=[AgendaItemKind.CARE, AgendaItemKind.FAMILY],
            title="Campagne de vaccination contre la grippe saisonnière",
            description="",
            date=datetime.date(2027, 1, 4),
            start_date=None,
            end_date=None,
            zones=[],
            emoji="",
            url="url",
        ),
        AgendaItem(
            kinds=[AgendaItemKind.CITIZENSHIP],
            title="Inscription sur les listes électorales",
            description="",
            date=None,
            start_date=datetime.date(2027, 2, 1),
            end_date=None,
            zones=[],
            emoji="",
        ),
        AgendaItem(
            kinds=[AgendaItemKind.OTHER],
            title="Information importante",
            description="",
            date=None,
            start_date=None,
            end_date=datetime.date(2027, 3, 1),
            zones=[],
            emoji="",
        ),
    ]
    assert result == AgendaSource(status=AgendaSourceStatus.SUCCESS, items=items)
