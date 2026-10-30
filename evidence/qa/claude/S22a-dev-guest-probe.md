# S22a dev guest probe (read-only HTTP GET, rehearsal only)

Env: Railway dev web https://web-dev-cd80.up.railway.app (NOT a judging candidate). UTC 2026-10-30T05:18:07Z-05:20:44Z.
Method: PowerShell Invoke-WebRequest, no cookies, no redirects followed. No browser/JS render, deployed SHA not read.

| Path | HTTP | Note |
|---|---|---|
| / | 200 | no login redirect |
| /library | 200 | text: "Demo library No demos are published yet. Guest browsing needs no account." "Viewer not connected". "No uploads are enabled." |
| /lab | 200 | synthetic lab, labelled not calibrated |
| /sign-in | 200 | page served; STATE reports sign-in unavailable (not re-tested) |
| /workspace/does-not-exist | 404 | guest private route not exposed (uniform 404) |

Protocol mapping (GATE_D_PROTOCOL.md): 2.1 PASS(dev, HTTP-only); 2.2 FAIL - no demos published;
2.3/2.4 BLOCKED-BY published library scenes (S09/S18 library path) + viewer connection; 2.5 partial PASS (404 for guest).
Implication: Gate D (b) is currently NOT met even on dev. Not a Gate D decision; S22b must re-run in browser.
