# CODEX-2 coverage map and missing cases

Read-only source baseline d939aa0; normalized hashes and exact Python test names/
lines in observations.json. No coverage percentage computed. All reproductions
use synthetic bytes/metadata and patched transports, not deployment/auth evidence.

| Finished module | Existing coverage | Missing regression / current observation |
|---|---|---|
| Auth policy `Build/web/src/auth/access.mjs:3-22` | access.test.mjs has4 tests: configuration/ID rejection, identity-before-data boundary, exact ownership/frozen minimal grant, callback failure denial | Add strict nonboolean configured values; exact1/128/129 ID boundaries; whitespace/nonstring identity; throwing metadata getter. Owned auth-review.mjs freshly verifies11 such cases, no live session. |
| Configuration `Build/web/src/auth/config.mjs:3-17` | config.test.mjs has4 tests: missing/partial, unsafe/mismatched keys, secret exclusion, unpadded public key | Add nonstring env values, live/test symmetric cases and malformed/noncanonical Base64 encodings; clarify syntax-only parser, never credential validity. Not all proposed cases executed. |
| Server wrapper `Build/web/src/auth/server-access.js:9-19` | Pure policy tests only; no metadata repository currently exists | Future integration must assert session-token-only Clerk call, unavailable-repository denies before provider work, redirect/notFound behavior and independent asset/job authorization. Intentional missing feature, NOT an exposed private route. |
| Dependency cache `Build/api/health/dependencies.py:69-99` | test_dependencies.py:46,55,65 cover dev gating, sanitization, pending de-duplication; adapter resource cleanup tests:87-139 | No committed5s expiry/failure/recovery regression. Deterministic probe verifies0/4.999/5/9.999/10s states ok/ok/unavailable/unavailable/ok,3 submissions; strict probe success requires literalTrue. Add concurrent callers and exception/cancelled Future handling if production ever supplies those Futures. |
| Health endpoints | test_health.py:25-99 covers missing config, sanitized revisions, absent job API and real loopback; test_dependencies.py:35 checks worker heartbeat503 | Existing tests could not import in this interpreter: missing typing_extensions; health-tests.txt preserves actual error. No health HTTP tests passed in this review. Stdlib cache probes are NOT a substitute for FastAPI/adapter integration. Reuse a complete project environment before changing health code. |
| Dev verifier `infra/railway/dev/verify.py:19-60` | test_verify.py:82-159 has7 methods covering service/status/revision/HTTP/dependency mismatches, nonobject JSON; fresh7/7 PASS | Add malformed JSON bytes, invalidUTF8 bytes, URL/timeout exceptions, missing web product/title/content and private-route200. Owned review.py verifies these without real transport; every case fails closed and retains10-check output. No new verifier acceptance defect found. |
| Staging `infra/railway/dev/stage.py:9-35` | No dedicated committed stager regression test found | See confirmed P2 below. Add fresh/existing-target tests, allowlist service isolation, committed-not-dirty bytes, manifest hashes and no .env/archive inclusion. These are missing automated cases, not claims that private inputs were uploaded. |

## P2 — existing staging destination can be overwritten under Python optimization

`stage.py:12` uses `assert not target.exists()` as its only existing-target guard.
Python optimization removes assertions. stage-review.py executes the ACTUAL module
compiled normally/optimized, with Git calls replaced by synthetic committed bytes
and isolated temporary files only. Normal mode rejects before changing a sentinel;
optimized mode overwrites it and writes a context manifest. Exact observations in
stage-observations.json. No real user file, .env value or repository source touched.

This is an operational data-preservation defect for `python -O`/PYTHONOPTIMIZE,
not a remotely exploitable auth bypass or proof of historical data loss. Current
documented command does not use optimization. Recommended separate owned repair:
explicit runtime validation for service/fresh target/allowlist invariants, plus
normal and optimized-mode regression. Never weaken the fresh-directory boundary.

## Prior finding reconciled

F-CODEX-2-1's incorrect service/status acceptance defect was fixed by S04g1.
Current source enforces both; existing7-test suite and fresh negative probes pass.
Do not repeat the superseded finding as current. Worker503/no consumer, private
repository unavailable, Google/OTP untested and packaging reproducibility limits
remain distinct intentional/integration boundaries; no gate/deploy success inferred.
