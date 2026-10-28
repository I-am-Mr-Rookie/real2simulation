import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "worker_timebox", Path(__file__).resolve().parents[1] / "worker_timebox.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class WorkerTimeboxTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 10, 28, 14, 0, tzinfo=timezone.utc)
        self.now = self.start + timedelta(minutes=31)
        self.receipt = mod.issue("test", self.start)
        self.receipt.update(status="PARTIAL", work_stopped_at=self.receipt["deadline_at"],
                            reported_at=self.now.isoformat())

    def test_full_window_and_dhaka(self):
        self.assertEqual(self.receipt["deadline_dhaka"], "2026-10-28T20:30:00+06:00")
        self.assertIn("TIMING PASS", mod.check(self.receipt, self.now))

    def test_early_incomplete_rejected(self):
        for status in ("PARTIAL", "BLOCKED"):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "EARLY"):
                mod.check(dict(self.receipt, status=status,
                               work_stopped_at=(self.start + timedelta(minutes=5)).isoformat()), self.now)

    def test_done_can_finish_early(self):
        self.assertIn("TIMING PASS", mod.check(dict(self.receipt, status="DONE",
                          work_stopped_at=(self.start + timedelta(minutes=5)).isoformat()), self.now))

    def test_short_dispatch_and_overrun_rejected(self):
        for updates in ({"deadline_at": (self.start + timedelta(minutes=20)).isoformat()},
                        {"work_stopped_at": self.now.isoformat()}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                mod.check(dict(self.receipt, **updates), self.now)

    def test_exception_requires_real_receipt(self):
        early = dict(self.receipt, work_stopped_at=self.start.isoformat())
        with self.assertRaises(ValueError):
            mod.check(dict(early, controller_exception={"reason": "safety"}), self.now)
        self.assertIn("TIMING PASS", mod.check(dict(early, controller_exception={
            "reason": "safety", "approval_receipt": "controller-reviewed-stop.md"}), self.now))

    def test_naive_and_future_rejected(self):
        with self.assertRaises(ValueError):
            mod.timestamp("2026-10-28T14:00:00")
        with self.assertRaises(ValueError):
            mod.check(self.receipt, self.start)


if __name__ == "__main__":
    unittest.main()
