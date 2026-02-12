import datetime
from typing import Any, TypedDict

from app.schemas import AgendaCatalog, AgendaCatalogStatus, Election


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


async def get_elections_catalog(
    *,
    start_date: datetime.date,
    end_date: datetime.date,
    **kwargs: Any,
) -> AgendaCatalog:
    elections = get_elections_data(start_date, end_date)
    catalog = AgendaCatalog()
    for election in elections:
        catalog.items.append(election.to_catalog_item())
    catalog.status = AgendaCatalogStatus.SUCCESS
    return catalog
