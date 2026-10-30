# Sidebar tools v1 — S16a, offline contracts only

`contracts.py` exports Python TypedDicts, Draft 2020-12 schema dictionaries,
`validate_call`, `validate_result`, `spec_sha256`, and the reused strict `parse_json`.
No dispatch, file writes, network, models, provider wiring or rebuild execution.
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

### `scene.rebuild`

Arguments: `{spec_sha256, spec}`. Existing experiment validation, digest and scene-id
binding are mandatory. Success payload: `{job_id, spec_sha256, state: "queued"}`.
This is an acknowledgment contract, **not** evidence that any worker started/completed.
The future dispatcher must compare the digest against its trusted persisted current spec
and perform scene-bundle `validate_setup`, budget/auth/resource gates before admission.
This contract checks numeric inputs only; it does not authenticate a caller or grant spend.

`tool_outputs` may carry already-code-built fitter/simulator receipts, validated with
`contracts.agent.validate.validate_tool_output`; unique output ids are mandatory.
They do not imply the queued rebuild completed. Empty is normal. Never source these
receipts from a model or from patched inputs. S14 rendering still separately validates
every number reference. Source/job ownership remains a caller trust boundary.

### `library.search`

Arguments: `{query, limit, templates, licenses}`. Nonblank query <=256 characters,
limit integer 1..20 (not bool); arrays unique; empty arrays mean no filter.
Templates reuse S08/S14's canonical template set. Licences reuse the exact scene-source
schema enum (`Public-Domain`, `CC0-1.0`, versioned `CC-BY-*`/`CC-BY-SA-*`, Pexels/Pixabay).
No NC/ND/unknown licence vocabulary. Search is local/metadata-only; not web acquisition.

Success payload: `{query, items}` (zero matches is valid). Query echoes exactly; items
are unique by id, <=limit, and match both requested filter sets. Each item requires:

| Field | Shape |
|---|---|
| id, title, template, synthetic | Stable identifier, display title, canonical template, boolean |
| source | clip_id, source_url, license, license_url, attribution, approval_evidence |
| artifact | path, sha256 (lowercase 64-hex immutable-content digest) |
| provenance | run_id, evidence, numeric_label: measured/simulated/synthetic/unknown |

URLs are HTTPS metadata, never fetched. Artifact/evidence paths are portable relative
references without traversal, absolute paths, drive letters or backslashes. Path/string
validation does not resolve files or authorize serving them. Synthetic flag and provenance
must agree; no numeric values appear in search cards. `tool_outputs: []`.

**S18 boundary:** base main dc74261 has no `Build/library` yet. This wire projection
preserves established scene provenance field names and exact licence values, adds rights
URL, immutable artifact digest, actual-run/evidence references and numeric label. S18's
full manifest may contain additional metadata; an S16e adapter must explicitly project it
into this shape, not pass arbitrary manifest fields through. Direct compatibility with an
unmerged S18 schema is NOT asserted/tested; no unmerged files were read or imported.
Structural validation cannot prove licence truth, owner approval, artifact bytes, actual
run origin or physical calibration. Library serving must verify these against S18 receipts.

## Errors and downstream work

Error payload: `{code, issues: [nonblank string, ...]}`; 1..32 issues, no tool outputs.
Codes: invalid_request, stale_spec, not_found, not_ready, budget_blocked, internal_error.
`validate_result` requires a valid originating call (including a trusted base for patch);
malformed pre-envelope transport errors are not this correlated-result contract. Never
return stack traces/secrets as issues; caller owns safe human-readable errors.

This completes S16a contract scope, not S16b-g integration or parent S16/Gate A/RS.
No Baseten/Fireworks/Meta call, dependency install, search engine, public upload or spend.

## Checks

```powershell
python -m unittest discover -s tests/sidebar-tools -v
python -m unittest discover -s tests/spec -q
python -m unittest discover -s tests/agent -q
```

Tests use visibly synthetic metadata and existing experiment fixtures, not physical evidence.
