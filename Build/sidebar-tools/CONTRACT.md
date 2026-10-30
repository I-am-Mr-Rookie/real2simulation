# Sidebar tools v1 — S16a contracts, S16b patch, S16c rebuild, S16d search adapter

`contracts.py` exports Python TypedDicts, Draft 2020-12 schema dictionaries,
`validate_call`, `validate_result`, `spec_sha256`, and the reused strict `parse_json`.
The contract validators do not dispatch, write files or execute rebuilds.
`rebuild.py` supplies the separate, local-only execution boundary described below.
Import by file path (existing directory convention contains a hyphen).

## Wire envelope

Call: `{schema_version: "sidebar-tools/1.0.0", id, scene_id, tool, arguments}`.
Result: `{schema_version, call_id, scene_id, tool, status, payload, tool_outputs}`.
All fields required; unknown fields rejected at every locally defined object boundary.
Results must match call id, scene id and tool. `status` is `ok` or `error`.
APIs return defensive copies. Exceptions are `SidebarContractError`; direct
`spec_sha256`/`parse_json` use existing experiment errors (`ValueError` subclasses).
Parse raw JSON using `parse_json` **before** either validator to reject duplicate keys.

### `spec.patch`

Arguments: `{base_spec_sha256, patch}`. A trusted current `base_spec` keyword argument
is mandatory for call/result validation. Digest is SHA-256 of UTF-8 JSON serialized
with sorted keys, `separators=(",", ":")`, `ensure_ascii=False`, `allow_nan=False`.
Whole-section replacement only (NOT RFC 6902/7396, NOT recursive merge): nonempty
patch can replace `environment`, `body`, `placement`, `parameters`, `simulation`.
No scene, experiment id, schema version or template edits; no deletes or defaults.
Each supplied section must be complete according to existing experiment contracts.

Validation order: envelope -> arguments -> existing base `validate` -> current digest
and scene binding -> deep-copied candidate -> existing `validate(candidate)`.
Candidate validation retains units, provenance, unknown-value, numeric and domain checks.
Success payload: `{spec, spec_sha256, rebuild_required: true}`; spec must exactly equal
the validated candidate. `tool_outputs: []`; input values cannot become tool-backed facts.
No spec persistence/rebuild happens here. S16b owns application and the rebuild handoff.

#### S16b application boundary

`Build/sidebar-tools/spec_patch.py` exports
`apply_patch(call, *, base_spec, scene, scene_root) -> ToolResult`:

```python
from importlib import import_module

patch_tool = import_module("Build.sidebar-tools.spec_patch")
call = patch_tool.contracts.parse_json(request_json)
try:
    result = patch_tool.apply_patch(
        call, base_spec=current_spec, scene=current_scene, scene_root=bundle_root)
except patch_tool.SidebarContractError as error:
    # Reject without changing current_spec or scheduling a rebuild.
    raise
```

The caller supplies the **trusted current** spec and authoritative scene bundle;
neither comes from model arguments. The application validates the S16a call,
applies whole sections to a deep copy, runs existing experiment `validate_setup`
(including scene assets, bounds, gravity, collision and stability preflight), and
validates the correlated success result before returning it. Numeric-only
`validate` is not enough: an otherwise valid spec outside the scene is rejected.
Both request and scene-preflight rejections raise the existing typed
`SidebarContractError`; preflight errors retain their original exception as cause.
No error is converted to success or a queued acknowledgment. Input objects remain
unchanged; returned specs do not alias them. `tool_outputs` is always empty.

`rebuild_required: true` is a **handoff**, not a rebuild call or job receipt.
This function has no dispatcher/callback, file writes or network calls: rejected
patches cannot start a rebuild, and accepted patches do not start one either.
S16c owns process-local spec storage/rebuild plumbing, including rechecking the
trusted current digest at commit/admission time and serialization. It admits no
GPU, paid, remote or physical jobs; their resource/budget gates are not bypassed.
Preflight does not authenticate rights/provenance or prove simulator accuracy.

### `scene.rebuild`

Arguments: `{spec_sha256, spec}`. Existing experiment validation, digest and scene-id
binding are mandatory. Legacy acknowledgment payload:
`{job_id, spec_sha256, state: "queued"}`. Queued is **not** completion evidence.
S16c local completion payload (`CompletedRebuildPayload`):
`{job_id, spec_sha256, state: "completed", output_sha256: {output_id: sha256, ...}}`.
Completed requires nonempty S14 numeric outputs and an exact matching hash map.
The digest uses normalized `validate_tool_output` JSON, sorted keys, compact
separators, UTF-8, `ensure_ascii=False`, `allow_nan=False`. `output_sha256(output)`
is exported for independent verification. No hash field is added to the strict
S14 output shape; the correlated payload carries the receipts instead.

`tool_outputs` may carry already-code-built fitter/simulator receipts, validated with
`contracts.agent.validate.validate_tool_output`; unique output ids are mandatory.
They do not imply a queued rebuild completed. Empty is normal for queued only. Never source these
receipts from a model or from patched inputs. S14 rendering still separately validates
every number reference. Source/job ownership remains a caller trust boundary.

#### S16c local execution boundary

```python
from importlib import import_module

RebuildSession = import_module("Build.sidebar-tools.rebuild").RebuildSession
session = RebuildSession(current_spec, scene_path=trusted_scene_json,
                         instruments=explicit_instrument_settings,
                         scratch_dir=existing_private_scratch_directory)
patched = session.handle(validated_patch_call)
completed = session.handle(rebuild_call_for_patched_digest)
# completed["tool_outputs"] goes to existing S14 validate_response/render, never
# concatenate numbers or hashes into model-authored free-text segments.
```

The host owns the session, paths, instrument settings and initial spec; never
construct these from a model's request. This is a code API, not an authenticated
HTTP endpoint. One lock serializes patch commit, rebuild admission, execution and
receipt publication. `current_spec` is a defensive snapshot. Only S16b's successful
scene-bundle-validated patch can mark a revision rebuildable. A raw valid spec or
forged success envelope does not grant admission; rebuild arguments must match
the internal current digest. Bundle metadata drift rejects the session; assets
and setup preflight are rechecked, including on cached requests.

The handler calls `Build.lab.pipeline.run_lab`, which uses the existing validated
setup exporter, Node RK4 simulator, synthetic instruments and `Build.fitter.api`.
It supports the existing synthetic free-fall/projectile lab only. Other templates
and physical scenes return `not_ready` without starting compute. No provider, GPU,
network, automatic retry, install or spend path is exposed. Temporary spec files
are confined to the caller's scratch directory and removed after execution.
Keep the trusted bundle immutable during execution; the host still owns filesystem
access and cross-process coordination (the session lock is process-local).

Simulator quantities reuse actual lab instrument observations, including their
explicit uncertainty/source; fitter gravity reuses `fit_tool_output`. Evidence
binds outputs to job/spec and visibly says synthetic/not calibrated. No input
parameter is converted into an asserted measurement. Each output validates as
S14 `agent-tool-output/1.0.0`; model numeric refs are still separately checked.

Malformed/stale patch calls raise `SidebarContractError` without state changes.
Valid but unadmitted rebuilds return correlated `not_ready`/`stale_spec` errors.
Local execution failures return a sanitized `internal_error`, no numbers, and
retain the accepted revision for an **explicit caller retry**. A completed
revision caches its original job/outputs; repeated rebuild requests (even with a
new call id) return the same receipt without rerunning. Returned objects do not
alias the cache. A subsequent accepted patch invalidates the cache. State is
in-memory only: restart requires a fresh validated patch; durable jobs, server
wiring and provider/search integration are not claimed by S16c.

SHA-256 detects receipt/content mismatches, not forgery by an attacker who can
replace both content and digest. Trusted host custody remains mandatory.

### `library.search`

Arguments: `{query, limit, templates, licenses}`. Nonblank query <=256 characters,
limit integer 1..20 (not bool); arrays unique; empty arrays mean no filter.
Templates reuse S08/S14's canonical template set. Licences reuse the exact scene-source
schema enum (`Public-Domain`, `CC0-1.0`, versioned `CC-BY-*`/`CC-BY-SA-*`, Pexels/Pixabay).
No NC/ND/unknown licence vocabulary. The searchable source is local/metadata-only,
not web acquisition. Baseten receives the query and candidate card metadata, never
raw media, artifact numeric arrays or report contents.

Success payload: `{query, items}` (zero matches is valid). Query echoes exactly; items
are unique by id, <=limit, and match both requested filter sets. Each item requires:

| Field | Shape |
|---|---|
| id, title, template, synthetic | Stable identifier, display title, canonical template, boolean |
| source | clip_id (including uppercase registry IDs), source_url, license, license_url, attribution, approval_evidence; or synthetic `{kind: "synthetic", description}` without invented licence/clip |
| artifact | path, sha256 (lowercase 64-hex immutable-content digest) |
| provenance | run_id, evidence, numeric_label: measured/simulated/synthetic/unknown |

URLs are HTTPS metadata, never fetched. Artifact/evidence paths are portable relative
references without traversal, absolute paths, drive letters or backslashes. Path/string
validation does not resolve files or authorize serving them. Synthetic flag and provenance
must agree; no numeric values appear in search cards. `tool_outputs: []`.

Store-backed items additionally retain `availability: metadata-only`, `scale_verified:
false`, `scale_label: SCALE_UNVERIFIED`, `gates` and `limitations`. These fields are
optional for backward-compatible S16a-c callers but mandatory in the search projection.
Synthetic sources require a synthetic item/provenance label, and cannot match an external
licence filter. Clip-backed fixture records also retain a synthetic provenance label.

#### S16d/S16f provider-selectable search adapter

`import_module("Build.sidebar-tools.library_search").search(call, *, manifest_path=None,
evidence_root=ROOT, environ=None, send=transport)` returns the correlated result above.
Invalid input raises the same `SidebarContractError` as the existing tools. The caller
loads environment secrets in its existing in-process loader (or passes its mapping as
`environ`); never put credentials in tool arguments. This module does not auto-load `.env`.

`SIDEBAR_SEARCH_PROVIDER` selects exactly `baseten` or `fireworks`. Omission retains
the existing Baseten default; blank/unknown values refuse without a request. Merely
populating Fireworks credentials never selects it. There is **no automatic failover,
retry, provider chain or Meta API fallback**. To switch after a failure, the trusted
host must explicitly change this configuration and invoke search again. Tool/model
arguments cannot select a provider; no global settings or `.env` files are changed.

For Baseten, all three names `BASETEN_API_KEY`, `BASETEN_BASE_URL`, `BASETEN_MODEL` must be populated.
The model must exactly equal **`meta-models/muse-spark-open-1026`**; mismatches fail closed,
without echoing the configured value. URL is restricted to
`https://inference.baseten.co/v1` (optional trailing slash).

For Fireworks, set `SIDEBAR_SEARCH_PROVIDER=fireworks` and populate
`FIREWORKS_API_KEY`, `FIREWORKS_BASE_URL`, `FIREWORKS_MODEL`. URL must be exactly
`https://api.fireworks.ai/inference/v1` (optional trailing slash). Model must be an
explicit `accounts/<account>/models/<model>` resource: lowercase account characters
`a-z0-9_-` (1..64), model characters `a-z0-9_.-` (1..128). There is no default model,
invented Muse alias, model discovery, availability check or authorization to spend.
The response must include that exact model ID; missing/different IDs fail closed.
Baseten retains its previous missing-response-model compatibility, never a different ID.

Each valid wire invocation emits one INFO record
`library.search provider=<provider> model=<model>` through the module logger; host
logging configuration must enable INFO. Invalid configuration is never echoed:
unknown provider/model use `unconfigured`; Baseten logs only its fixed intended pin.
No query, credential, URL, provider body or exception text is logged.

Search now always emits a code-owned top-level `execution` receipt alongside the
unchanged payload and empty `tool_outputs`:

```json
{"provider":"fireworks","model":"accounts/fireworks/models/synthetic-ranker","state":"served","meta_bonus_claimed":false}
```

This example model is **synthetic test configuration, not an available-model claim**.
`provider`/`model` describe the validated selection (null when unknown), not proof a
request was served. `state` is `not_requested` for configuration/catalogue rejection
or empty local candidates; `failed` for an attempted but unavailable/unusable call;
`served` only for a validated model response, including an empty ID selection.
Thus empty local search never claims hosted inference. The schema permits missing
`execution` only for older contract callers; this adapter always supplies it on
valid-wire results. Rebuild/patch results cannot carry this search-only receipt.

`meta_bonus_claimed` is always **false**, including on Baseten; it is not a legal
eligibility verdict. Fireworks success is labelled Fireworks plus its exact configured
model, **not Muse, Meta API, Llama bonus or open-weight bonus evidence**. A returned
model identifier alone does not independently establish model identity or bonus
eligibility. An injected fake transport is still only offline synthetic evidence.

Search reuses `Build.library.validate.validate_file`, current owner/acquisition checks,
content-addressed artifact hashes, and evidence/numeric pointer checks. Default source
is the existing `test-data/library-artifacts/free-fall.json`; a trusted caller may select
another accepted manifest under `evidence_root`. No new index or guessed experiments.
Artifact JSON is read once per distinct digest per call; there is no stale cross-call
cache. The current source yields four **synthetic simulated**, metadata-only free-fall
cards. The RM02 reconstruction descriptor has no verified template and is omitted rather
than mislabelled as free fall. Source paths remain local references, not playable URLs.

The model ranks the filtered, validated candidates and may return only `{"ids":[...]}`.
Only IDs selected from this exact catalogue are accepted; duplicate/unknown IDs, extra
fields, prose, non-JSON, tool calls, non-stop completions and wrong response model IDs
are unavailable results. All returned fields come from the store, never model text.
Search cards are **tool-result payloads**, not S14 numeric receipts; `tool_outputs` stays
empty and cannot authorize numeric claims in agent text. No free-form explanation is
returned. Empty candidates need no provider request; an empty model selection is valid.

Transport is stdlib urllib/json, one POST `/chat/completions`, Bearer authorization,
non-streaming, 15-second timeout, no retries/redirects, 256-KiB request / 64-KiB response
limits. Config/library/provider failures return `status: error`, `code: not_ready`, and a
readable `Library search unavailable: ...` message without raw exception content. HTTP
error bodies are closed without reading/logging. This adapter is callable, not a new
route, UI dispatcher, billing guard or permission grant: **S16e must verify balance,
authorized live invocation, deployed routing and exact pinned model availability**.

Request shape follows the [Meta Baseten cookbook](https://github.com/meta-models/meta-oss-cookbook/blob/main/muse-spark/hosted/baseten.md).
Its current example uses the unpinned alias; this adapter deliberately retains the
owner-required pinned ID instead. Documentation lookup is not live inference proof.
Fireworks endpoint, Bearer authentication and chat-completion shape follow its
[official Chat Completions reference](https://docs.fireworks.ai/api-reference/post-chatcompletions)
(read Oct30 2026). No hosted-model availability or pricing was inferred from it.

## Errors and downstream work

Error payload: `{code, issues: [nonblank string, ...]}`; 1..32 issues, no tool outputs.
Codes: invalid_request, stale_spec, not_found, not_ready, budget_blocked, internal_error.
`validate_result` requires a valid originating call (including a trusted base for patch);
malformed pre-envelope transport errors are not this correlated-result contract. Never
return stack traces/secrets as issues; caller owns safe human-readable errors.

S16a-d local contract/application/rebuild/offline search scope does not complete S16e-h,
parent S16, real-scene integration or Gate A/RS.
No live Baseten/Fireworks/Meta call, dependency install, public upload or spend in S16d.

## Checks

```powershell
python -m unittest discover -s tests/sidebar-tools -v
python -m unittest discover -s tests/spec -q
python -m unittest discover -s tests/agent -q
```

Tests use visibly synthetic metadata and existing experiment fixtures, not physical evidence.
