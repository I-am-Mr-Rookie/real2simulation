"""R-C recheck probes: temp dirs only, no network/spend, never canonical runtime. Run from repo root:
python evidence/reviews/R-C/recheck/probes_recheck.py  -> JSON lines {id, expect, observed, ok}."""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from Build.guardrails.accounting import headroom_usd  # noqa: E402
from Build.guardrails.admission import ReconstructionPaused, require_reconstruction  # noqa: E402
from Build.guardrails.durable import read_json, write_json  # noqa: E402
from Build.guardrails.reservations import repository_root, reserve_gpu  # noqa: E402

out = []


def rec(pid, expect, observed, ok):
    out.append({"id": pid, "expect": expect, "observed": observed, "ok": bool(ok)})


def fixture():
    root = Path(tempfile.mkdtemp(prefix="rc-recheck-"))
    rt = root / "evidence/S20/runtime"
    rt.mkdir(parents=True)
    receipt = {"schema": "reconstruction-admission/1", "as_of": datetime.now(timezone.utc).isoformat(),
               "paused": False, "coverage_verified": True, "credit_verified": True, "sources": ["SYNTHETIC"],
               "Meta Model API": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "150"},
               "Modal": {"historical_usd": "0", "requests": [], "credit_headroom_usd": "30"}}
    write_json(rt / "receipt.json", receipt)
    write_json(rt / "reservations.json", {"schema": "gpu-reservations/1", "requests": [], "ledgers": []})
    return root, rt, receipt


def try_reserve(root, name, amount=".4"):
    try:
        reserve_gpu(root, root / "Run-System/Runs" / name / "gpu-ledger.jsonl", "reconstruct", name, amount,
                    max_jobs=2, cap_usd="1")
        return "admitted"
    except ReconstructionPaused:
        return "paused"


# N-CONC: 8 real processes race $0.40 each against $1/2-job cap.
root, rt, _ = fixture()
code = ("import sys;sys.path.insert(0,sys.argv[1]);from pathlib import Path\n"
        "from Build.guardrails.reservations import reserve_gpu\n"
        "from Build.guardrails.admission import ReconstructionPaused\n"
        "try:\n reserve_gpu(Path(sys.argv[2]),Path(sys.argv[2])/'Run-System/Runs'/sys.argv[3]/'gpu-ledger.jsonl',"
        "'reconstruct',sys.argv[3],'.4',max_jobs=2,cap_usd='1');print('admitted')\n"
        "except ReconstructionPaused:\n print('paused')")
procs = [subprocess.Popen([sys.executable, "-c", code, str(REPO), str(root), f"p{i}"], stdout=subprocess.PIPE, text=True)
         for i in range(8)]
res = [p.communicate(timeout=120)[0].strip() for p in procs]
j = read_json(rt / "reservations.json")
rec("N-CONC", "<=2 admitted, journal rows == admitted, lock released",
    {"results": res, "journal_rows": len(j["requests"]), "lock_left": (rt / "admission.lock").exists()},
    res.count("admitted") <= 2 and len(j["requests"]) == res.count("admitted") and not (rt / "admission.lock").exists())

# N-STALE: crashed owner leaves lock -> pause, never auto-broken.
root, rt, _ = fixture()
(rt / "admission.lock").write_text("999999")
r = try_reserve(root, "a")
rec("N-STALE", "paused; lock untouched", {"result": r, "lock": (rt / "admission.lock").exists()},
    r == "paused" and (rt / "admission.lock").exists())

# N-CORRUPT: corrupt journal / missing receipt / extra journal key -> pause, nothing written.
for label, mutate in (("journal", lambda rt: (rt / "reservations.json").write_text("{bad")),
                      ("receipt-missing", lambda rt: (rt / "receipt.json").unlink()),
                      ("journal-extra-key", lambda rt: write_json(rt / "reservations.json",
                       {"schema": "gpu-reservations/1", "requests": [], "ledgers": [], "x": 1}))):
    root, rt, _ = fixture()
    mutate(rt)
    r = try_reserve(root, "a")
    led = root / "Run-System/Runs/a/gpu-ledger.jsonl"
    rec("N-CORRUPT-" + label, "paused, no ledger", {"result": r, "ledger": led.exists()}, r == "paused" and not led.exists())

# N-MISSING-LEDGER: an inventoried ledger deleted later must pause (no refill by deletion).
root, rt, _ = fixture()
try_reserve(root, "a")
(root / "Run-System/Runs/a/gpu-ledger.jsonl").unlink()
r = try_reserve(root, "b")
rec("N-MISSING-LEDGER", "paused", r, r == "paused")

# N-REFILL: server-owned journal replaced by an EMPTY valid one (tamper/"cleanup"). Contract count/$ cap uses
# journal rows + caller ledger only; old ledgers still project into the Modal $30 cap.
root, rt, _ = fixture()
first = [try_reserve(root, n) for n in ("a", "b", "c")]
write_json(rt / "reservations.json", {"schema": "gpu-reservations/1", "requests": [], "ledgers": []})
after = [try_reserve(root, n) for n in ("d", "e")]
rec("N-REFILL", "FINDING if after_reset admits (contract cap refilled by journal reset)",
    {"before_reset": first, "after_reset": after}, True)

# N-REPLAY: same key / same ledger replay rejected.
root, rt, _ = fixture()
a1, a2 = try_reserve(root, "a"), try_reserve(root, "a")
rec("N-REPLAY", "second identical reservation paused", [a1, a2], a1 == "admitted" and a2 == "paused")

# N-WORKTREE / N-CLONE: linked worktree shares main state; an independent clone has its own.
tmp = Path(tempfile.mkdtemp(prefix="rc-wt-"))


def g(*a, cwd=tmp):
    subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True)


g("init", "-q", "main")
main = tmp / "main"
g("-c", "user.email=r@c", "-c", "user.name=rc", "commit", "-q", "--allow-empty", "-m", "x", cwd=main)
g("worktree", "add", "-q", str(tmp / "wt"), "-b", "w", cwd=main)
rr = repository_root(tmp / "wt")
rec("N-WORKTREE", "worktree -> main root", str(rr), rr == main.resolve())
g("clone", "-q", str(main), str(tmp / "clone"))
rc = repository_root(tmp / "clone")
rec("N-CLONE", "clone resolves to itself (separate state; admits only with copied receipt+journal)",
    str(rc), rc == (tmp / "clone").resolve())

# N-UNKNOWN-KEY: unknown top-level snapshot key rejected (M2).
root, rt, receipt = fixture()
receipt["AWS_typo"] = {}
write_json(rt / "s.json", receipt)
try:
    require_reconstruction(rt / "s.json", candidate_modal_usd=".1")
    r = "admitted"
except ReconstructionPaused:
    r = "paused"
rec("N-UNKNOWN-KEY", "paused", r, r == "paused")

# N-FLOOR: credit headroom floors (L2).
rec("N-FLOOR", "headroom 1e-9 -> 0", str(headroom_usd("0.000000001")), headroom_usd("0.000000001") == 0)

# N-META-UNDERSTAND: Build/pipeline/understand.py::reserve caps per caller-selected LEDGER file (CLI arg);
# fresh files reset; no lock/global journal. Probe calls only the pure check; no transport.
try:
    from Build.pipeline import understand
    body = {"input": [{"content": [{"type": "input_text", "text": "x" * 100}, {"type": "input_image"}]}]}
    d = Path(tempfile.mkdtemp(prefix="rc-meta-"))
    admits = []
    for i in range(4):
        led = d / f"l{i}.jsonl"
        led.write_text(json.dumps({"est_usd": 0.999}) + "\n")  # each ledger already near its $1 cap
        try:
            admits.append(round(understand.reserve(body, d / f"fresh{i}.jsonl"), 6))
        except Exception as exc:  # noqa: BLE001
            admits.append(type(exc).__name__)
    rec("N-META-UNDERSTAND", "FINDING if every fresh ledger admits (per-file Meta cap, no global reserve)",
        {"fresh_ledger_admits_worst_usd": admits, "global_journal_consulted": False}, True)
except ImportError as exc:
    rec("N-META-UNDERSTAND", "import", repr(exc), False)

for row in out:
    print(json.dumps(row))

