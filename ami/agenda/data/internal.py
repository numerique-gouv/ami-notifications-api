import datetime
from typing import Any, TypedDict

from ami.agenda.data.schemas import Election
from ami.agenda.schemas import AgendaSource, AgendaSourceStatus


class ElectionDict(TypedDict):
    title: str
    description: str
    date: datetime.date


ELECTIONS: list[ElectionDict] = [
    {
        "title": "Élections municipales - Premier tour de scrutin",
        "description": "Votez au premier tour des municipales",
        "date": datetime.date(2026, 3, 15),
    },
    {
        "title": "Élections municipales - Second tour de scrutin",
        "description": "Votez au second tour des municipales",
        "date": datetime.date(2026, 3, 22),
    },
]


def get_elections_data(
    start_date: datetime.date,
    end_date: datetime.date,
) -> list[Election]:
    elections: list[Election] = []
    for election_data in ELECTIONS:
        election_date = election_data["date"]
        if election_date < start_date or election_date > end_date:
            continue
        elections.append(Election.from_dict(dict(**election_data)))
    return elections


def get_elections_source(
    *,
    start_date: datetime.date,
    end_date: datetime.date,
    **kwargs: Any,
) -> AgendaSource:
    elections = get_elections_data(start_date, end_date)
    source = AgendaSource()
    for election in elections:
        source.items.append(election.to_agenda_item())
    source.status = AgendaSourceStatus.SUCCESS
    return source
