import datetime

from freezegun import freeze_time
from freezegun.api import FakeDatetime

from app.data.schemas import DurationExpiration, MonthlyExpiration, TimeUnit


@freeze_time("2026-02-13 11:16:00")
def test_duration_expiration():
    rule = DurationExpiration(amount=1, unit=TimeUnit.SECONDS)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 2, 13, 11, 16, 1, tzinfo=datetime.timezone.utc
    )

    rule = DurationExpiration(amount=75, unit=TimeUnit.SECONDS)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 2, 13, 11, 17, 15, tzinfo=datetime.timezone.utc
    )

    rule = DurationExpiration(amount=1, unit=TimeUnit.MINUTES)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 2, 13, 11, 17, tzinfo=datetime.timezone.utc
    )

    rule = DurationExpiration(amount=75, unit=TimeUnit.MINUTES)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 2, 13, 12, 31, tzinfo=datetime.timezone.utc
    )

    rule = DurationExpiration(amount=1, unit=TimeUnit.HOURS)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 2, 13, 12, 16, tzinfo=datetime.timezone.utc
    )

    rule = DurationExpiration(amount=35, unit=TimeUnit.HOURS)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 2, 14, 22, 16, tzinfo=datetime.timezone.utc
    )

    rule = DurationExpiration(amount=1, unit=TimeUnit.DAYS)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 2, 14, 11, 16, tzinfo=datetime.timezone.utc
    )

    rule = DurationExpiration(amount=30, unit=TimeUnit.DAYS)
    assert rule.compute_expires_at() == FakeDatetime(
        2026, 3, 15, 11, 16, tzinfo=datetime.timezone.utc
    )


def test_monthly_expiration():
    with freeze_time("2026-02-01 00:00:00"):
        rule = MonthlyExpiration()
        assert rule.compute_expires_at() == FakeDatetime(2026, 3, 1, tzinfo=datetime.timezone.utc)

    with freeze_time("2026-02-13 11:16:00"):
        rule = MonthlyExpiration()
        assert rule.compute_expires_at() == FakeDatetime(2026, 3, 1, tzinfo=datetime.timezone.utc)

    with freeze_time("2026-02-28 23:59:59"):
        rule = MonthlyExpiration()
        assert rule.compute_expires_at() == FakeDatetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
