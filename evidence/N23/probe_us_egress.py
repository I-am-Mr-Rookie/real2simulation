"""N23: one GET /v1/models from a Modal CPU container pinned to a US region. Prints counts only, never the key.
Run: uv run --python 3.12 --with modal==1.6.3 --env-file .env modal run evidence/N23/probe_us_egress.py
"""
import json
import os

import modal

app = modal.App("n23-us-egress-probe")
KEYS = ("MODEL_API_KEY", "MODEL_API_BASE_URL")


@app.function(region="us-east", timeout=60, secrets=[modal.Secret.from_dict({k: os.environ.get(k, "") for k in KEYS})])
def probe():
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
    base = (os.environ["MODEL_API_BASE_URL"] or "https://api.meta.ai/v1").rstrip("/")
    out = {"region": os.environ.get("MODAL_REGION"), "cloud": os.environ.get("MODAL_CLOUD_PROVIDER")}
    try:
        with urlopen(Request(f"{base}/models", headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"}), timeout=30) as r:
            body = json.loads(r.read())
            out.update(status=r.status, models=sorted(m.get("id", "?") for m in body.get("data", [])))
    except HTTPError as e:
        out.update(status=e.code)
    with urlopen("https://ipinfo.io/json", timeout=15) as r:  # egress geo only, no IP kept
        out["egress_country"] = json.loads(r.read()).get("country")
    return out


@app.local_entrypoint()
def main():
    print(json.dumps(probe.remote()))
