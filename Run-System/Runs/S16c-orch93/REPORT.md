# S16c-orch93 — DONE (local rebuild API scope)

- Parent: Meta AI Hackathon `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; controller contract S16c-orch93, step S16, lane CODEX-2.
- Requested route: `gpt-6.1-sol/medium`; independent runtime model identity/tokens not observable. Coding quota: **OpenCodex-managed; not polled**.
- UTC issue/start: 2026-10-30T06:31:42+00:00 / first inspection 06:32:07Z. Work stopped/reported: 2026-10-30T06:51:23+00:00. Original deadline 07:01:42Z; cutoff 06:56:42Z. Verified DONE early; no extension or exception.
- Base: main `3ea7f5342c1129fba2d134377fee2ba926269ff0`; branch `run/S16c-orch93`, plain Git worktree `.worktrees/S16c-orch93` as requested. No main/control edits or merge.
- Model/provider/GPU/network calls, dependency installs and deployments: none. API/compute spend: $0; subscription tokens/cost unobservable.

## Delivered

- `Build/sidebar-tools/rebuild.py`: `RebuildSession` stores a defensive current revision and serializes admission, patch commit, execution and receipt publication. Only S16b `apply_patch` success enables rebuilding. Rebuild must match the internal revision, not an arbitrary valid supplied spec. Bundle metadata drift, asset tampering and invalid setups fail closed before execution.
- Calls **existing** `Build.lab.pipeline.run_lab` -> validated setup exporter (`Build/simulator`) -> actual Node RK4 -> synthetic instruments -> `Build.fitter.api`. Synthetic free-fall and projectile exercised end-to-end. No alternate simulator, synthetic numeric guesses or remote execution path added.
- Code-built S14 simulator/fitter numeric outputs preserve emitted units, explicit uncertainties and simulated provenance. Evidence binds job/spec and says synthetic/not calibrated; measured relabelling is rejected. Existing S14 reference validation/render works; untraced model numeric text remains blocked.
- Typed completed payload carries a SHA-256 map keyed by output id. `contracts.output_sha256` hashes normalized S14 receipts; validation rejects altered numbers, missing/wrong digests and empty completion outputs. S14's strict output shape remains unchanged. Legacy `state: queued` acknowledgments remain accepted; completed results say **completed**, not queued.
- Execution errors return sanitized correlated errors with no partial numbers; accepted revision remains retryable. Successful retries reuse the original job/receipt without new compute, even with a fresh call id. Accepted new patches invalidate cache; rejected patches do not. Temporary spec files are confined to trusted caller scratch and removed.

## Fresh checks / evidence

All commands run in this worktree with Python bytecode disabled:

| Command | Result | Evidence relative to worktree |
|---|---|---|
| `python -B -m unittest discover -s tests/sidebar-tools -t tests/sidebar-tools -v` | **56 passed** | `evidence/S16/S16c-orch93-tests.txt` |
| `python -B -m unittest discover -s tests/spec -q` | **93 passed** | `evidence/S16/S16c-orch93-spec-tests.txt` |
| `python -B -m unittest discover -s tests/agent -q` | **52 passed** | `evidence/S16/S16c-orch93-agent-tests.txt` |
| `python -B -m unittest discover -s tests/lab -q` | **17 passed** | `evidence/S16/S16c-orch93-lab-tests.txt` |
| Actual local smoke, then independent hashlib digest verification + S14 render | **PASS** | `evidence/S16/S16c-orch93-smoke/`, `evidence/S16/S16c-orch93-smoke-check.txt` |
| `git diff --check` | **PASS** | command output, no whitespace errors |

218 tests total. The smoke directory contains the actual synthetic scene/asset,
base spec, explicit instrument settings, patch/rebuild calls and results, numeric
reference response and rendered tool-only text. These are **synthetic local
integration evidence, not calibrated physical results**. A scoped smoke-directory
`.gitattributes` preserves PLY bytes against Git CRLF conversion; checkout
normalization was explicitly checked before final handoff.

An initial added behavioral test incorrectly assumed halving configured duration
halves the observed duration; the existing simulator stops at its stop plane first.
Fixed the test to shorten the **actual tool-observed** run duration, then verified
the patched value reaches the simulator and changes output/hash receipts. Initial
failure preserved in `S16c-orch93-tests-initial.txt`; final 56-test suite is green.

## Ponytail full applied / scope

Read the installed 5.3.3 skill. Reused S16a wire validators, S16b application,
S08 scene preflight, S10 lab pipeline and S14 fitter-output/render helpers rather
than creating another simulator, fitter, dispatcher or numeric contract. Reused
the existing synthetic spec/scene fixtures; added one focused owned test module
covering actual execution, safe retry/cache, concurrency, provenance and hashes.
No caller/config/export outside Owns needed changing: no production/sidebar server
caller exists for this local API yet. Documented the new completed payload/API in
the existing contract rather than adding another protocol document.

## Skipped / risks / next integration boundary

- No model/provider calls, search/fallback wiring, UI/server route, authenticated endpoint, durable queue or cross-process job storage. S16d-h and parent S16 remain separate work; no Gate A/RS/physical-success claim.
- Current revision/cache are **process-local**. Restart requires a fresh validated patch. The trusted host must own/authenticate session inputs, provide immutable bundle storage during execution and an existing private scratch directory. The lock is not a cross-process filesystem transaction.
- Existing lab supports only synthetic ballistic free-fall/projectile; physical metadata or other templates return `not_ready`, not fake success. Existing simulation step bound/preflight and Node timeout are reused. Unsupported live jobs are never admitted, so no paid-job authorization is inferred.
- SHA-256 binds content; it does not authenticate an attacker who can replace both receipt and digest. Host custody and S14 numeric-reference validation remain necessary.
- Downstream integration must recognize `state: completed` and pass only the correlated `tool_outputs` to S14, not paste payload hashes/numbers into free text.
- Controller should inspect this branch/report, run `python -B Run-System/worker_timebox.py check Run-System/Runs/S16c-orch93/TIMEBOX.json`, then integrate serially. No canonical controls changed by this worker.

## Communication compliance

Silent work except the mandatory Ponytail skill notice and the required verification
finding notice about evidence-asset line endings. No blocker/question arose.
One owner-authorized concise completion callback to the controller follows commit;
no orchestration, worker launches, schedules or automatic continuation.
