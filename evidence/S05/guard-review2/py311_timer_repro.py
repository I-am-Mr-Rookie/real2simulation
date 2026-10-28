"""Isolated local repro: rm02_deadline real-timer tests vs Windows clock granularity.
Imports only rm02_deadline + the test Fake (no Modal). Run parent-capped."""
import asyncio, sys, time
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import rm02_deadline as guard
from test_rm02_deadline import Fake

async def scenario(scale):
    f = Fake(); f.hang = True
    with patch.object(guard, "STARTUP_SECONDS", .01 * scale), \
         patch.object(guard, "EXECUTION_SECONDS", .01 * scale), \
         patch.object(guard, "CLEANUP_SECONDS", .04 * scale), \
         patch.object(guard, "EXIT_SECONDS", .01 * scale):
        try:
            await guard.guarded_probe(f, f, (), f.records.append, total_seconds=.15 * scale)
        except BaseException as exc:
            r = f.records[-1]
            return (type(exc).__name__, r["cleanup_errors"], r["stop_acknowledged"],
                    r["remote_stop_confirmed"], round(r["elapsed_s"], 3))

print(sys.version.split()[0], time.get_clock_info("monotonic").implementation)
for scale in (1, 10):
    print("scale", scale, asyncio.run(scenario(scale)))
