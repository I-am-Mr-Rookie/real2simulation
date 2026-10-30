"""S21d: runtime and per-scene cost, ONLY from sha256-pinned accepted evidence (S21a pattern).

python Build/benchmark/costs.py [out.json]  -> writes evidence/S21/S21d-costs.json (deterministic).
python Build/benchmark/costs.py --md         -> prints the generated BENCHMARK.md cost table.
Classes are never summed together: billed (Modal billing report read), estimated (rate x time),
reservation (pre-job hold), measured (timing/tokens), simulated (S20d cap regression, NOT spend),
unavailable (evidence value is null).
"""
import hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manifest as mf

OUT = mf.ROOT / "evidence/S21/S21d-costs.json"
CLASSES = ("billed", "estimated", "reservation", "measured", "simulated", "unavailable")
# Accepted cost evidence not in the frozen S21a manifest; pinned here (as S21c did) instead of re-freezing.
EXTRA = {
    "scene_cost_rm02": {"path": "evidence/S06/S06h/RM02-scene-log.reconciled.json",
                        "sha256": "3b9c8f52f29b452d58963b1951b3681128cd3495784c35836c035a7a1f9a9a4c"},
    "scene_cost_rm04": {"path": "evidence/S06/S06h/RM04-scene-log.reconciled.json",
                        "sha256": "7cf30556ef899055c55a4ecbf0ad13413121d6bce6c5bf92b364cd830bc95fb9"},
    "meta_s16e": {"path": "evidence/S16/S16e-orch108-live.json",
                  "sha256": "65afd740c5556d4443d1f80b73df6a30ff5fbcbe53888a8b7af3a010f457bed5"},
    "sim_s20d": {"path": "evidence/S20/S20d-regression.json",
                 "sha256": "c800b8fc672a3020f80539659b3fd0f5f987be58c5d2a3e09c7d2a267dc619b2"},
}


def ref(ev, ptr):
    return {"evidence": ev, "pointer": ptr}


def rows(docs):
    r = lambda ev, ptr: mf.resolve(docs, ref(ev, ptr))
    out = []

    def add(id, cls, scene, unit, ev, ptr, *, reason=None, reason_sources=(), note=None):
        v = r(ev, ptr)
        if cls == "unavailable":
            if v is not None or not reason:  # fail closed: never reinterpret a non-null "unavailable" value
                raise ValueError(f"{id}: {ev}{ptr} expected null (unavailable), got {v!r}")
        elif cls == "simulated" and isinstance(v, str):
            v = float(v)  # S20d stores decimal strings; still a pointer value, never billed
        elif not mf._num(v):
            raise ValueError(f"{id}: {cls} value must be a number from evidence, got {v!r}")
        out.append({"id": id, "class": cls, "scene": scene, "value": v, "unit": unit,
                    "sources": [ref(ev, ptr)], "reason": reason, "reason_sources": list(reason_sources),
                    "note": note})

    def billed(ev):
        if r(ev, "/cost/billed/status") != "billed":
            raise ValueError(f"{ev}: /cost/billed/status is not 'billed'")

    # Modal scene jobs (MapAnything, A10G): billed vs estimate; cold start vs GPU time kept separate
    for c in ("RM02", "RM04"):
        ev, k = f"scene_cost_{c.lower()}", c.lower()
        billed(ev)
        add(f"{k}_scene_billed_usd", "billed", c, "USD", ev, "/cost/billed/total_usd",
            note="Modal billing report (read-only); whole app incl. egress")
        add(f"{k}_scene_estimated_usd", "estimated", c, "USD", ev, "/cost/estimated/total_usd",
            note="rate x measured container time; NOT billed")
        add(f"{k}_gpu_seconds_billed", "billed", c, "GPU-s", ev, "/gpu_seconds/billed")
        add(f"{k}_cold_start_s", "measured", c, "s", ev, "/timing_s/cold_start_s", note="before function body")
        add(f"{k}_model_load_s", "measured", c, "s", ev, "/timing_s/model_load_s")
        add(f"{k}_inference_s", "measured", c, "s", ev, "/timing_s/inference_s", note="GPU forward pass only")
        add(f"{k}_client_round_trip_s", "measured", c, "s", ev, "/timing_s/client_round_trip_s")

    # ST03 held-out tracking job (S12 Gate RS input)
    billed("cost_st03_job")
    add("st03_tracking_billed_usd", "billed", "ST03", "USD", "cost_st03_job", "/cost/billed/total_usd")
    add("st03_tracking_gpu_seconds_billed", "billed", "ST03", "GPU-s", "cost_st03_job", "/gpu_seconds/billed")

    # Modal month-to-date and S06 jobs from the S06h checkpoint (already-pinned manifest evidence)
    if r("checkpoint_s06h", "/jobs/3/task") != "S06e":
        raise ValueError("checkpoint_s06h /jobs/3 is not S06e")
    add("modal_month_to_date_billed_usd", "billed", "all", "USD", "checkpoint_s06h",
        "/modal_month_to_date_billed_usd", note=f"all Modal jobs; read {r('checkpoint_s06h', '/billing_read_utc')}")
    add("s06_jobs_billed_usd", "billed", "S06", "USD", "checkpoint_s06h", "/s06_jobs_billed_usd")
    add("s06e_reservation_usd", "reservation", "RM02", "USD", "checkpoint_s06h", "/jobs/3/reservation_usd",
        note="pre-job hold, NOT spend")

    # Meta Model API (S16e live call): tokens measured, dollars unknown (Q17)
    add("meta_s16e_total_tokens", "measured", "S16e", "tokens", "meta_s16e", "/usage_measured/total_tokens")
    add("meta_s16e_latency_s", "measured", "S16e", "s", "meta_s16e", "/latency_seconds_measured")
    add("meta_s16e_cost_usd", "unavailable", "S16e", "USD", "meta_s16e", "/cost_usd",
        reason=f"{r('meta_s16e', '/cost_basis')} (Q17)", reason_sources=[ref("meta_s16e", "/cost_basis")])

    # S20d simulated cap regression: must be zero provider calls; values SIMULATED, never billed
    if r("sim_s20d", "/provider_calls") != 0 or r("sim_s20d", "/mode") != "SIMULATED_ONLY":
        raise ValueError("sim_s20d is not a zero-call simulated run")
    for k in ("meta_routine_stop_usd", "modal_cap_usd"):
        add(f"s20d_{k}", "simulated", "SIM", "USD", "sim_s20d", f"/{k}", note="cap exercised in simulation; NOT spend")
    return out


def build(m=None, extra=None):
    m = m or json.loads(mf.DEFAULT.read_text(encoding="utf-8"))
    pins = {**m["evidence"], **(EXTRA if extra is None else extra)}
    chk = mf.check(m)
    if not chk["ok"]:
        raise ValueError(f"frozen manifest check failed: {chk['errors']}")
    docs, errs = mf._load({"evidence": pins})
    if errs:
        raise ValueError(f"evidence pin failed: {errs}")
    rs = rows(docs)
    return {"schema": "s21d-costs/1", "generated_by": "Build/benchmark/costs.py",
            "rule": "classes are never summed together; billed only from read-only Modal billing report reads",
            "manifest_sha256": hashlib.sha256(mf.DEFAULT.read_bytes()).hexdigest(),
            "evidence_sha256": {k: e["sha256"] for k, e in pins.items()},
            "gates": chk["gates"],
            "summary": {k: sum(x["class"] == k for x in rs) for k in CLASSES},
            "rows": rs}


def markdown(doc):
    """Generated table pasted verbatim into BENCHMARK.md; test_costs checks it is current."""
    f = lambda v: "UNAVAILABLE" if v is None else f"{v:.6g}"
    lines = ["| id | class | scene | value | unit | note / reason |", "|---|---|---|---|---|---|"]
    for x in doc["rows"]:
        lines.append(f"| {x['id']} | {x['class']} | {x['scene']} | {f(x['value'])} | {x['unit']} | "
                     f"{x['reason'] or x['note'] or ''} |")
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1:] == ["--md"]:
        sys.exit(print(markdown(build())))
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    try:
        doc = build()
    except ValueError as e:
        sys.exit(str(e))
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(doc["summary"]), out)
