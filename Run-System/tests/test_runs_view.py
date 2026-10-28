"""Offline regression checks for the generated manual-run checklist."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "runs_view", Path(__file__).resolve().parents[1] / "runs_view.py")
view = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(view)


class RetryHoldTests(unittest.TestCase):
    def render(self, now="2026-10-27T19:14:00+00:00", deadline="2026-10-27T20:10:00Z",
               dependency="DONE", status="PARTIAL", include_hold=True, hold_id="S02c"):
        class FrozenDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return datetime.fromisoformat(now).astimezone(tz)

        queue = (
            "## Leaf tasks\n"
            "| ID | Lane | Model / effort | Step | Min | Task | Depends | Owns | Acceptance | Status |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            f"| S02b | CODEX-2 | Terra / high | S02 | 30 | Source | — | clips/ | Check | {dependency} |\n"
            f"| S02c | CODEX-2 | Terra / high | S02 | 30 | Acquire clips | S02b | clips/ | Check | {status} |\n"
        )
        if include_hold:
            queue += (
                "\n## Retry holds\n\n"
                "| Run | Retry not before (UTC) | Reason |\n"
                "|---|---|---|\n"
                f"| {hold_id} | {deadline} | HTTP 429/403; do not bypass source restrictions. |\n"
            )
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "QUEUE.md").write_text(queue, encoding="utf-8")
            (root / "STATE.md").write_text("## Owner questions\n", encoding="utf-8")
            with patch.multiple(view, QUEUE=root / "QUEUE.md", STATE=root / "STATE.md",
                                OUT=root / "RUNS.md", datetime=FrozenDatetime):
                view.main()
            return (root / "RUNS.md").read_text(encoding="utf-8")

    def ready_section(self, rendered):
        return rendered.split("## Ready now\n", 1)[1].split("\n## ", 1)[0]

    def test_rate_limited_partial_is_waiting_not_ready(self):
        output = self.render()
        self.assertNotIn("**S02c**", self.ready_section(output))
        self.assertIn("## Waiting to retry", output)
        self.assertIn("Oct 27, 20:10 UTC / Oct 28, 02:10 Dhaka", output)
        self.assertIn("HTTP 429/403", output)
        self.assertNotIn("partial: resume it", output)

    def test_one_second_before_deadline_still_waits(self):
        self.assertNotIn("**S02c**", self.ready_section(
            self.render(now="2026-10-27T20:09:59+00:00")))

    def test_at_deadline_bounded_retry_eligible_not_recovery(self):
        output = self.render(now="2026-10-27T20:10:00+00:00")
        self.assertIn("**S02c**", self.ready_section(output))
        self.assertIn("bounded retry eligible; source recovery unverified", output)
        self.assertNotIn("## Waiting to retry", output)

    def test_expired_hold_does_not_override_dependency(self):
        self.assertNotIn("**S02c**", self.ready_section(
            self.render(now="2026-10-27T21:00:00+00:00", dependency="TODO")))

    def test_partial_without_hold_keeps_existing_resume_behavior(self):
        output = self.render(include_hold=False)
        self.assertIn("**S02c**", self.ready_section(output))
        self.assertIn("partial: resume it", output)

    def test_done_task_not_reintroduced_by_hold(self):
        output = self.render(status="DONE")
        self.assertNotIn("**S02c**", self.ready_section(output))
        self.assertNotIn("## Waiting to retry", output)

    def test_malformed_or_timezone_naive_deadline_fails_closed(self):
        for deadline in ("later", "2026-10-27T20:10:00", "2026-10-28T02:10:00+06:00"):
            with self.subTest(deadline=deadline), self.assertRaises(ValueError):
                self.render(deadline=deadline)

    def test_unknown_task_hold_fails_closed(self):
        with self.assertRaises(ValueError):
            self.render(hold_id="S99z")


if __name__ == "__main__":
    unittest.main()
