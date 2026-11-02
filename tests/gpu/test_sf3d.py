"""N31 SF3D client: daily_cap reserve at the A10G worst case, settle at the GPU that ran; fake Modal, no paid call."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Build.gpu import sf3d
from Build.guardrails import daily_cap


class Call:
    object_id = 'fc-sf3d-test'
    def __init__(self, result=None, exc=None):
        self.result, self.exc, self.cancelled = result, exc, False

    def get(self, timeout):
        self.timeout = timeout
        if self.exc:
            raise self.exc
        return self.result

    def cancel(self, terminate_containers=False):
        self.cancelled = True


class Fn:
    def __init__(self, call):
        self.call, self.inputs = call, []

    def spawn(self, png):
        self.inputs.append(png)
        return self.call


class TimeoutError(Exception):  # same name as modal's: matched by name
    pass


class Sf3dClient(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cap = Path(self.tmp) / "cap.sqlite3"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_settles_at_the_gpu_that_ran(self):
        fn = Fn(Call({"glb": b"glTF", "vertices": [], "faces": [], "gpu_name": "NVIDIA L4"}))
        r = sf3d.generate_remote(b"png", cap_path=self.cap, fn=fn)
        self.assertEqual((r["gpu"], fn.inputs), ("L4", [b"png"]))
        expect = sf3d.cost(r["wall_s"] + sf3d.IDLE_S, "L4", sf3d.CPU, sf3d.MEM_GIB)["total_usd"]
        self.assertAlmostEqual(r["estimated_usd"], expect, places=5)
        self.assertAlmostEqual(float(daily_cap.today(self.cap)["spent_usd"]), r["estimated_usd"], places=5)
        self.assertGreater(sf3d.ESTIMATE_USD, r["estimated_usd"])  # reservation was the worst case

    def test_timeout_cancels_and_still_settles(self):
        call = Call(exc=TimeoutError())
        with patch.object(sf3d.time, 'monotonic', side_effect=[0, 0, 0, 90, 90]):
            with self.assertRaises(sf3d.GenerationTimeout):
                sf3d.generate_remote(b"png", cap_path=self.cap, fn=Fn(call))
        self.assertTrue(call.cancelled)
        self.assertEqual(call.timeout, 10)
        spent = float(daily_cap.today(self.cap)["spent_usd"])  # unknown GPU: settled at the dearer A10G rate
        self.assertEqual(spent, sf3d.ESTIMATE_USD)  # no result: keep the conservative cold-start upper bound

    def test_remote_function_timeout_also_cancels_and_settles(self):
        call = Call(exc=type("FunctionTimeoutError", (Exception,), {})("execution timeout"))
        with self.assertRaises(sf3d.GenerationTimeout):
            sf3d.generate_remote(b"png", cap_path=self.cap, fn=Fn(call))
        self.assertTrue(call.cancelled)
        self.assertGreater(daily_cap.today(self.cap)["spent_usd"], 0)

    def test_unconfirmed_cancellation_retains_full_reservation(self):
        call = Call(exc=RuntimeError('synthetic disconnect'))
        with patch.object(call, "cancel", side_effect=OSError("synthetic disconnected")):
            with self.assertRaisesRegex(sf3d.GenerationTimeout, "unconfirmed"):
                sf3d.generate_remote(b"png", cap_path=self.cap, fn=Fn(call))
        self.assertEqual(float(daily_cap.today(self.cap)["spent_usd"]), sf3d.ESTIMATE_USD)

    def test_cap_denial_does_not_spawn(self):
        fn = Fn(Call())
        rid = daily_cap.reserve("Modal", daily_cap.today(self.cap)["cap_usd"], "synthetic full cap", path=self.cap)
        with self.assertRaises(daily_cap.CapExceeded):
            sf3d.generate_remote(b"png", cap_path=self.cap, fn=fn)
        self.assertEqual(fn.inputs, [])
        daily_cap.settle(rid, 0, path=self.cap)

    def test_failed_call_settles_once_at_full_bound(self):
        import sqlite3
        fn = Fn(Call(exc=RuntimeError('synthetic remote failure')))
        with self.assertRaisesRegex(RuntimeError, 'synthetic remote failure'):
            sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn)
        with sqlite3.connect(self.cap) as con:
            reserved, actual = con.execute('SELECT reserved,actual FROM spend').fetchone()
        self.assertEqual(actual, reserved)
        self.assertTrue(fn.call.cancelled)

    def test_polling_timeout_can_still_return_a_result(self):
        call = Call()
        with patch.object(call, 'get', side_effect=[TimeoutError(), {'gpu_name': 'NVIDIA L4'}]) as get:
            r = sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call))
        self.assertEqual(r['gpu'], 'L4')
        self.assertEqual(get.call_count, 2)
        self.assertTrue(all(0 < c.kwargs['timeout'] <= 10 for c in get.call_args_list))
        self.assertFalse(call.cancelled)

    def test_replaced_batch_cancels_inflight_call_and_retains_bound(self):
        call = Call()
        with patch.object(call, 'get', side_effect=TimeoutError()), patch.object(call, 'cancel') as cancel:
            with self.assertRaisesRegex(RuntimeError, 'shell rebuilt'):
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call),
                                     abort=iter([False, False, True]).__next__, timeout_s=1)
        cancel.assert_called_once_with(terminate_containers=True)
        self.assertEqual(float(daily_cap.today(self.cap)['spent_usd']), sf3d.ESTIMATE_USD)

    def test_replaced_batch_unconfirmed_cancel_retains_full_estimate(self):
        call = Call()
        with patch.object(call, 'cancel', side_effect=OSError('disconnected')):
            with self.assertRaisesRegex(sf3d.GenerationTimeout, 'unconfirmed'):
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call),
                                     abort=iter([False, True]).__next__, timeout_s=1)
        self.assertEqual(float(daily_cap.today(self.cap)['spent_usd']), sf3d.ESTIMATE_USD)

    def test_replaced_queued_batch_never_spawns_and_settles_zero(self):
        from Build.api import gpu
        fn = Fn(Call())
        jobs = Path(self.tmp) / 'jobs.db'
        stale = False
        start = gpu.start
        def queued(jid, path):
            nonlocal stale
            start(jid, path)
            stale = True
        with patch.object(gpu, 'start', side_effect=queued):
            with self.assertRaisesRegex(RuntimeError, 'shell rebuilt'):
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, owner='owner', gpu_path=jobs,
                                     abort=lambda: stale, timeout_s=1)
        self.assertFalse(fn.inputs)
        self.assertEqual(daily_cap.today(self.cap)['spent_usd'], 0)
        self.assertEqual(gpu.status('owner', None, jobs)['queue_length'], 0)

    def test_spawn_id_persisted_before_wait(self):
        import sqlite3
        jobs = Path(self.tmp) / 'jobs.db'
        call = Call({'gpu_name': 'NVIDIA L4'})
        def get(timeout):
            with sqlite3.connect(jobs) as con:
                self.assertEqual(con.execute('SELECT modal_call_id FROM gpu_jobs').fetchone(), (call.object_id,))
            return call.result
        with patch.object(call, 'get', side_effect=get):
            sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call), owner='owner', gpu_path=jobs)

    def test_invalid_budget_does_not_reserve_or_spawn(self):
        fn = Fn(Call())
        for budget in (0, -1, float('nan'), sf3d.BACKGROUND_BUDGET_S + 1):
            with self.assertRaises(ValueError):
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, timeout_s=budget)
        self.assertFalse(fn.inputs)
        self.assertFalse(self.cap.exists())

    def test_slow_transport_cannot_settle_above_provider_lifetime_reservation(self):
        fn = Fn(Call({'gpu_name': 'NVIDIA L4'}))
        with patch.object(sf3d.time, 'monotonic', side_effect=[0, 0, 0, 10000]):
            r = sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn)
        self.assertEqual(r['wall_s'], 10000)
        self.assertLessEqual(r['estimated_usd'], sf3d.ESTIMATE_USD)
        self.assertEqual(r['estimated_usd'], sf3d.cost(sf3d.STARTUP_S + sf3d.TIMEOUT_S + sf3d.IDLE_S,
                                                     'L4', sf3d.CPU, sf3d.MEM_GIB)['total_usd'])

    def test_lookup_failure_never_spawns_and_settles_zero(self):
        from types import SimpleNamespace
        def lookup(*args):
            raise RuntimeError('synthetic lookup failure')
        with patch.object(sf3d, 'modal', SimpleNamespace(Function=SimpleNamespace(
                from_name=lookup))):
            with self.assertRaisesRegex(RuntimeError, 'synthetic lookup failure'):
                sf3d.generate_remote(b'png', cap_path=self.cap)
        self.assertEqual(daily_cap.today(self.cap)['spent_usd'], 0)


if __name__ == "__main__":
    unittest.main()

