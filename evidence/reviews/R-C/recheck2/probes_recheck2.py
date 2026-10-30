"""R-C recheck2 probes: temp dirs only, reuses tests/guardrails Settlement fixture; no network/spend.
Run from repo root: python -B evidence/reviews/R-C/recheck2/probes_recheck2.py"""
import json, os, sys, threading
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "tests/guardrails")]
from test_settlement import Settlement, billing_row  # reuse the fix4 synthetic fixture
from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.durable import read_json, write_json
from Build.guardrails.reservations import claim_gpu, reserve_meta, repository_root
from Build.guardrails.settlement import settle_gpu
from Build.guardrails import standalone

OUT = []


def fresh():
    s = Settlement("test_releases_slot_and_bound_not_monthly_spend_or_replay")
    s.setUp()
    return s


def paused(fn):
    try:
        fn()
        return False
    except ReconstructionPaused:
        return True


def record(pid, expect, observed, ok, note=""):
    OUT.append({"probe": pid, "expect": expect, "observed": observed, "met": bool(ok), "note": note})


def race(fn, n=8):
    gate, wins = threading.Barrier(n), []
    def go():
        gate.wait()
        try:
            wins.append(fn())
        except ReconstructionPaused:
            pass
    threads = [threading.Thread(target=go) for _ in range(n)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    return wins


def committed(s):
    st = s.state()["Modal"]["requests"]
    return {r["request_id"].split(":")[-1]: (r.get("settled", False), r.get("billed_usd"), r.get("reserved_usd")) for r in st}


# 1 Forged zero bill by a repo writer: self-consistent local files release slot AND lower monthly liability.
s = fresh()
write_json(s.log, {"app_id": "ap-synthetic", "cost": {"billed": {"status": "billed", "total_usd": "0"}}})
write_json(s.bill, [billing_row("0")])
s.save_proof()
amt = str(s.settle())
third = not paused(lambda: s.reserve("third"))
record("N-SETTLE-FORGED-ZERO", "trust boundary: forged self-consistent evidence accepted",
       {"settled_usd": amt, "third_admitted": third, "first": committed(s).get("first")}, amt == "0E-8" or amt.startswith("0"),
       "No provider-authenticity anchor; same privilege class as N3 journal tamper")
s.doCleanups()

# 2 settled=True tampered into journal without evidence -> pause.
s = fresh()
j = read_json(s.runtime / "reservations.json")
j["requests"][0].update(settled=True, billed_usd="0")
write_json(s.runtime / "reservations.json", j)
p = paused(lambda: s.reserve("third"))
record("N-SETTLED-FLAG-TAMPER", "pause", {"paused": p}, p)
s.doCleanups()

# 3 settle then replay same key/request id; settle twice.
s = fresh(); s.settle()
p1, p2 = paused(lambda: s.reserve("first", ".01")), paused(s.settle)
record("N-SETTLE-REPLAY", "pause both", {"replay_paused": p1, "resettle_paused": p2}, p1 and p2)
s.doCleanups()

# 4 reuse same billing evidence for the second request.
s = fresh(); s.settle()
s.proof["request_id"] = s.second; s.save_proof()
p1 = paused(lambda: settle_gpu(s.root, s.second, s.proof_path))
with s.ledger.open("a") as f:
    f.write(json.dumps({"request_id": s.second, "app_id": "ap-synthetic", "provider": "Modal"}) + "\n")
p2 = paused(lambda: s.reserve("third"))
record("N-SETTLE-EVIDENCE-REUSE", "pause", {"second_settle_paused": p1, "dup_app_then_reserve_paused": p2}, p1 and p2)
s.doCleanups()

# 5 concurrent settlement of the same request -> at most one.
s = fresh()
wins = race(s.settle)
j = read_json(s.runtime / "reservations.json")
record("N-SETTLE-CONCURRENT", "<=1 success, journal settled once", {"wins": len(wins), "settled_rows": sum(bool(r.get("settled")) for r in j["requests"]), "lock_left": (s.runtime / "admission.lock").exists()},
       len(wins) <= 1 and sum(bool(r.get("settled")) for r in j["requests"]) == len(wins) and not (s.runtime / "admission.lock").exists(),
       "threads, non-blocking O_EXCL lock: contention pauses (availability)")
s.doCleanups()

# 6 concurrent claim of one request id.
s = fresh()
wins = race(lambda: claim_gpu(s.root, s.first, "spike-rm02"))
again = paused(lambda: claim_gpu(s.root, s.first, "spike-rm02"))
record("N-CLAIM-CONCURRENT", "<=1 claim; later reclaim pauses", {"wins": len(wins), "reclaim_paused": again}, len(wins) <= 1 and again)
s.doCleanups()

# 7 forged / wrong-stage / settled claims.
s = fresh()
a = paused(lambda: claim_gpu(s.root, "bogus", "spike-rm02"))
b = paused(lambda: claim_gpu(s.root, s.first, "modal-track:clip"))
s.settle()
c = paused(lambda: claim_gpu(s.root, s.first, "spike-rm02"))
record("N-CLAIM-FORGED", "pause all", {"unknown": a, "wrong_stage": b, "settled": c}, a and b and c)
s.doCleanups()

# 8 bearer request id: another launcher of the same stage may consume a pending reservation.
s = fresh()
cross = not paused(lambda: claim_gpu(s.root, s.second, "scene-job:OTHER"))
record("N-CLAIM-BEARER", "documented: same-stage id is a bearer token", {"cross_claim_admitted": cross}, True,
       "No extra slot/$; reserved amount is the parent's bound, not re-validated against the child job")
s.doCleanups()

# 9 standalone mains share the envelope.
s = fresh()
with patch.object(standalone, "ROOT", s.root):
    res = {}
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("S20_MODAL_REQUEST_ID", None); os.environ.pop("S20_MODAL_RESERVATION_USD", None)
        res["no_amount"] = paused(lambda: standalone.admit_standalone("spike-rm02"))
        os.environ["S20_MODAL_REQUEST_ID"] = ""
        res["empty_id"] = paused(lambda: standalone.admit_standalone("spike-rm02"))
        del os.environ["S20_MODAL_REQUEST_ID"]
        os.environ["S20_MODAL_RESERVATION_USD"] = ".1"
        res["slots_full"] = paused(lambda: standalone.admit_standalone("spike-rm02"))
        s.settle()
        res["after_settle_admitted"] = not paused(lambda: standalone.admit_standalone("spike-rm02"))
        res["next_paused"] = paused(lambda: standalone.admit_standalone("spike-rm02"))
        os.environ.pop("S20_MODAL_RESERVATION_USD", None)
record("N-STANDALONE", "pause unless bounded+slot; shares 2-job envelope", res,
       res["no_amount"] and res["empty_id"] and res["slots_full"] and res["after_settle_admitted"] and res["next_paused"])
s.doCleanups()

# 10/11 corrupt journal, missing receipt, stale lock -> every entry point pauses.
for pid, mutate in (("N-CORRUPT-JOURNAL", lambda s: (s.runtime / "reservations.json").write_text("{")),
                    ("N-MISSING-RECEIPT", lambda s: (s.runtime / "receipt.json").unlink()),
                    ("N-STALE-LOCK", lambda s: (s.runtime / "admission.lock").write_text("999999"))):
    s = fresh(); mutate(s)
    calls = {"reserve_gpu": lambda: s.reserve("third", ".01"), "claim": lambda: claim_gpu(s.root, s.first, "spike-rm02"),
             "settle": s.settle,
             "reserve_meta": lambda: reserve_meta(s.root, s.root / "m.jsonl", "understand", "k", ".01", max_calls=6, cap_usd="1")}
    res = {k: paused(f) for k, f in calls.items()}
    record(pid, "pause all", res, all(res.values()))
    s.doCleanups()

# 12 Meta: global cap across fresh caller-selected ledgers; replay.
s = fresh()
adm = []
for i in range(4):
    adm.append(not paused(lambda: reserve_meta(s.root, s.root / f"fresh{i}.jsonl", "understand", f"k{i}", ".3", max_calls=6, cap_usd="1")))
rep = paused(lambda: reserve_meta(s.root, s.root / "fresh9.jsonl", "understand", "k0", ".01", max_calls=6, cap_usd="1"))
record("N-META-GLOBAL", "3 admitted then pause; replay pause", {"admitted": adm, "replay_paused": rep}, adm == [True, True, True, False] and rep)
s.doCleanups()

# 13 Meta pre-POST durability through the real live_post closure (transport mocked to crash).
s = fresh()
import Build.pipeline.understand as U
body = {"model": "m", "input": [{"role": "user", "content": [{"type": "input_text", "text": "x"}]}], "max_output_tokens": 10}
try:
    with patch.object(U, "ROOT", s.root), patch("httpx.post", side_effect=RuntimeError("crash after admission")), \
         patch("dotenv.dotenv_values", return_value={"MODEL_API_BASE_URL": "http://x", "MODEL_API_KEY": "k"}):
        try:
            U.live_post(s.root / "u.jsonl")(body, "kk")
            got = "posted?"
        except RuntimeError:
            got = "crashed"
    rows = [r for r in read_json(s.runtime / "reservations.json")["requests"] if r["provider"] == "Meta Model API"]
    record("N-META-PREPOST", "journal row exists although POST crashed", {"transport": got, "meta_rows": len(rows)}, got == "crashed" and len(rows) == 1)
except Exception as e:  # body shape may not match reserve(); report, do not hide
    record("N-META-PREPOST", "journal row exists although POST crashed", {"error": type(e).__name__ + ": " + str(e)[:120]}, False, "probe harness issue, see fix3 tests")
s.doCleanups()

# 14 linked worktree resolves to main checkout state.
rr = repository_root(ROOT)
record("N-WORKTREE", "main root", {"worktree": str(ROOT), "resolved": str(rr)}, (ROOT / ".git").is_file() and rr != ROOT and (rr / ".git").is_dir())

out = Path(__file__).with_name("probes-output.jsonl")
out.write_text("".join(json.dumps(r) + "\n" for r in OUT), encoding="utf-8")
print(f"{sum(r['met'] for r in OUT)}/{len(OUT)} expectations met")
for r in OUT:
    print(r["probe"], "MET" if r["met"] else "NOT MET", json.dumps(r["observed"]))
