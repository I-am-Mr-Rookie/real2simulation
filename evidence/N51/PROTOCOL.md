# N51 reasoning effort

## Scope
- `core._loop`: every main-model request and every step of the hidden Sol fallback.
- `run_turn`: only a twice-blocked number guard escalates Sol to xhigh; API/no-tool fallback stays high.
- `_to_chat`/`http_post`: Baseten gets `reasoning_effort`; Meta/Merge retain Responses `reasoning.effort`.
- Existing callers, tool schemas, fixture data, environment configuration and exports need no changes.
- Reservation keeps all `max_output_tokens`, including reasoning. Settlement uses total output tokens, not visible tokens alone.

## Live comparison
`benchmark.py` calls the real `core._loop` with the unchanged instructions, tool specs, output limit and step cap.
It uses real lab scene validation, node physics, and fitter handlers. Edit cases start with a generated ball.
Fit input is explicitly SIMULATED. No private uploads, reconstruction GPU, or image generation are used.
Primary-model comparisons intentionally exclude automatic fallback, which would confound model/effort scores.
The fallback escalation itself is covered by offline tests.

Ten fixed requests per model/effort, including contributor, high/xhigh/max. Three concurrent turns maximum,
case-major scheduling. Each turn has an isolated owner scene. One sample per request, not a significance study.
The shared daily ledger remains active. The benchmark separately counts settled AND in-flight reservations
for its $1.50 cap before admitting each API call. Uncertain/failed charges retain the full reservation.
No new calls after 05:45 UTC, leaving the original implementation cutoff at 05:46:48 UTC intact.

`turns.jsonl` contains prompts by case mapping in the script, real final replies/tools, per-call UTC/usage,
reservation ids and ledger cost units (one unit is $0.00000001). Rates are the existing product estimates,
not provider invoices. `summary.json` aggregates the run. The canonical shared ledger is not committed.
Schema-valid call rate counts valid JSON/schema calls, including ask_user, divided by attempted calls.
Handler success is independently available in tool outputs. No-tool refusals have no call denominator.
Number-guard blocks count distinct model response steps, avoiding duplicate checks of one ask_user response.
Refusal flags are a text heuristic plus structured refusal status; review the actual replies before conclusions.

### Harness correction
The first pass used the real lab and fitter handlers but left list_files as the core UNAVAILABLE stub.
Muse Open used that tool for the vague request. All twelve vague-case model/effort combinations were rerun
with the real workspace handlers, including list_files against an empty isolated local file store.
Every paid attempt remains in JSONL and the shared ledger. Scoring uses the latest attempt per case;
the run-wide spend total includes superseded attempts. Curly apostrophes are recognized in refusal summaries.
To regenerate summaries without more calls, import the benchmark module, set `CASES = []`, then call `main(root)`.

## Checks
`python evidence/N51/benchmark.py --self-check`

```powershell
uv run --no-project --python 'C:\Users\HP\AppData\Local\Programs\Python\Python314\python.exe' python -m pytest tests/agent/test_core.py tests/agent/test_handlers.py tests/agent/test_lab_handlers.py tests/agent/test_fallback.py tests/n21 -q
```

No deployment. Cross-vendor spend review belongs to the controller before merge.
