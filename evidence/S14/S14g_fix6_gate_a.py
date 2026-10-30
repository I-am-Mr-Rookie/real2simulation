"""S14g-fix6 Gate A OFFLINE re-run (R-A F1-R3: bare label-chain unit binding removed).
Usage (repo root): python -B evidence/S14/S14g_fix6_gate_a.py

Reuses S14g_fix5_gate_a.run() unchanged (same guards, saved fix3 responses, Q16=A labelling); the fix6 validator and
oracle are what it now imports. Writes S14g-fix6-offline.json. No model call, $0. Never plain MET via Q16.
"""
from __future__ import annotations

import json

import S14g_fix5_gate_a as F5

if __name__ == "__main__":
    result = F5.run()
    result["summary"]["scope"] = result["summary"]["scope"].replace("fix5 structural unit rule",
                                                                    "fix6 unit rule (no bare label binding)")
    (F5.HERE / "S14g-fix6-offline.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n",
                                                    encoding="utf-8")
    print(json.dumps(result["summary"], indent=1, ensure_ascii=False))
