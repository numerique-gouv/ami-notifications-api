from typing import Any

from ami.agenda.data.schemas import Marronnier
from ami.agenda.models import SpActuItem
from ami.agenda.schemas import AgendaSource, AgendaSourceStatus


def get_marronniers_data() -> list[Marronnier]:
    marronniers: list[Marronnier] = []

    for item in SpActuItem.objects.all():
        marronniers.append(Marronnier.from_sp_actu_item(item))
    return marronniers


def get_marronniers_source(
    **kwargs: Any,
) -> AgendaSource:
    marronniers = get_marronniers_data()
    source = AgendaSource()
    for marronnier in marronniers:
        source.items.append(marronnier.to_agenda_item())
    source.status = AgendaSourceStatus.SUCCESS
    return source
