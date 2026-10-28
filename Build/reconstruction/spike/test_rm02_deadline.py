"""Deterministic fake-only caller policy tests; never import the Modal runner."""
import asyncio
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import rm02_deadline as guard


def api(fn):
    return NS(aio=fn)


class Fake:
    def __init__(self):
        self.now = 0
        self.setup_delay = self.spawn_delay = 0
        self.running = True
        self.result = ("receipt", b"fake")
        self.failure = None
        self.hang = False
        self.stop_failure = self.verify_failure = self.exit_failure = False
        self.stopped = False
        self.stop_calls = self.spawn_calls = self.exit_calls = 0
        self.records = []
        self.app_id = None
        self.object_id = "fc-fake"
        self.run = api(lambda: self)
        self.spawn = api(self.do_spawn)
        self.get = api(self.do_get)
        self.get_current_stats = api(self.stats)
        self.stop = api(self.do_stop)
        self.info = api(self.do_info)

    async def __aenter__(self):
        self.app_id = "ap-fake"
        self.now += self.setup_delay
        return self

    async def __aexit__(self, *args):
        self.exit_calls += 1
        if self.exit_failure:
            raise RuntimeError("fake exit error")

    async def do_spawn(self, *args):
        self.spawn_calls += 1
        self.now += self.spawn_delay
        return self

    async def do_get(self, *, timeout):
        assert timeout > 0
        if self.hang:
            await asyncio.Event().wait()
        if self.failure:
            raise self.failure
        return self.result

    async def stats(self):
        await asyncio.sleep(0)
        return NS(num_running_inputs=int(self.running and not self.stopped),
                  num_total_runners=int(not self.stopped), backlog=int(not self.stopped))

    async def do_stop(self):
        self.stop_calls += 1
        if self.stop_failure:
            raise RuntimeError("fake stop failure")
        self.stopped = True

    async def do_info(self, *, refresh):
        assert refresh is True
        if self.verify_failure:
            raise RuntimeError("fake verification failure")
        return NS(lifecycle=NS(state="stopped" if self.stopped else "stopping"))

    async def sleep(self, seconds):
        self.now += seconds
        await asyncio.sleep(0)

    async def execute(self, **kwargs):
        return await guard.guarded_probe(self, self, (), self.records.append,
                                        clock=lambda: self.now, sleep=self.sleep, **kwargs)


class DeadlineTests(unittest.IsolatedAsyncioTestCase):
    async def test_absolute_deadline_consumes_preflight_time(self):
        f = Fake()
        f.now = 100
        f.running = False
        f.hang = True
        with self.assertRaises(TimeoutError):
            await f.execute(deadline=1200)
        self.assertEqual(f.now, 150)  # Not250: child startup cannot restart the clock.
        self.assertEqual(f.records[-1]["absolute_deadline_monotonic"], 1200)
        self.assertEqual(f.records[-1]["remaining_at_start_s"], 1100)
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])

    async def test_absolute_deadline_cannot_extend_relative_budget(self):
        f = Fake()
        f.running = False
        f.hang = True
        with self.assertRaises(TimeoutError):
            await f.execute(deadline=10000)
        self.assertEqual(f.now, 150)
        self.assertEqual(f.records[-1]["absolute_deadline_monotonic"], 1200)

    async def test_exhausted_absolute_deadline_never_enters_remote_setup(self):
        for deadline in (1049, 1050):
            f = Fake()
            with self.assertRaises(TimeoutError):
                await f.execute(deadline=deadline)
            self.assertIsNone(f.app_id)
            self.assertEqual(f.spawn_calls, 0)

    async def test_invalid_absolute_deadline_never_enters_remote_setup(self):
        for deadline in (float("nan"), float("inf"), -1):
            f = Fake()
            with self.assertRaises(ValueError):
                await f.execute(deadline=deadline)
            self.assertIsNone(f.app_id)

    async def test_result_is_saved_before_stop_and_failed_cleanup_is_not_success(self):
        f = Fake()
        saved = []
        def save(result):
            self.assertEqual(f.stop_calls, 0)
            saved.append(result)
        f.exit_failure = True
        with self.assertRaises(guard.ResourceIncident):
            await f.execute(save_result=save)
        self.assertEqual(saved, [f.result])
        self.assertTrue(f.records[-1]["result_persisted"])
        self.assertTrue(f.records[-1]["resource_incident"])

    async def test_persistence_failure_still_stops_and_preserves_original_error(self):
        f = Fake()
        def save(result):
            raise OSError("synthetic disk failure")
        with self.assertRaisesRegex(OSError, "synthetic disk failure"):
            await f.execute(save_result=save)
        self.assertEqual(f.stop_calls, 1)
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])
        self.assertNotIn("result_persisted", f.records[-1])

    async def test_already_expired_clock_still_invokes_stop(self):
        f = Fake()
        f.setup_delay = 1500
        with self.assertRaises(TimeoutError):
            await f.execute()
        self.assertEqual(f.stop_calls, 1)
        final = f.records[-1]
        self.assertTrue(final["stop_attempted"])
        self.assertTrue(final["stop_acknowledged"])
        self.assertTrue(final["remote_stop_confirmed"])
        self.assertEqual(final["caller_error"], "TimeoutError")

    async def test_stop_invocation_not_recorded_as_rpc_dispatch_without_ack(self):
        f = Fake()
        f.stop_failure = True
        with self.assertRaises(guard.ResourceIncident):
            await f.execute()
        self.assertTrue(f.records[-1]["stop_attempted"])
        self.assertEqual(f.records[-1]["stop_dispatched"], "NOT_VERIFIED")

    async def test_late_stop_ack_is_recorded_without_claiming_timely_success(self):
        f = Fake()
        async def late_stop():
            f.stop_calls += 1
            f.stopped = True
            f.now += guard.STOP_SECONDS + 1
        f.stop = api(late_stop)
        with self.assertRaises(guard.ResourceIncident):
            await f.execute()
        self.assertTrue(f.records[-1]["stop_acknowledged"])
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])
        self.assertIn("stop:TimeoutError", f.records[-1]["cleanup_errors"])

    async def test_slow_cancellation_overshoot_preserves_timeout_and_stops(self):
        f = Fake()
        async def late_enter():
            f.app_id = "ap-fake"
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                await asyncio.sleep(.8)
        f.__class__ = type("LateFake", (Fake,), {"__aenter__": lambda self: late_enter()})
        # Windows CPython 3.11 monotonic ticks can be 15.6ms; avoid sub-tick budgets.
        with (patch.object(guard, "STARTUP_SECONDS", .1),
              patch.object(guard, "EXECUTION_SECONDS", .1),
              patch.object(guard, "CLEANUP_SECONDS", .4),
              patch.object(guard, "EXIT_SECONDS", .1)):
            with self.assertRaises(TimeoutError):
                await guard.guarded_probe(f, f, (), f.records.append, total_seconds=1)
        self.assertEqual(f.stop_calls, 1)
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])

    async def test_app_id_published_before_noncooperative_setup_finishes(self):
        f = Fake()
        release = asyncio.Event()
        published = asyncio.Event()
        async def slow_enter():
            f.app_id = "ap-fake"
            await release.wait()
        f.__class__ = type("SlowFake", (Fake,), {"__aenter__": lambda self: slow_enter()})
        def record(state):
            f.records.append(state)
            published.set()
        task = asyncio.create_task(guard.guarded_probe(
            f, f, (), record, clock=lambda: f.now, sleep=f.sleep))
        try:
            await asyncio.wait_for(published.wait(), timeout=2)
            self.assertFalse(task.done())
            self.assertEqual(f.records[0]["app_id"], "ap-fake")
        finally:
            release.set()
            await task

    async def test_success_stops_and_confirms_before_return(self):
        f = Fake()
        self.assertEqual(await f.execute(), f.result)
        self.assertEqual((f.spawn_calls, f.stop_calls, f.exit_calls), (1, 1, 1))
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])
        self.assertFalse(f.records[-1]["resource_incident"])

    async def test_impossible_and_nonfinite_budget_never_sets_up(self):
        for budget in (0, 1050, float("nan"), float("inf")):
            f = Fake()
            with self.assertRaises(ValueError):
                await f.execute(total_seconds=budget)
            self.assertIsNone(f.app_id)
            self.assertEqual(f.spawn_calls, 0)

    async def test_setup_consumes_admission_budget(self):
        f = Fake()
        f.setup_delay = 151
        with self.assertRaises(TimeoutError):
            await f.execute()
        self.assertEqual(f.spawn_calls, 0)
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])
        self.assertEqual(f.exit_calls, 1)

    async def test_completed_result_does_not_require_running_snapshot(self):
        f = Fake()
        f.running = False
        self.assertEqual(await f.execute(), f.result)
        self.assertTrue(f.records[-1]["result_received"])
        self.assertFalse(f.records[-1]["admission_observed"])

    async def test_enqueue_timeout_without_call_handle_still_stops_app(self):
        f = Fake()
        f.spawn_delay = 151
        with self.assertRaises(TimeoutError):
            await f.execute()
        self.assertEqual(f.stop_calls, 1)
        self.assertNotIn("function_call_id", f.records[-1])

    async def test_slow_queue_stops_at_admission_cutoff(self):
        f = Fake()
        f.running = False
        f.hang = True
        with self.assertRaises(TimeoutError):
            await f.execute()
        self.assertEqual(f.now, 150)
        self.assertFalse(f.records[-1]["admission_observed"])
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])

    async def test_remote_exception_preserved_after_confirmed_cleanup(self):
        f = Fake()
        f.failure = ValueError("fake remote error")
        with self.assertRaisesRegex(ValueError, "fake remote error"):
            await f.execute()
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])

    async def test_stop_failure_is_incident_not_success(self):
        f = Fake()
        f.stop_failure = True
        with self.assertRaises(guard.ResourceIncident):
            await f.execute()
        self.assertTrue(f.records[-1]["stop_requested"])
        self.assertFalse(f.records[-1]["stop_acknowledged"])
        self.assertFalse(f.records[-1]["remote_stop_confirmed"])

    async def test_acknowledged_stop_without_fresh_confirmation_is_incident(self):
        f = Fake()
        f.verify_failure = True
        with self.assertRaises(guard.ResourceIncident):
            await f.execute()
        self.assertTrue(f.records[-1]["stop_acknowledged"])
        self.assertFalse(f.records[-1]["remote_stop_confirmed"])

    async def test_context_cleanup_failure_is_incident(self):
        f = Fake()
        f.exit_failure = True
        with self.assertRaises(guard.ResourceIncident):
            await f.execute()
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])

    async def test_real_local_timer_bounds_hanging_get(self):
        f = Fake()
        f.hang = True
        with (patch.object(guard, "STARTUP_SECONDS", .1),
              patch.object(guard, "EXECUTION_SECONDS", .1),
              patch.object(guard, "CLEANUP_SECONDS", .4),
              patch.object(guard, "EXIT_SECONDS", .1)):
            with self.assertRaises(TimeoutError):
                await guard.guarded_probe(f, f, (), f.records.append, total_seconds=1.5)
        self.assertTrue(f.records[-1]["remote_stop_confirmed"])
        self.assertLess(f.records[-1]["elapsed_s"], 1.5)

    async def test_unobserved_setup_state_is_incident(self):
        f = Fake()
        async def failed_enter():
            raise ConnectionError("setup response lost")
        class Context:
            __aenter__ = staticmethod(failed_enter)
        f.run = api(Context)
        with self.assertRaises(guard.ResourceIncident):
            await f.execute()
        self.assertEqual(f.spawn_calls, 0)
        self.assertIn("setup:unknown_remote_state", f.records[-1]["cleanup_errors"])

    async def test_broken_evidence_write_does_not_skip_stop(self):
        f = Fake()
        def broken_record(state):
            raise OSError("disk unavailable")
        with self.assertRaises(OSError):
            await guard.guarded_probe(f, f, (), broken_record)
        self.assertTrue(f.stopped)
        self.assertEqual(f.stop_calls, 1)

    async def test_slow_cleanup_is_bounded_and_remains_incident(self):
        f = Fake()
        async def hung_stop():
            await asyncio.Event().wait()
        f.stop = api(hung_stop)
        with (patch.object(guard, "STARTUP_SECONDS", .1),
              patch.object(guard, "EXECUTION_SECONDS", .1),
              patch.object(guard, "CLEANUP_SECONDS", .5),
              patch.object(guard, "STOP_SECONDS", .1),
              patch.object(guard, "EXIT_SECONDS", .5)):
            with self.assertRaises(guard.ResourceIncident):
                await guard.guarded_probe(f, f, (), f.records.append, total_seconds=3)
        self.assertLess(f.records[-1]["elapsed_s"], 3)
        self.assertFalse(f.records[-1]["remote_stop_confirmed"])


if __name__ == "__main__":
    unittest.main()
