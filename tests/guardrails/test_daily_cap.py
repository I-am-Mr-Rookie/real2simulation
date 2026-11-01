import threading
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from Build.guardrails import daily_cap as dc

NOV1 = datetime(2026, 11, 1, 6, 0, tzinfo=timezone.utc)  # 12:00 Dhaka


def test_cap_edge_equal_allowed_any_more_refused(tmp_path):
    db = tmp_path / "s.db"
    dc.reserve("Modal", "9.99", path=db, now=NOV1)
    dc.reserve("Meta Model API", "0.01", path=db, now=NOV1)  # exactly $10: allowed
    with pytest.raises(dc.CapExceeded):
        dc.reserve("Modal", "0.00000001", path=db, now=NOV1)
    assert dc.today(path=db, now=NOV1)["headroom_usd"] == 0


def test_dhaka_day_boundary(tmp_path):
    db = tmp_path / "s.db"
    dc.reserve("Modal", "10", path=db, now=datetime(2026, 11, 1, 17, 59, tzinfo=timezone.utc))  # 23:59 Dhaka Nov 1
    dc.reserve("Modal", "10", path=db, now=datetime(2026, 11, 1, 18, 0, tzinfo=timezone.utc))  # 00:00 Dhaka Nov 2


@pytest.mark.parametrize("utc, cap", [
    (datetime(2026, 11, 4, 17, 59, tzinfo=timezone.utc), 10),  # Nov 4 23:59 Dhaka
    (datetime(2026, 11, 4, 18, 0, tzinfo=timezone.utc), 20),  # Nov 5 00:00 Dhaka
    (datetime(2026, 11, 8, 17, 59, tzinfo=timezone.utc), 20),  # Nov 8 23:59 Dhaka
    (datetime(2026, 11, 8, 18, 0, tzinfo=timezone.utc), 10),  # Nov 9 00:00 Dhaka
    (datetime(2027, 11, 6, 6, 0, tzinfo=timezone.utc), 10),  # same dates, other year
])
def test_judging_dates(tmp_path, utc, cap):
    db = tmp_path / "s.db"
    dc.reserve("Modal", cap, path=db, now=utc)
    with pytest.raises(dc.CapExceeded):
        dc.reserve("Modal", "0.01", path=db, now=utc)


def test_concurrent_reserve_never_overshoots(tmp_path):
    db = tmp_path / "s.db"
    dc.today(path=db)  # create the table before the race
    ok, refused = [], []

    def go():
        try:
            ok.append(dc.reserve("Modal", "1", path=db, now=NOV1))
        except dc.CapExceeded:
            refused.append(1)

    threads = [threading.Thread(target=go) for _ in range(25)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert len(ok) == 10 and len(refused) == 15
    assert dc.today(path=db, now=NOV1)["spent_usd"] == Decimal("10")


def test_settle_lower_frees_headroom_and_settles_once(tmp_path):
    db = tmp_path / "s.db"
    rid = dc.reserve("Modal", "8", path=db, now=NOV1)
    with pytest.raises(dc.CapExceeded):
        dc.reserve("Modal", "3", path=db, now=NOV1)
    dc.settle(rid, "1.5", path=db)
    dc.reserve("Modal", "3", path=db, now=NOV1)
    assert dc.today(path=db, now=NOV1)["spent_usd"] == Decimal("4.5")
    with pytest.raises(ValueError):
        dc.settle(rid, "0", path=db)
    with pytest.raises(ValueError):
        dc.settle("nope", "0", path=db)


def test_rejects_bad_input(tmp_path):
    db = tmp_path / "s.db"
    for bad in (-1, "nan", None, True):
        with pytest.raises(ValueError):
            dc.reserve("Modal", bad, path=db, now=NOV1)
    with pytest.raises(ValueError):
        dc.reserve("OpenAI", "1", path=db, now=NOV1)
