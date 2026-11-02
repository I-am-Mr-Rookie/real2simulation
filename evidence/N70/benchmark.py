"""Reuse N51's exact live loop, cases, handlers and shared-ledger reservations."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from evidence.N51 import benchmark as bench

bench.OUT = Path(__file__).resolve().parent
bench.RUN_ID, bench.CAP_USD = "N70", 3.0
bench.CAP = bench.dc._units(bench.CAP_USD)
bench.CALL_CUTOFF = "2026-11-02T20:04:00+00:00"
bench.MODELS = (bench.core.WONDER_MODEL,)


def unreliable(rows):
    return len(rows) != len(bench.CASES) or any(
        r.get("error") or r["valid_tools"] != r["attempted_tools"]
        or r["number_guard_blocks"] > 1
        or r.get("result", {}).get("stopped") not in ("final", "ask_user", "refusal")
        or r.get("refusal") and r["case"] != "off_topic"
        or r["case"] != "off_topic" and not r["attempted_tools"]
        or r["case"] == "off_topic" and (not r.get("refusal") or r["attempted_tools"])
        for r in rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--effort", choices=("high", "max"), default="high")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        bench.self_check()
        rows = [{"case": k, "valid_tools": 1, "attempted_tools": 1, "number_guard_blocks": 0,
                 "result": {"stopped": "final"}} for k, _ in bench.CASES]
        rows[-1].update(valid_tools=0, attempted_tools=0, refusal=True)
        assert not unreliable(rows)
        assert unreliable(rows[:-1])
        rows[0]["valid_tools"] = 0
        assert unreliable(rows)
        rows[0].update(valid_tools=1, number_guard_blocks=2)
        assert unreliable(rows)
        rows[0].update(number_guard_blocks=0, refusal=True)
        assert unreliable(rows)
        rows[0].update(refusal=False, attempted_tools=0, valid_tools=0)
        assert unreliable(rows)
        rows[0].update(attempted_tools=1, valid_tools=1)
        rows[-1]["refusal"] = False
        assert unreliable(rows)
    else:
        if args.root is None:
            parser.error("--root is required for live calls")
        if args.effort == "max":
            path = bench.OUT / "turns.jsonl"
            rows = [json.loads(line) for line in path.read_text("utf-8").splitlines()] if path.exists() else []
            high = list({r["case"]: r for r in rows if r["effort"] == "high"}.values())
            if len(high) != len(bench.CASES) or not unreliable(high):
                parser.error("max requires a complete, unreliable high sweep first")
        bench.EFFORTS = (args.effort,)
        bench.main(args.root.resolve())
