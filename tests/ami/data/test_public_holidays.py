import datetime

from app.data.holidays import get_public_holidays_data
from app.schemas import PublicHoliday


async def test_get_public_holidays_data() -> None:
    result = get_public_holidays_data(datetime.date(2025, 11, 12), datetime.date(2026, 9, 15))
    assert result == [
        PublicHoliday(description="Noël", date=datetime.date(2025, 12, 25), emoji="📅"),
        PublicHoliday(description="Jour de l’An", date=datetime.date(2026, 1, 1), emoji="🎉"),
        PublicHoliday(description="Lundi de Pâques", date=datetime.date(2026, 4, 6), emoji="📅"),
        PublicHoliday(description="Fête du Travail", date=datetime.date(2026, 5, 1), emoji="📅"),
        PublicHoliday(description="Victoire 1945", date=datetime.date(2026, 5, 8), emoji="📅"),
        PublicHoliday(description="Ascension", date=datetime.date(2026, 5, 14), emoji="📅"),
        PublicHoliday(
            description="Lundi de Pentecôte", date=datetime.date(2026, 5, 25), emoji="📅"
        ),
        PublicHoliday(description="Fête Nationale", date=datetime.date(2026, 7, 14), emoji="🎆"),
        PublicHoliday(description="Assomption", date=datetime.date(2026, 8, 15), emoji="📅"),
    ]
