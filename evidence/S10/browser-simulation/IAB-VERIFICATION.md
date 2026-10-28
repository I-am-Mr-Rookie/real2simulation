# Parent verification — actual ChatGPT in-app browser

2026-10-28 20:37–20:41 UTC. Candidate code `694df9a`, local development
server at loopback3101. No deployment or real-scene claim.

Actual UI actions: choose each NORMAL template, Run trial, Compute in browser.
All four rendered the reused RK4 engine output, not pre-authored screenshots.

| Template | Actual SVG points | innerWidth | document clientWidth | scrollWidth |
|---|---:|---:|---:|---:|
| Free fall | 201 | 375 | 360 | 360 |
| Projectile | 201 | 375 | 360 | 360 |
| Ramp | 201 | 375 | 360 | 360 |
| Pendulum | 1001 | 375 | 360 | 360 |

Read-only DOM records: `iab-normal-375.json`; per-template375px PNGs beside
this document. Parent visually inspected pendulum screenshot: full trace,
clear simulated/synthetic/RK4-only and no-contact-response/free-drag labels;
no horizontal overflow. Trace is deliberately static, not an animation.

Then switch from normal pendulum to free-fall Mystery, Run trial, Fit & reveal.
Before and after reveal there is NO in-browser simulation section/control.
Before fit no gravity-unit reveal was present; after fit the existing simulated
fitter reveal succeeded. Both views have375px innerWidth and360px client/scroll.
Read-only DOM evidence: `iab-mystery-375.json`, screenshots before/after.
This DOM observation is not proof of network privacy by itself: actual bridge
and service tests separately verify no Mystery DTO/setup/seed/gravity publication.

Parent fresh combined checks after transport integration: Node84/84 PASS and
Python lab17/17 PASS; worker timebox receipts both TIMING PASS. Logs in
`Run-System/Runs/R11-browser-engine/parent-node-tests.txt` and
`parent-python-tests.txt`. Tests include actual four Python exports/server
trace equivalence and normal horizon bounds. No new dependency or physics copy.

Not checked here: full production bundle, native targeted gate review (separate
workers), real devices/performance, calibrated physics, contact response,
free dragging, physical M/S12. All owner holds unchanged.
