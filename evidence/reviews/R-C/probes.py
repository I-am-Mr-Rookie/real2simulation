"""R-C adversarial probes: offline, temp files only, no network/cloud/spend. Run from repo root:
python evidence/reviews/R-C/probes.py  -> prints JSON, exits 1 if any EXPECTED-safe probe fails."""
import json, sys, tempfile
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from Build.guardrails.accounting import liability_usd, meta_snapshot
from Build.guardrails.admission import ReconstructionPaused, require_reconstruction
from Build.guardrails.failover import select_provider
from Build.pipeline import gpu_stages

NOW = datetime(2026, 10, 29, 22, 30, tzinfo=timezone.utc)
TMP = Path(tempfile.mkdtemp(prefix="rc-probe-"))
results = []


def snap(meta_hist="10", meta_credit="40", modal_hist="1", modal_credit="29", meta_req=(), modal_req=(), **top):
    s = {"schema": "reconstruction-admission/1", "as_of": NOW.isoformat(), "paused": False,
         "coverage_verified": True, "credit_verified": True, "sources": ["SYNTHETIC probe"],
         "Meta Model API": {"historical_usd": meta_hist, "requests": list(meta_req), "credit_headroom_usd": meta_credit},
         "Modal": {"historical_usd": modal_hist, "requests": list(modal_req), "credit_headroom_usd": modal_credit}}
    s.update(top)
    return s


def write(doc, name, raw=None, encoding="utf-8"):
    p = TMP / name
    p.write_bytes(raw if raw is not None else json.dumps(doc).encode(encoding))
    return p


def admit(path, modal="1", meta="0", now=NOW):
    try:
        require_reconstruction(path, candidate_modal_usd=modal, candidate_meta_usd=meta, now=now)
        return "ALLOWED"
    except ReconstructionPaused:
        return "PAUSED"


def check(pid, got, want, note, expected_safe=True):
    results.append({"id": pid, "got": got, "want": want, "pass": got == want,
                    "expected_safe": expected_safe, "note": note})


row = lambda rid, prov="Meta Model API", **kw: {"request_id": rid, "provider": prov, **kw}

# --- Meta $120 strict cap / $30 reserve
check("M1", admit(write(snap(meta_hist="119", meta_req=[row("a", reserved_usd="0.5")]), "m1.json"), meta="0.5"),
      "PAUSED", "history+pending+candidate == 120 must pause (strict <)")
check("M2", admit(write(snap(meta_hist="119.99999999"), "m2.json"), meta="0"), "ALLOWED", "just below cap, zero new Meta")
check("M3", admit(write(snap(meta_hist="120"), "m3.json"), meta="0"), "PAUSED", "Meta at cap blocks even Modal-only work")
check("M4", admit(write(snap(meta_hist="100", meta_credit="50"), "m4.json"), meta="25"), "PAUSED",
      "$30 reserve not usable as routine headroom even with credit")
check("M5", admit(write(snap(meta_hist="1", meta_req=[row("x", reserved_usd="1", est_usd="200")]), "m5.json")),
      "PAUSED", "conservative estimate above reservation counts")
# --- lifecycle
check("L1", str(liability_usd({"reserved_usd": "1", "billed_usd": "3"})), "3.00000000", "overrun: provisional bill > reserve counts")
check("L2", str(liability_usd({"reserved_usd": "1"})), "1.00000000", "crash: unsettled reserve-only row keeps reservation")
check("L3", admit(write(snap(meta_req=[row("r", reserved_usd="1"), row("r", reserved_usd="1")]), "l3.json")), "PAUSED",
      "retry reusing request_id pauses (cannot shadow)")
check("L4", admit(write(snap(meta_req=[row("s", reserved_usd="5", billed_usd="0", settled=True)]), "l4.json")), "PAUSED",
      "settled without reconciliation_ref pauses")
check("L5", admit(write(snap(meta_req=[row("s", est_usd="5")]), "l5.json")), "PAUSED", "unsettled row without reservation pauses")
check("L6", admit(write(snap(meta_hist="119", meta_req=[row("s", reserved_usd="50", billed_usd="0", settled=True,
                                                            reconciliation_ref="x")]), "l6.json")),
      "ALLOWED", "OBSERVED: settled row trusts billed + any nonempty ref (shape-only; caller must verify finality)",
      expected_safe=False)
# --- fail-closed state
for pid, val in [("F1", "NaN"), ("F2", "Infinity"), ("F3", "1e999999999"), ("F4", True), ("F5", "-1"), ("F6", None)]:
    check(pid, admit(write(snap(modal_hist=val), pid + ".json")), "PAUSED", f"modal historical_usd={val!r}")
check("F7", admit(write(None, "f7.json", raw=b'{"schema":"reconstruction-admission/1","paused":true,"paused":false}')),
      "PAUSED", "duplicate key cannot flip kill switch")
check("F8", admit(TMP / "missing.json"), "PAUSED", "missing state file")
check("F9", admit(TMP), "PAUSED", "directory instead of file")
check("F10", admit(write(snap(), "f10.json", raw=b"\xef\xbb\xbf" + json.dumps(snap()).encode())), "PAUSED",
      "UTF-8 BOM (PowerShell writer) fails closed")
check("F11", admit(write(snap(), "f11.json"), now=NOW + timedelta(minutes=5)), "ALLOWED", "exactly 5 min old allowed")
check("F12", admit(write(snap(), "f12.json"), now=NOW + timedelta(minutes=5, seconds=1)), "PAUSED", "stale >5 min")
check("F13", admit(write(snap(), "f13.json"), now=NOW - timedelta(seconds=1)), "PAUSED", "future snapshot")
check("F14", admit(write(snap(), "f14.json"), now=NOW.replace(tzinfo=None)), "PAUSED", "naive clock")
check("F15", admit(write(snap(), "f15.json"), modal="0"), "PAUSED", "zero Modal candidate cannot bypass")
check("F16", admit(write(snap(), "f16.json"), meta="-1"), "PAUSED", "negative Meta candidate cannot offset")
check("F17", admit(write(snap(meta_req=[row("m", prov="Modal", reserved_usd="1")]), "f17.json")), "PAUSED",
      "Modal row smuggled into Meta envelope")
check("F18", admit(write(snap(sources="x"), "f18.json")), "PAUSED", "sources must be list")
check("F19", admit(write(snap(sources=["only one opaque label"]), "f19.json")), "ALLOWED",
      "OBSERVED: any nonempty source label satisfies inventory (shape-only by design)", expected_safe=False)
# --- Modal cap/floor
check("D1", admit(write(snap(modal_hist="24", modal_credit="100"), "d1.json"), modal="1"), "ALLOWED", "projected 25 = floor edge")
check("D2", admit(write(snap(modal_hist="24", modal_credit="100"), "d2.json"), modal="1.00000001"), "PAUSED", "below $5 floor")
# --- rounding of credit headroom (ROUND_CEILING applied to headroom in admission)
check("R1", admit(write(snap(meta_credit="0.000000001"), "r1.json"), meta="0.00000001"), "ALLOWED",
      "OBSERVED: Meta credit 1e-9 rounded UP to 1e-8 admits 1e-8 candidate (admission rounds headroom up; failover refuses this)",
      expected_safe=False)
# --- AWS switch
def sel(env, **kw):
    try:
        return select_provider(write(snap(**kw.pop("snapkw", {})), "sel.json"), candidate_modal_usd="1", env=env, now=NOW, **kw)["provider"]
    except ReconstructionPaused:
        return "PAUSED"

check("A1", sel({}), "Modal", "default OFF")
check("A2", sel({"R2S_ENABLE_AWS": "true"}), "Modal", "only exact '1' enables")
check("A3", sel({"R2S_ENABLE_AWS": "1"}), "PAUSED", "flag without receipts pauses, no Modal fallback")
check("A4", sel({"R2S_ENABLE_AWS": "1"}, snapkw={"modal_hist": "29"}), "PAUSED", "AWS cannot bypass Modal floor/cap")
q = {"schema": "aws-quota-receipt/1", "as_of": NOW.isoformat(), "owner_approved": True, "region": "us-east-2",
     "market": "spot", "quota_code": "L-3819A6DF", "spot_quota_vcpu": 8}
b = {"schema": "aws-budget-receipt/1", "as_of": NOW.isoformat(), "owner_approved": True, "region": "us-east-2",
     "coverage_verified": True, "credit_verified": True, "remaining_gross_usd": "50", "credit_headroom_usd": "50",
     "budget": {"name": "Real2Sim EC2 50 USD", "amount_usd": 50, "currency": "USD", "period": "MONTHLY", "gross": True,
                "services": ["Amazon Elastic Compute Cloud - Compute", "EC2 - Other"],
                "alerts": ["actual:50", "actual:80", "actual:100", "forecast:100"]}}
def aws(qd=q, bd=b, **kw):
    kw = {"candidate_aws_usd": "2", "max_session_seconds": 600, **kw}
    return sel({"R2S_ENABLE_AWS": "1"}, quota_receipt_path=write(qd, "q.json"), budget_receipt_path=write(bd, "b.json"), **kw)

check("A5", aws(), "AWS", "valid receipts -> plan only (launched=False)")
check("A6", aws(qd={**q, "market": "on-demand"}), "PAUSED", "on-demand refused")
check("A7", aws(qd={**q, "region": "us-east-1"}), "PAUSED", "wrong region refused")
check("A8", aws(bd={**b, "remaining_gross_usd": "50.000000001"}), "PAUSED", "headroom >50 / >8dp refused")
check("A9", aws(candidate_aws_usd="51"), "PAUSED", "bound above headroom refused")
check("A10", aws(max_session_seconds=True), "PAUSED", "bool session refused")
check("A11", aws(max_session_seconds=3601), "PAUSED", "session >1h refused")
check("A12", aws(qd={**q, "owner_approved": "true"}), "PAUSED", "string approval refused")
check("A13", aws(bd={**b, "as_of": (NOW - timedelta(minutes=6)).isoformat()}), "PAUSED", "stale budget receipt")
check("A14", aws(candidate_aws_usd="0"), "PAUSED", "zero AWS bound refused")
check("A15", [aws(), aws()], ["AWS", "AWS"], "OBSERVED: same receipts admit twice; AWS liabilities live only in the "
      "receipt's net headroom (no AWS bucket in shared snapshot, no reservation memory)", expected_safe=False)

# --- shared-snapshot shape gaps (orch60)
check("X1", admit(write(snap(AWS={"historical_usd": "999", "requests": [row("z", prov="AWS", reserved_usd="999")]}),
                        "x1.json")), "ALLOWED",
      "OBSERVED: unknown provider bucket (e.g. AWS liabilities) silently ignored, not rejected", expected_safe=False)
same = write(snap(modal_hist="20"), "c1.json")
check("C1", [admit(same, modal="4"), admit(same, modal="4")], ["ALLOWED", "ALLOWED"],
      "OBSERVED: preflight has no reservation; two $4 admissions on one snapshot both pass (projected 28 > floor) "
      "-> caller must serialize check+reserve", expected_safe=False)

# --- live paid-boundary cap: gpu_stages.reserve is per-ledger-file, not global
spent = 0.0
for i in range(3):
    gpu_stages.reserve(TMP / f"run{i}" / "gpu-ledger.jsonl", "reconstruct", f"k{i}", 1.0)
    spent += 1.0
check("G1", spent, 1.0, "FINDING: three fresh ledger paths each accepted a $1 reservation (caller-chosen path resets cap)",
      expected_safe=False)
try:
    gpu_stages.reserve(TMP / "run0" / "gpu-ledger.jsonl", "segment", "k9", 0.01); g2 = "ALLOWED"
except gpu_stages.StageError:
    g2 = "PAUSED"
check("G2", g2, "PAUSED", "same ledger enforces its own $1 run cap")
(TMP / "bad.jsonl").write_text("{not json\n", encoding="utf-8")
try:
    gpu_stages.reserve(TMP / "bad.jsonl", "segment", "k", 0.01); g3 = "ALLOWED"
except Exception as exc:
    g3 = type(exc).__name__
check("G3", g3, "JSONDecodeError", "corrupt run ledger raises (fails closed, but not mapped to SPEND_PAUSED)")

bad = [r for r in results if r["expected_safe"] and not r["pass"]]
print(json.dumps({"tmp": str(TMP), "total": len(results), "expected_safe_failures": len(bad),
                  "observed_findings": [r for r in results if not r["expected_safe"]], "failures": bad}, indent=1, default=str))
sys.exit(1 if bad else 0)

