"""N31 SF3D client: daily_cap reserve at the A10G worst case, settle at the GPU that ran; fake Modal, no paid call."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Build.gpu import sf3d
from Build.guardrails import daily_cap


class Call:
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
        with self.assertRaises(sf3d.GenerationTimeout):
            sf3d.generate_remote(b"png", cap_path=self.cap, fn=Fn(call))
        self.assertTrue(call.cancelled)
        self.assertEqual(call.timeout, 90)
        spent = float(daily_cap.today(self.cap)["spent_usd"])  # unknown GPU: settled at the dearer A10G rate
        self.assertAlmostEqual(spent, sf3d.cost(sf3d.IDLE_S, "A10G", sf3d.CPU, sf3d.MEM_GIB)["total_usd"], places=3)

    def test_remote_function_timeout_also_cancels_and_settles(self):
        call = Call(exc=type("FunctionTimeoutError", (Exception,), {})("execution timeout"))
        with self.assertRaises(sf3d.GenerationTimeout):
            sf3d.generate_remote(b"png", cap_path=self.cap, fn=Fn(call))
        self.assertTrue(call.cancelled)
        self.assertGreater(daily_cap.today(self.cap)["spent_usd"], 0)

    def test_unconfirmed_cancellation_retains_full_reservation(self):
        call = Call(exc=TimeoutError())
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


if __name__ == "__main__":
    unittest.main()

