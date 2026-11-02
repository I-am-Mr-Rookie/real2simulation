"""N31 SF3D client: daily_cap reserve at the A10G worst case, settle at the GPU that ran; fake Modal, no paid call."""
import shutil
import sqlite3
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

    def rows(self):
        with sqlite3.connect(self.cap) as con:
            rows = con.execute('SELECT label,reserved,actual FROM spend ORDER BY rowid').fetchall()
        self.assertTrue(all(actual is not None and 0 <= actual <= reserved for _, reserved, actual in rows))
        return rows

    def test_four_serial_calls_reserve_before_spawn_and_book_one_idle_tail(self):
        clock, walls = [0], iter([97, 7, 7, 6])
        fn = Fn(Call({'gpu_name': 'NVIDIA A10G'}))

        def result(timeout):
            with sqlite3.connect(self.cap) as con:
                pending = con.execute('SELECT reserved FROM spend WHERE actual IS NULL').fetchall()
            self.assertEqual(len(pending), 2, 'compute and idle tail both reserved before spending')
            clock[0] += next(walls)
            return fn.call.result

        with patch.object(sf3d.time, 'monotonic', side_effect=lambda: clock[0]), patch.object(fn.call, 'get', side_effect=result):
            with sf3d.SerialBatch(self.cap) as batch:
                for _ in range(4):
                    sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=batch)
        rows = self.rows()
        self.assertEqual(len(rows), 5)
        self.assertEqual(sum('idle tail' in label for label, _, _ in rows), 1)
        expected = sf3d.cost(117 + sf3d.IDLE_S, 'A10G', sf3d.CPU, sf3d.MEM_GIB)['total_usd']
        self.assertAlmostEqual(float(daily_cap.today(self.cap)['spent_usd']), expected, places=7)

    def test_failure_mid_batch_still_books_one_tail_when_remaining_calls_continue(self):
        with sf3d.SerialBatch(self.cap) as batch:
            sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(Call({'gpu_name': 'NVIDIA L4'})), batch=batch)
            with self.assertRaisesRegex(RuntimeError, 'synthetic remote failure'):
                sf3d.generate_remote(b'png', cap_path=self.cap,
                                     fn=Fn(Call(exc=RuntimeError('synthetic remote failure'))), batch=batch)
            sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(Call({'gpu_name': 'NVIDIA L4'})), batch=batch)
        rows = self.rows()
        self.assertEqual(sum('idle tail' in label for label, _, _ in rows), 1)
        self.assertEqual(rows[2][1], rows[2][2], 'failed compute keeps its full reservation')

    def test_interrupted_batch_exit_still_settles_the_tail(self):
        with self.assertRaisesRegex(RuntimeError, 'local fitting failed'):
            with sf3d.SerialBatch(self.cap) as batch:
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(Call({'gpu_name': 'NVIDIA L4'})), batch=batch)
                raise RuntimeError('local fitting failed')
        self.assertEqual(sum('idle tail' in label for label, _, _ in self.rows()), 1)

    def test_aborted_before_spawn_has_no_idle_charge(self):
        fn = Fn(Call())
        with sf3d.SerialBatch(self.cap) as batch:
            with self.assertRaisesRegex(RuntimeError, 'shell rebuilt'):
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=batch, abort=lambda: True)
        self.assertFalse(fn.inputs)
        self.assertEqual(self.rows()[0][2], 0)
        self.assertEqual(daily_cap.today(self.cap)['spent_usd'], 0)

    def test_two_concurrent_batches_each_keep_their_own_tail(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier = Barrier(2)

        def run(_):
            call = Call({'gpu_name': 'NVIDIA L4'})
            with patch.object(call, 'get', side_effect=lambda timeout: (barrier.wait(timeout=10), call.result)[1]):
                with sf3d.SerialBatch(self.cap) as batch:
                    sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call), batch=batch)

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(run, range(2)))
        rows = self.rows()
        self.assertEqual(sum('idle tail' in label for label, _, _ in rows), 2)

    def test_tail_cap_denial_prevents_spawn_and_releases_compute(self):
        from decimal import Decimal
        headroom = Decimal(str(sf3d.RUN_ESTIMATE_USD)) + Decimal('0.01')
        daily_cap.reserve('Modal', daily_cap.today(self.cap)['cap_usd'] - headroom, path=self.cap)
        fn = Fn(Call())
        with sf3d.SerialBatch(self.cap) as batch:
            with self.assertRaises(daily_cap.CapExceeded):
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=batch)
        self.assertFalse(fn.inputs)
        with sqlite3.connect(self.cap) as con:
            self.assertEqual(con.execute('SELECT actual FROM spend ORDER BY rowid DESC LIMIT 1').fetchone(), (0,))

    def test_short_gaps_are_charged_and_long_gaps_reserve_a_fresh_tail(self):
        clock = [0]
        fn = Fn(Call({'gpu_name': 'NVIDIA A10G'}))
        with patch.object(sf3d.time, 'monotonic', side_effect=lambda: clock[0]):
            with sf3d.SerialBatch(self.cap) as batch:
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=batch)
                clock[0] += 10
                r = sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=batch)
                self.assertEqual(r['estimated_usd'], sf3d.cost(10, 'A10G', sf3d.CPU, sf3d.MEM_GIB)['total_usd'])
                clock[0] += sf3d.GAP_BUDGET_S + 1
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=batch)
        self.assertEqual(sum('idle tail' in label for label, _, _ in self.rows()), 2)

    def test_batch_abort_unconfirmed_cancel_keeps_compute_plus_tail_bound(self):
        call = Call(exc=RuntimeError('disconnect'))
        with patch.object(call, 'cancel', side_effect=OSError('disconnected')):
            with sf3d.SerialBatch(self.cap) as batch:
                with self.assertRaisesRegex(sf3d.GenerationTimeout, 'unconfirmed'):
                    sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call), batch=batch)
        self.assertEqual(self.rows()[0][1], self.rows()[0][2])
        self.assertAlmostEqual(float(daily_cap.today(self.cap)['spent_usd']), sf3d.ESTIMATE_USD, places=7)

    def test_batch_gap_plus_slow_transport_cannot_exceed_compute_reservation(self):
        clock = [0]
        call = Call({'gpu_name': 'NVIDIA A10G'})
        with patch.object(sf3d.time, 'monotonic', side_effect=lambda: clock[0]):
            with sf3d.SerialBatch(self.cap) as batch:
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call), batch=batch)
                clock[0] += sf3d.GAP_BUDGET_S

                def slow(timeout):
                    clock[0] += 10000
                    return call.result

                with patch.object(call, 'get', side_effect=slow):
                    r = sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call), batch=batch)
                self.assertEqual(r['estimated_usd'], sf3d.RUN_ESTIMATE_USD)
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(call), batch=batch)
        self.assertEqual(sum('idle tail' in label for label, _, _ in self.rows()), 2,
                         'slow transport may let the old container sleep before the next call')

    def test_gap_is_always_worst_gpu_even_if_next_call_moves_to_l4(self):
        clock = [0]
        with patch.object(sf3d.time, 'monotonic', side_effect=lambda: clock[0]):
            with sf3d.SerialBatch(self.cap) as batch:
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(Call({'gpu_name': 'NVIDIA A10G'})), batch=batch)
                clock[0] += 10
                r = sf3d.generate_remote(b'png', cap_path=self.cap, fn=Fn(Call({'gpu_name': 'NVIDIA L4'})), batch=batch)
                self.assertEqual(r['estimated_usd'], sf3d.cost(10, 'A10G', sf3d.CPU, sf3d.MEM_GIB)['total_usd'])
        self.rows()

    def test_closed_or_different_ledger_batch_cannot_spawn(self):
        fn = Fn(Call())
        with sf3d.SerialBatch(self.cap) as batch:
            pass
        with self.assertRaisesRegex(ValueError, 'open and serial'):
            sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=batch)
        with sf3d.SerialBatch(self.cap.parent / 'other.db') as other:
            with self.assertRaisesRegex(ValueError, 'same spend ledger'):
                sf3d.generate_remote(b'png', cap_path=self.cap, fn=fn, batch=other)
        self.assertFalse(fn.inputs)
        self.rows()

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

