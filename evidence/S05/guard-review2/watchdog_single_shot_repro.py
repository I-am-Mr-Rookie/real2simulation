"""Isolated local repro: watchdog does ONE info/container check; a transient
'stopping...' state (APP_STATE_STOPPING, modal/cli/app.py:49) right after stop becomes
a permanent incident although reserve remains. Local CLI double only; never Modal."""
import json, pathlib, sys, tempfile
sys.path.insert(0, sys.argv[1])
import rm02_watchdog as watchdog

APP_ID = "ap-" + "B" * 22
CHILD = "import json,os,pathlib,sys;pathlib.Path(os.environ['RM02_WATCHDOG_RECEIPT']).write_text(json.dumps({'app_id':sys.argv[1]}))"
CLI = '''
import json, pathlib, sys
count = pathlib.Path(__file__).with_name("info_calls")
if sys.argv[2] == "info":
    n = int(count.read_text()) if count.exists() else 0
    count.write_text(str(n + 1))
    print(json.dumps({"app_id": sys.argv[3], "lifecycle": {"state": "stopping..." if n == 0 else "stopped"}}))
elif sys.argv[1] == "container":
    print("[]")
'''
root = pathlib.Path(tempfile.mkdtemp())
(root / "child.py").write_text(CHILD); (root / "cli.py").write_text(CLI)
try:
    watchdog.supervise([sys.executable, str(root / "child.py"), APP_ID], root / "attempt",
                       total_seconds=6, reserve_seconds=5, cli=[sys.executable, str(root / "cli.py")])
    print("CONFIRMED")
except watchdog.ResourceIncident:
    s = json.loads((root / "attempt/watchdog.json").read_text())
    print("INCIDENT", {k: s[k] for k in ("stop_acknowledged", "independent_stop_confirmed", "elapsed_s", "errors")},
          "info_calls", (root / "info_calls").read_text(), "reserve_s", 5)
