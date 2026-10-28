# S08a — DONE

## Objective and execution

Define versioned experiment inputs, units, source labels and scene constraints.
Authorized by Koushik's `Complete run S08a`. CODEX-1, planned GPT-6.1 Sol / medium;
actual runtime model/effort unavailable, no routing/settings changes.

- Claim UTC: 2026-10-27T17:30:19Z; verification complete by 2026-10-27T17:34:00Z.
  Preflight occurred before claim; report/control recording followed verification.
- Start main: f0d64943d6487657c037e27cd04b51f55af827f4.
- Claim commit: 02d693c; task commit: 4a663b079d5549e1fc1837ce7b2e03903c289450.
- Branch run/S08a rebased (already current), verified and fast-forwarded to main.

## Files

- contracts/experiment/experiment.schema.json: closed JSON Schema2020-12 v1.0.0,
  four parameter variants, labelled physical quantities, explicit units/unknowns,
  world-frame scene constraints and fixed-step replay inputs. No output/result fields.
- contracts/experiment/README.md: unit dimensions, source semantics, frame/sign and
  placement conventions, mandatory future execution validation and version policy.
- contracts/experiment/requirements.txt: existing jsonschema4.23.0 pinned; no install.
- tests/spec/test_experiment_schema.py: original synthetic structural fixtures/tests.
- Main-only serialized receipts: QUEUE/RUNS, STATE, DECISIONS_LOG, API_BUDGET,
  RUN_LOG, PLAN and REPORT. No Build/templates implementation needed in this leaf.

## Actual verification

| Command/check | Result |
|---|---|
| python -m unittest discover -s tests/spec -p 'test_*.py' -v | 13/13 PASS initially, after rebase, and on fresh main (1.105s) |
| python -m unittest discover -s contracts/scene -p 'test_*.py' -v | 11/11 PASS on fresh main (14.054s) |
| git diff --cached --check; git diff main...HEAD --check; git diff --check | PASS |
| git rebase main; git merge --ff-only run/S08a | Already current; fast-forward succeeded |
| Plan preservation compared with start main f0d6494 | Git blobs identical; working file LF-equivalent; no plan edit |

Coverage: schema self-validation/internal-only refs; required/closed shape; four
discriminated variants; explicit typed units; provenance/uncertainty; null unknown
drafts; position shape; scene constraints; uint32 seed; fixed baseline environment.
Source labels are structurally validated metadata, not authentication of measurements.

STATE's prior plan hash was stale. Fresh Git-blob SHA256:
ef101e5efa7c945463fe9f16b0c5f1c66154991fd1464af259507a3eab82706e.
Windows raw-file SHA256 (CRLF):
4e0c276c7156d15e465eed4b53708821b70e7ee8d6733555a07a2eec65ca60f7.

## Limits, budget, next

S08a only is complete, not parent S08. JSON parsing hardening, finite/range checks,
dimensional validation, actual scene reference/geometry/stability verification and
executable templates/oracles remain later runs. Unknown drafts are representable,
not executable. No physics or real footage tested; all gates R/M/P/RS/A/C/D/S NOT RUN.
The authored test numbers are synthetic inputs, not measured/simulated results.

No inference, GPU, deployment, installs, network/model calls, secrets, private data,
archive imports, publication or remote changes. Meta/service/GPU spend $0 this run;
historical balance unknown. Coding tokens/task dollars/Claude quota unavailable.
Codex shared before/after used67%5h /49%weekly, remaining33% /51%; reset1793132283;
rounded shared snapshots cannot attribute this task's usage. No reset/purchase.

Unrelated four untracked research/concept paths and CODEX-2 S02a claim preserved.
During receipt recording, main advanced through concurrent S02a commits7309313
and b853382 (clips and scope receipt). They are preserved, not S08a-owned work;
S02a was still IN PROGRESS in QUEUE at this checkpoint. No other lane was accepted.
Next: S08b, Codex CODEX-1, GPT-6.1 Sol / medium. No owner question needed.
