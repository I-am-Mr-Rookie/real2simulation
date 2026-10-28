# CLEAN-20261028-2 — PARTIAL

**All 44 files are full-SHA256-identical to surviving canonical counterparts,
but all 44 are TRACKED in their own dormant worktree indexes and none is ignored
there. Deleted nothing.** The contract explicitly prohibits deleting tracked
files; canonical ignore rules do not override another worktree's index/rules.

## Exact result

| Dormant source | Files | Logical bytes | Hash-identical | Deleted |
|---|---:|---:|---:|---:|
| `.worktrees/S02c/test-data` | 22 | 624,701,445 | 22 | 0 |
| `.worktrees/S02c1/test-data` | 22 | 624,701,445 | 22 | 0 |
| Total | 44 | 1,249,402,890 | 44 | 0 |

- 19 media files per tree (38 comparisons) also match the exact SHA256 in
  canonical `evidence/clips/S02c-acquisition.json`, including ST03.mp4 and NASA
  N1/N2/N3. The other three per tree are synthetic `.gitattributes`, `points.ply`
  and `scene.json`; they match canonical bytes but have no acquisition-hash entry.
  These six would independently remain KEEP under the missing-record safeguard.
- Every candidate has an exact absolute candidate -> canonical map, full hashes,
  bytes, allowed root, source index/ignore result, acquisition result, KEEP reason
  and restoration/redirect method in `restoration-map.json`. All copies survive;
  restoration is unnecessary. Historical paths and reports remain valid unchanged.
- Full candidate AND canonical hashes repeated after mapping: PASS. No reparse
  paths or containment escapes accepted. Canonical acquisition manifest rehash:
  PASS. No media viewing, decode, export, reencoding or clip approval changes.
- Canonical and both dormant worktree HEAD/index/status snapshots match before/
  after. Example source index entry for FF01.webm is mode100644/blob
  b60f37f7740c6cd1f374538187ca4f257a5daaaf, not an untracked ignored copy.
  Source `check-ignore -v` returns1; even `--no-index` returns1 for that example.
  Canonical FF01 is ignored by `.gitignore:50`, illustrating the different rules.
- Protected r-m-review ST03 prefix: all **271 JPEGs / 49,873,994 bytes** remain;
  exact filename/length/mtime metadata unchanged. Prefix content was not opened
  or rehashed; this is presence/metadata verification, not renewed image custody.
- Metadata-only canonical top-level inventory before/after: **3,060,439,242
  logical bytes / 22,847 files**, unchanged; zero reparse entries. No enumeration
  errors. Physical allocation/hardlinks were not measured; savings are exactly
  **0 files / 0 logical bytes**, not an inferred disk-space saving.
- Sanitized Win32_Process scans: 381 then375 processes; no exact candidate-tree
  command-line matches. Fresh app snapshot lists only this worker/controller
  active among retrieved chats, neither based in a dormant source. This is NOT
  exhaustive open-handle/cwd proof. No deletion relied on that limited evidence.

## Scope, evidence and verification

Contract read FIRST. Current canonical AGENTS, saved OWNER_INSTRUCTIONS, relevant
controls, protocol, README/owner checklist/plan context and latest three available
reports inspected. Original scanned PDF not reread. No archive/private contents
or secret values read. No shared controls edited.

Assigned CODEX-2, existing managed gpt-6.1-sol / medium. Actual backend/effort,
tokens and coding dollars are not independently exposed. **OpenCodex-managed;
not polled**. No new API/GPU/network/install/billing actions or spend. Fresh
separate desktop chat01a182e0-d6fe-7113-9885-ac99d14e7f17 was independently listed
in existing project91e441f8-e40c-4ec4-bea2-de7fa1582d97; see project receipt.

First UTC14:19:10; executable audit14:22:32.897–14:22:55.455 on2026-10-28.
Report finalized approximately14:25UTC, well before14:35 deletion cutoff and
14:40 absolute deadline. Finished early; no waiting for a savings quota.

All authored files ONLY in prepared checkout
`C:/Users/HP/.codex/worktrees/s02g-forensics/2026-10-26 - Meta Global AI Developer Hackathon`,
branch `run/CLEAN-20261028-2`, HEAD6a2a2be5508fbe6717705292a420f0675bdd92d2:

- `Run-System/Runs/CLEAN-20261028-2/{PLAN.md,REPORT.md}`
- `evidence/maintenance/CLEAN-20261028-2/audit.ps1`
- Same evidence folder: `project-receipt.json`, `restoration-map.json`,
  `verification.json`, `git-{before,after}.json`, `inventory-{before,after}.json`,
  `process-{before,after}.json`, `prefix-{before,after}.json`, `final-self-check.json`.

Execution: PowerShell AST parser then native `& audit.ps1`; exit0. Assertions
cover positive containment, same-prefix sibling rejection, parent traversal,
cross-source rejection, inventory sums, exact44 maps, own-index tracked gate,
fresh full hashes and protected-prefix metadata. No Remove-Item command exists
in this audit, so no accidental rerun can delete tracked media. Native Git uses
`--no-optional-locks` for reads. No commits/staging/rebase/merge/fanout performed.
PLAN/REPORT are ignored by existing policy; controller must preserve/integrate
them intentionally along with untracked evidence.

## Ponytail full/default and next action

Reused installed native PowerShell/.NET SHA256/Git and the first cleaner's
metadata stack-traversal pattern. Smallest complete response to the failed gate:
read-only hash audit + KEEP map, no deletion machinery, untracking, replacement
worktree, new dependency, product edits or permission workaround. Evidence links
are represented by filenames above; bulky raw hashes/status live on disk only.

Skipped product rebuild/tests (no product change), destructive restoration test,
handle tooling/install, physical-block measurement, worktree removal/history GC,
new source discovery and remote backup checks. No runtime/physics/license/final-
use acceptance inferred. Source files are byte-identical but not deletable within
this contract; storage contribution remains. Controller should accept this bounded
PARTIAL finding and preserve the evidence; no owner question or wider cleanup
request is necessary for this run. Any later tracked/worktree change requires
its own authorized scope, not an extension hidden in this maintenance task.

Communication: mandatory brief pre-tool/skill update and one finding-change
update only; no optional repeated progress. One authorized terminal callback to
sole controller, then required one-line final report pointer. No other messages.
