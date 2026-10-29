"""S06g AWS spot adapter: DISABLED by default; pure gate check, no AWS SDK, no API calls.

Mirrors sam3d_option.gate: returns reasons AWS must NOT activate; empty list = every owner gate passes.
Gates (owner, DECISIONS_LOG 2026-10-29): env flag -> region us-east-2 -> spot only -> G/VT spot quota
-> $50 EC2 budget with alerts. Inputs are explicit owner-recorded facts; nothing is inferred or fetched.
Offline receipt:  python Build/gpu/aws_adapter.py [out.json]
"""
import json
import os
import sys
from pathlib import Path

ENV_FLAG = "R2S_ENABLE_AWS"  # must be exactly "1"; anything else keeps it off
REGION = "us-east-2"
INSTANCE = "g6e.xlarge"
INSTANCE_VCPU = 4
SPOT_QUOTA_CODE = "L-3819A6DF"  # EC2 "All G and VT Spot Instance Requests" (vCPU)
BUDGET_MAX_USD = 50
BUDGET_SERVICES = {"Amazon Elastic Compute Cloud - Compute", "EC2 - Other"}
REQUIRED_ALERTS = {"actual:50", "actual:80", "actual:100", "forecast:100"}


def gate(gates, env=None):
    """gates: {region, market, spot_quota_vcpu, budget: {amount_usd, services, alerts}}; returns refusal reasons."""
    env = os.environ if env is None else env
    g = gates or {}
    reasons = []
    if env.get(ENV_FLAG) != "1":
        reasons.append(f"disabled: {ENV_FLAG} != 1 (default off)")
    if g.get("region") != REGION:
        reasons.append(f"region: {g.get('region')!r} != {REGION}")
    if g.get("market") != "spot":
        reasons.append(f"market: {g.get('market')!r} refused; spot only (on-demand quota 0)")
    q = g.get("spot_quota_vcpu")
    if not isinstance(q, (int, float)) or isinstance(q, bool) or q < INSTANCE_VCPU:
        reasons.append(f"quota: G/VT spot {q!r} vCPU < {INSTANCE_VCPU} needed for {INSTANCE}")
    b = g.get("budget") or {}
    amt = b.get("amount_usd")
    if not isinstance(amt, (int, float)) or isinstance(amt, bool) or not 0 < amt <= BUDGET_MAX_USD:
        reasons.append(f"budget: amount {amt!r} not in (0, {BUDGET_MAX_USD}] USD")
    if not BUDGET_SERVICES <= set(b.get("services") or ()):
        reasons.append("budget: not filtered to EC2-Compute + EC2-Other")
    missing = REQUIRED_ALERTS - set(b.get("alerts") or ())
    if missing:
        reasons.append(f"budget: missing alerts {sorted(missing)}")
    return reasons


def activate(gates, env=None):
    """Plan only. No launcher is packaged: even a passing gate returns a spec, never creates resources."""
    reasons = gate(gates, env)
    return {"active": not reasons, "reasons": reasons, "launched": False,
            "plan": {"region": REGION, "instance": INSTANCE, "market": "spot"} if not reasons else None}


# Owner-recorded state (DECISIONS_LOG 2026-10-29); env flag still required to activate.
OWNER_GATES = {"region": REGION, "market": "spot", "spot_quota_vcpu": 8,
               "budget": {"name": "Real2Sim EC2 50 USD", "amount_usd": 50,
                          "services": sorted(BUDGET_SERVICES), "alerts": sorted(REQUIRED_ALERTS)}}

if __name__ == "__main__":
    result = {"contract": "S06g-aws-adapter/v1", "no_aws_api_calls": True,
              "default": activate(OWNER_GATES, env={}),
              "on_demand": activate({**OWNER_GATES, "market": "on-demand"}, env={ENV_FLAG: "1"}),
              "no_gates": activate({}, env={ENV_FLAG: "1"})}
    text = json.dumps(result, indent=1)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[1]).write_text(text + "\n")
    print(text)
    sys.exit(0 if not (result["default"]["active"] or result["on_demand"]["active"]) else 1)

