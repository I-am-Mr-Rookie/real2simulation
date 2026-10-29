# S14d-orch20 REPORT — DONE

- Lane/model: anthropic/claude-opus-5-5 high; coding quota OpenCodex-managed; not polled. Tokens/cost: unknown (unobservable). Meta/Muse calls: **0** (offline replay only; billing hold respected). GPU/spend: none.
- UTC issue 2026-10-29T12:06:16+00:00 (work began 12:07:11) — end 2026-10-29T12:22:13+00:00. Branch run/S14d-orch20, code commit 6e6e8a5 on main 4f193cf. Worktree .worktrees/S14d-orch20.
- Communication: silent; one authorized completion line to controller. Canonical controls untouched.

## Result
Acceptance "Max 3 retries; unresolved ambiguity asks user rather than fabricating": met on recorded + SYNTHETIC fixtures.
- `Build/agent/muse.py` (+43 lines): `MAX_RETRIES = 3`; `build_request(..., feedback=())` appends the last rejected reply's validator issues (bounded 8 x 200 chars) to instructions; `understand_with_retry(context, post) -> (response, rejected_issues)` makes at most 1 + 3 calls; `ask_user(scene_id)` is a code-owned, validated, number-free response with `candidates: []` and one chip question whose chip ids are the S08 templates (each feeds `interview.questions`).
- Ambiguity rule: no valid reply after 3 retries, OR a valid reply with no candidate -> `ask_user`. No default template, candidate or number is ever produced by code or kept from a rejected reply.
- Transport errors from `post` propagate without retry (avoid retry churn; not validator failures).
- `contracts/agent/CONTRACT.md`: S14d section (incl. worst case 4 calls/scene for budget reservation). `tests/agent/test_retry.py`: 7 tests.

## Ponytail (full) applied
- Reuse: S14b `build_request`/`output_text`/`validate_response` unchanged path (`understand` untouched; `record_muse` caller unaffected — keyword default); existing `AgentContractError.issues` as retry feedback; S08 `TEMPLATES` as fallback chips; S14c `interview.questions` as the next step; RECORDED fixtures `live-room-v1-a` (incomplete) and `-d` (valid).
- Smallest complete: one loop + one fallback builder + one optional arg; no new schema, state machine, retry config, backoff or dependency. Dropped a `max_retries` parameter (nobody asked; constant is the contract).
- Skipped (named): live Muse retry run (billing hold); ledger/budget integration of retries (record_muse ledger untouched; reservation note in CONTRACT); UI wiring of ask_user (S15 lane); S14b model-authored question handling (unchanged from S14c).

## Fresh checks
- `python -m unittest discover -s tests/agent -p 'test_*.py' -v` -> 30 OK (evidence/S14/S14d-unittest.txt).
- `python -m unittest discover -s tests/spec -p 'test_*.py'` -> 93 OK (regression).
- Mutation spot checks 7/7 killed (evidence/S14/S14d-mutation.txt via evidence/S14/S14d_mutation.py): MAX_RETRIES=4, off-by-one loop, feedback dropped, candidate-free reply returned, transport errors retried, fallback fabricates candidate, fallback unvalidated. First run let "transport errors retried" survive because the mutation left `post` outside try; mutation fixed, then killed.
- Probe (evidence/S14/S14d-probe.txt): 4 rejected attempts (incomplete / bad JSON / number word "two" / wrong scene_id) -> exactly 4 requests, 4th carries the 3rd's issue, final = ask_user.

## Limits / risks
- Fixture-only: replay of recorded synthetic-scene replies + marked SYNTHETIC mutations. Not Gate A, real-scene, calibration or physical evidence; whether live Wonder actually fixes issues from feedback is unverified.
- Retries cost up to 4x tokens per scene; callers reserving Meta budget must reserve for 4 calls.

