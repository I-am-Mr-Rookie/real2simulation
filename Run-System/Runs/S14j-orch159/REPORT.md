# S14j-orch159 REPORT — DONE

Lane CODEX-1 (Claude per owner); model anthropic/claude-opus-5-5/high; coding quota OpenCodex-managed; not polled.
UTC start 2026-10-30T20:23:43Z; end 2026-10-30T20:29:59Z. Base main 6cd7bc91; branch run/S14j-orch159; code commit 49754d0.
Tokens/cost: unobservable; $0 model/GPU/Meta. Railway DEV build only (existing plan).

## Change
- Build/api/workspace/analysis.py: spec route, on AgentContractError whose issues are ALL `$.scene: invalid authoritative bundle:`
  (validate_setup runs numeric validate() first, and answer issues are raised before it, so this is bundle-only), reruns the
  exact answers_to_spec code with Gate A's spec_only stand-in (contracts.experiment validate()) as validate_setup, via a
  types.FunctionType copy with replaced globals (no global monkeypatch; thread-safe). Returns 200 {ok, spec, validated_setup
  (same shape: the validated spec), label 'scale unverified, not setup-validated', setup_validated:false}. Any other failure 422.
  Authoritative path response unchanged (no new keys).
- tests/api-workspace/test_spec_q16.py (new, 4 tests): RM04 recorded understanding precondition is bundle-only failure;
  valid answers -> 200 + verbatim label, setup_validated false, user's 1.5 m kept, no MET; 4 invalid answer sets -> 422;
  synthetic authoritative scene -> same keys/value as before.
- tests/api-workspace/test_jobs.py: real RM04 READY job via jobs.scene_resolver now expects 200 + label (was 422).

## Ponytail (full) applied
- Reuse: interview.answers_to_spec code itself + contracts validate() (the Gate A spec_only validator); no mapping duplicated,
  interview.py untouched. Precise detection = existing validator's own bundle error prefix. Tests reuse test_analysis fixtures.
- Smallest complete: ~20 lines in one file; deploy via existing stage.py + railway up.
- Skipped: changing verify.py / deployments.json (not owned; lines given in evidence/S14j/README.md); live authenticated DEV spec
  call (needs secret token).

## Checks (fresh)
- tests/api-workspace: 20 OK; tests/pipeline: 53 OK (evidence/S14j/*.txt).
- Railway DEV api deployment a2777e67-be64-4455-9d71-c8c5803c40a0 SUCCESS, /api/version = 49754d0.
- verify.py as committed: exit 1 solely on pinned api revision (54d1575); with pin = 49754d0 in-memory: exit 0, 11/11.

## Risks / limits
- Recorded RM04 base spec carries fixture-labelled ('synthetic', test_experiment_schema.py:authored-fixture) gravity/mass/origin/
  bounds and scale_status 'estimated' from S14g-fix3; S14j adds none and only labels the result. Downstream fit/report must keep
  the Q16 label. Deployed source is branch commit 49754d0, not yet on main; controller must update deployments.json + verify.py pin.
- Communication: silent; one completion line to controller as authorized.
