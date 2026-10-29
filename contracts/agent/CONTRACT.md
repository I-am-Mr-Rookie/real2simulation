# S14a agent contracts v1.0.0 (fixture-only)

Hard rule: **agent text carries no numbers; every number is a reference to a
code-built fitter/simulator output labelled `measured` or `simulated`.**

| Contract | Version | Where |
|---|---|---|
| Structured response (model output) | `agent-response/1.0.0` | [response.schema.json](response.schema.json) + `validate_response` |
| Question (inside response, max 3) | same | `$defs/question`: `chips`, `free_text`, `chips_and_free_text`; max 6 chips |
| Tool output (code-built, never model-authored) | `agent-tool-output/1.0.0` | `validate_tool_output` |
| Scene context (model input) | `agent-scene-context/1.0.0` | `Build/agent/tools.scene_context` |

## Response

`segments` is a list of `{"type":"text","text":...}` and
`{"type":"number","ref":{"tool_output_id":...,"quantity":...}}`. Number segments
have no inline value: the renderer (`Build/agent/tools.render`) prints value,
standard uncertainty, unit and label from the referenced tool output. Question
prompts, chip labels and candidate rationales use the same segment lists.

`validate_response(response, tool_outputs, scene_id)` returns the response or
raises `AgentContractError` (`issues` tuple). It applies, in order: strict JSON
(for strings; duplicate keys/NaN rejected via `contracts/experiment` `parse_json`),
JSON Schema 2020-12 (ASCII digits in text rejected; unknown fields rejected),
then semantics: Unicode numerals/fractions and common number words rejected,
every ref resolves to an existing tool-output quantity, `scene_id` matches,
`free_text` has no chips and chip kinds have at least one.

## Tool output

`{"schema_version","id","tool":"fitter"|"simulator","status":"ok","quantities":{name: Quantity}}`.
Quantities reuse the S11 `contracts/fit` quantity checks (finite value, allowed
unit, non-negative uncertainty, non-empty evidence); `source.label` must be
`measured` or `simulated`. `fit_tool_output` builds one from
`Build.fitter.api.handle`; failed fits or null gravity cannot back numbers.

## Scene context

Built only from a bundle that passes `contracts/scene` validation. Exposes
ids, labels, `synthetic`, scale and gravity *statuses*, surface ids and collider
shapes; **no numeric fields**, so scene geometry cannot be quoted as a result.

## S14b Muse Wonder scene understanding

`Build/agent/muse.understand(scene_context, post)` sends only the number-free scene
context to `muse-wonder-1.0` (Meta Model API `/v1/responses`, structured output with
this schema, minimal reasoning, `max_output_tokens` 1500) and returns a validated
`agent-response`. No tool outputs are passed, so any number segment is untraced and
rejected. Added semantics: `candidates[].template` must be an S08 experiment template
(read from `contracts/experiment/experiment.schema.json`) and candidate ids are unique;
a non-`completed` Responses status is rejected. Live replies are recorded by
`python -m Build.agent.record_muse <name>` (key by name from `.env`; <=20 calls/<=$1 guard;
ledger `evidence/S14/S14b-ledger.jsonl`) as sanitized fixtures in
`tests/agent/fixtures/muse/`; `tests/agent/test_muse.py` replays them offline.
Fixture validity is synthetic-scene contract evidence only: not Gate A, video input (S13e),
real-scene, calibration or physical evidence.

## S14c interview (offline, code-owned questions)

`Build/agent/interview.py`: `template_of(response, candidate_id)` takes the template of the Muse
candidate the user picked; `questions(scene_id, template)` returns a validated, number-free
agent-response with that template's one to three questions (free_fall/projectile two, ramp/pendulum
three); `answers_to_spec(base_spec, scene, scene_root, answers)` maps
`{question id: {"chip": id} | {"text": str}}` onto a copy of a same-template base spec and returns it only
after S08c `validate_setup`; otherwise `AgentContractError` lists every issue.

- Question id = spec parameter name. Chips are exact meanings only (`at-rest`, `frictionless` -> 0); no
  default physical numbers. Free text: ASCII decimal plus optional unit (contract unit; angles require
  `deg`/`rad` since a bare number is ambiguous). Non-finite, words, Unicode digits, unknown chips/units/
  questions and missing answers are rejected.
- S14a open item decided: user-entered numbers enter the **spec** only, labelled `assumed`, evidence
  `user-input:<param>:<chip:id|free-text>`, uncertainty null (unquantified). They are never echoed in
  agent text; anything displayed comes from simulator/fitter tool outputs.
- Model-authored questions (S14b) are shown as context only; their chips are not mapped to spec inputs.
- Unasked inputs (gravity, body, origin, simulation, other parameters) keep the base spec's provenance.
- Tests: `tests/agent/test_interview.py` with S08 SYNTHETIC fixtures, hand-written SYNTHETIC answers and the
  RECORDED S14b fixture `live-room-v1-d`. Not Gate A, real-scene, calibration or physical evidence.

## Limits (S14a)

- Number-word list is a shortcut (`one` allowed as a pronoun; Roman-numeral
  letters and rarer phrasings not caught). Gate A (S14f/S14g) extends it.
- User-entered numbers are not echoable yet (no `user_input` label); S14c decides.
- Fail-closed false positives: superscripts such as `m/s²` or words like "half"
  in text are rejected; units belong to rendered number segments.
- Contract validity is not Gate A, real-scene, calibration or physical evidence.
  Tests use visibly synthetic fixtures only.

```powershell
python -m unittest discover -s tests/agent -p 'test_*.py' -v
```
