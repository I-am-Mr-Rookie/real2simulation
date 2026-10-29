"""S14e probe: real S10 simulator + fitter trials, SYNTHETIC Spark replies, rendered checks. No Meta calls.
Usage (from root): python -m evidence.S14.S14e_probe  OR  python evidence/S14/S14e_probe.py with PYTHONPATH=."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.agent.test_trial import BRIDGE, GOOD, SCENE_ID, TRIAL_ID, Post, SYNTHETIC_reply, text  # noqa: E402
from Build.agent import trial  # noqa: E402
from Build.agent.tools import render  # noqa: E402

for template in ("free_fall", "projectile"):
    start = BRIDGE.handle({"action": "start", "template": template})
    fit = BRIDGE.handle({"action": "fit", "observations": start["observations"]})
    outputs = trial.trial_outputs(TRIAL_ID, start, fit)
    context = trial.trial_context(SCENE_ID, TRIAL_ID, start, outputs)
    print(f"== {template}: {len(start['observations'])} simulated samples; fitter status {fit['status']}")
    print("tool values:", json.dumps({o["id"]: {k: q["value"] for k, q in o["quantities"].items()} for o in outputs}))
    post = Post(SYNTHETIC_reply([text("Gravity is about ten.")]), SYNTHETIC_reply(GOOD))
    response, rejected = trial.check_trial(context, post)
    print(f"calls {len(post.requests)}; rejected {rejected}")
    print("rendered:", render(response, outputs, SCENE_ID))
    post = Post(*[SYNTHETIC_reply([text("Fine.")])] * 4)
    response, rejected = trial.check_trial(context, post)
    print(f"fallback after {len(post.requests)} calls:", render(response, outputs, SCENE_ID))
