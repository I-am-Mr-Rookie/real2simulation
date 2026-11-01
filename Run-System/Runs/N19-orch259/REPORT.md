# N19-orch259
Status: DONE. Read-only cross-vendor security/spend review of wave-1 main b085708c.
Deliverable: evidence/reviews/R-N/REVIEW.md, offline probes.py and PROBE-RESULTS.txt.
Findings: 3 P1, 4 P2. HOLD paid/live-processing DEV exposure; no fixes applied.
P1: live paid transports bypass cap; two independent GPU pools violate one-GPU policy; image recipe omits ffprobe and duration validation fails open.
P2: cross-connection quota races; incomplete number/provenance guard; agent/BFF namespace mismatch; transcription input-limit mismatch/pre-buffering.
Checks: 39 Python tests PASS using repository FastAPI/multipart/httpx pins; 8 Node BFF/editor tests PASS; 7 adversarial probe groups PASS.
Daily-cap atomic reservation, exact USD accounting and Dhaka/judging date tests passed; missing integration is the blocker.
No demonstrated cross-owner disclosure, path traversal or arbitrary code-execution tool.
Paid calls: NONE. GPU allocations: NONE. Deploys/source edits: NONE. No .env values or owner media read.
Setup: reused canonical node_modules junction; cached uv test dependencies only, no manifest changes or npm install.
Initial test setup issues: bare Python lacked pytest; unpinned FastAPI changed router introspection; pins resolved all 39 tests.
Skipped: fixes, web build (no web changes), live/browser E2E, container build, actual deployed image/volume inspection and billing reconciliation.
Risk: passing unit tests do not establish spend-safe runtime or honest model-generated measurement prose; F4/F7 exposure limits are explicit in REVIEW.
