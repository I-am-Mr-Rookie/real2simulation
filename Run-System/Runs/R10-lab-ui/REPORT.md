# R10-lab-ui — DONE (owned UI contract)

## Identity and timebox

- Assigned lane/model: CODEX-2, Sol medium. Runtime model identity is not independently observable here.
- Parent project: `91e441f8-e40c-4ec4-bea2-de7fa1582d97`; inline Oct29 owner swarm exception.
- Only working checkout: `C:/Users/HP/.codex/worktrees/swarm10-ui/2026-10-26 - Meta Global AI Developer Hackathon`.
- Branch: `run/R10-lab-ui`; started detached at `3fa80eb4985779f8b913ce1d9cdbd932f1b65468`, created only the assigned branch. No merge/rebase/main edits.
- Code head: **`1600d816c07eb10d36ef8941ea6d96bcccd4fa1f`**. Subsequent receipt-only commit includes this report, TIMEBOX, final test output and whitespace-only cleanup of the captured failing log.
- Issued `2026-10-28T19:55:20.136Z`; first recorded runtime clock `19:55:55.1569286Z`; implementation cutoff `20:20:20.136Z`; deadline `20:25:20.136Z`.
- Correct Dhaka deadline: **Oct29 02:25:20.136 +06:00**. Handout's `06:55` Dhaka value is inconsistent; authoritative UTC gives exactly 1,800 seconds.
- Task implementation/checks stopped **2026-10-28T20:02:28Z**. Fully verified owned criteria DONE early; no padding or early incomplete exception. Report/receipt finalization follows separately.

## Smallest complete change — Ponytail full applied

- Read canonical AGENTS/STATE/QUEUE, swarm report and timebox policy; applied full skill from the specified marketplace path. No duplicate worker, service or browser launched.
- Reused existing SVG `plotPoints` directly on `session.observations`, rather than its nine-row table sample. The existing finite filter now sees every bounded trajectory observation.
- Moved the existing table sampler into the existing helper module for executable tests; preserved <=9 rows and first/final observations, excluding malformed/nonfinite rows without numeric coercion. Existing component export remains compatible.
- Corrected visible chart/table and accessible chart labels: **downward vertical displacement from start**, positive down; explicitly not ramp distance or pendulum arc. This is an ordinate-versus-time plot, not a spatial reconstruction.
- Ramp/pendulum ready status no longer invites an unsupported ballistic fit. Disabled fit/Mystery controls remain unchanged.
- Reproduced malformed fit: an outer `status: error` with inner valid fit was accepted. One extra envelope-status check now rejects that and missing outer status; valid actual service responses continue to parse.
- Preserved simulated source/uncertainty metadata, Mystery pre-fit secrecy, reset/unmount abort and request-version stale guards. No CSS changes were needed; no new dependencies or features.

## Fresh verification

| Command/check | Actual outcome | Evidence |
|---|---|---|
| `node --test tests/lab/ui-contract.test.mjs` before fix | 3 pass / 3 fail: full-data wiring, labels/status, malformed envelope reproduced | `evidence/S10/ui-hardening/before.txt` |
| Same command after final code/test changes | **8/8 pass** | `evidence/S10/ui-hardening/after.txt`, post-commit `final-ui.txt` |
| 2,000-point oscillation regression | All 2,000 SVG points retained; nine table rows alias a near-flat line while the real plotted maximum exceeds 0.999. First/final table rows retained. | Executable helper test |
| Empty/malformed/nonfinite and constant-domain inputs; table sizes 1/2/8/9/16/17/2000 | Pass; no coercion, <=9 rows, endpoints retained | Executable helper tests |
| Next SWC `transformSync` on actual `LabClient.jsx` | Parse/transform pass using existing canonical Next dependency read-only; no emitted build/server | `evidence/S10/ui-hardening/jsx-transform.txt` |
| Node here-string: `handleLab(start/fit)` -> `plotPoints`/`sampleRows`/`parseFitReveal` | Actual bridge/fitter passes all four templates: fall/projectile/ramp 201 points each, pendulum 1001; nine table rows each. Ballistic Mystery responses redact pre-fit data and parse after fit; stale session rejected. Ramp/pendulum return actual unsupported-fit code and no reveal. | `evidence/S10/ui-hardening/actual-bridge-helpers.txt` |
| `node --test tests/lab/*.test.mjs` | **14 pass / 1 fail** at that point (before the later guard-source test): 7 session-service and 7 UI tests pass. Contact integration cannot import absent worktree `@dimforge/rapier3d-compat`. Not a green whole-suite claim. | `evidence/S10/ui-hardening/lab-node.txt` |
| `git diff --check HEAD~1` | Pass after whitespace-only failing-log cleanup | Final local command |

No failed test was hidden/reclassified. Broad-suite failure is a missing isolated-checkout dependency outside the owned UI acceptance, not simulator correctness evidence. No install/config changes were made.

## Scope, skips and remaining risk

- Changed product paths only `Build/web/src/lab/LabClient.jsx`, `Build/web/src/lab/fit-contract.mjs`, `tests/lab/ui-contract.test.mjs`; additional writes only owned evidence/run directory.
- **Parent must perform real IAB 375px/rendered interaction verification after integration.** No browser/server control here; SWC/source/helper tests do not prove mobile rendering or live interaction.
- Preserved existing bounded-service contract (<=2,000 observations). No new generic response schema, axis ticks, spatial/3D features, fitter/simulator/Python/service/config/control changes.
- No physical Gate M/S12/real-scene, GPU, deployment, publication, account, term, credential or policy action. No global model/provider changes or quota polling.
- No Claude review performed; any required gate review belongs to parent.
- Costs/tokens: **unknown**. Coding quota: **OpenCodex-managed; not polled**.
- Communication: no optional greeting/plan/status. Mandatory higher-priority Ponytail announcement and changed-verification finding only; final one-line pointer. No cross-chat messages.

Owned criteria complete. Skipped browser/mobile E2E and full dependency-backed contact suite; those remain parent/integration checks, not physical evidence.
