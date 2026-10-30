# Gate RS fourth recheck — R-RS-recheck4-orch85

**Verdict: CLEAR. Review DONE; this is NOT a Gate RS pass.**

Reviewed main `b2fc20bea02efce45aa7d993ce6e46f2a7ddd3a9`, including merged S12e-fix4-orch76. Assigned cross-vendor `gpt-6.1-sol/high`, CLAUDE review lane. No product, test, S12 evidence, registry or canonical-control edits. No installs, paid calls or GPU work.

## Prior findings

| Finding | Fresh result |
|---|---|
| F2-R3 [P1] caller-authored tracker admitted | **Closed with the accepted registry held trusted.** All three original synthetic tracks have genuine public IDs/hashes, valid structure, normal v2 predictions and complete synthetic observations. Native unpatched `Tracked`/`score` still compute diagnostics, but attach no custody and are ineligible. Aggregate NOT_MET; all categories shortfall. |
| F2-C [P1] loader bound to another training boundary | **Closed.** Genuine ST03 artifact with a loader bound to the original prefix and a target shifted by 0.01 H refuses before loader read (`evidence` remains None). Training-digest transplant and changing the carried seal both fail the independent gate recheck. |
| F1 / F1-R | **Remain closed on reviewed paths.** Nine identity/trace/commitment mutations and a self-consistent truncated trace refuse before suffix access. Historical recheck3 executes its earlier foreign/overlay/nonfinite controls before stopping at its obsolete exploit assertion. The focused 38-test suite passes. |
| F2-A [P2] approval grant parser | **Remains closed.** Six negated/revoked grant variants refuse through the actual `public_receipt` API; genuine approval accepts. Focused suite additionally covers the original parser cases. |
| F2-L [P2] licence identifier allowlist | **Remains closed.** Eight NC/ND, false-PD, malformed and unknown-version cases refuse through `public_receipt`; existing licence test passes. This is label validation, not a new legal determination. |

## Registry trust boundary — adequate for this project's internal review workflow

`Build/real2sim/score.py:57–74` checks exactly one artifact path+digest entry, the full clip/source/training/suffix seal, presentation-map bytes and the exact ordered inclusive frame range/PTS. `score` checks loader-boundary equality before calling it; the gate re-derives registry custody and compares its digest with the carried receipt.

Fresh scratch-root probes:

- Unknown artifacts, wrong path/digest/seal, duplicate/empty entries, changed map digest or map bytes, changed/reversed frame ranges and spoofed caller PTS refuse.
- Any registry byte change invalidates an old carried custody digest. A freshly derived receipt for the changed registry accepts. Restoring identical historical bytes restores acceptance: **there is no monotonic revocation/anti-replay store**.
- Actual registered artifact digest, seal and map pass. Registry app `ap-2Sbu8Pen5jJhHlNxAhuva6` matches exactly one ledger row reporting 26 frames and $0.02330591, and the accepted S12e-orch45 report identifies that app/job/range. **The ledger row does not contain the artifact digest.** The registry/controller receipt supplies that binding; it is not a provider-signed output receipt.
- `gpu`, `accepted_runs`, object/prompt annotations and the word “committed” are not runtime authentication. Invented ledger/app/run metadata in a scratch registry still passes the custody reader. A caller who can replace the trusted registry and maps can admit all three synthetic tracks and produce synthetic MET without any media/GPU read. This was reproduced in an owned temporary root, with unpatched production functions. It is **not** possible in the same probe with the real registry intact.

**Who may add entries:** technically any filesystem/repository writer; under this project's Owns + serialized controller integration policy, the authorized S12 evidence owner proposes entries and the controller independently reviews/accepts their diffs. Git commit status, actor identity and ledger facts are not checked by the reader. A commit alone is therefore not proof of independent acceptance.

**Judgment:** a versioned, independently reviewed allowlist is adequate here because controller-approved repository state is already trusted for code, clip rights and acquisition identity. F2-R3 asked for an independent accepted artifact receipt, not resistance to a malicious code/registry maintainer. The current entry has been checked against its existing report, ledger and exact artifact/map bytes. Requiring provider signatures, a separate service or per-pixel attestation would not be a proportionate repair for this internal solo-project pipeline. This CLEAR does **not** authorize automatically promoting arbitrary future registry entries, especially entries added by the artifact author without independent review.

### H1 [P3, nonblocking] Preserve the admission/replay limitation in future integrations

Registry writers are trusted as code writers. The loader does not enforce commits, controller identity, ledger hashes/app linkage or revocation freshness. Continue reviewing every registry diff against accepted job evidence; never expose registry writes to ordinary artifact submitters. Before accepting untrusted uploads or revocation-sensitive replay, move admission authority outside caller-writable evidence (or pin a separately trusted accepted snapshot). No product change is required for the present internal workflow.

## Runnable evidence and verification limits

From the repository root:

```powershell
python -B evidence/reviews/R-RS/recheck4/review.py
python -B -m unittest -v tests.prediction.test_score tests.prediction.test_boundary tests.prediction.test_predict tests.prediction.test_overlay
```

- [review.py](recheck4/review.py): PASS; [results.json](recheck4/results.json), [probes.txt](recheck4/probes.txt), [source-hashes.json](recheck4/source-hashes.json). Protected `Build/real2sim`, `Build/pipeline`, `tests/prediction`, `evidence/S12` hashes identical before/after.
- Historical `recheck3/review.py` is loaded and executed unchanged, redirecting **only its output directory** to owned `recheck4/rerun-recheck3/`. It now fails at line 99's assertion that a forged tracker passes `_tracking_ok`; this is expected closure, not a new failing product regression. [Recorded traceback](recheck4/recheck3-rerun.txt). The later historical assertions are replaced by the explicit current probes, not claimed to have run past that failure.
- Focused suite **38/38 OK**: [log](recheck4/tests-focused.txt).
- Broader discovery **44 run: 42 pass, 1 failure, 1 error**, both simulator-dependent parameter tests. [Log](recheck4/tests-prediction.txt). Direct import confirms missing worktree dependency `@dimforge/rapier3d-compat`: [diagnostic](recheck4/simulator-import.txt). No dependency installed or product path changed; full simulator integration remains unverified here. S12e-orch45's report documents the same worktree-dependency prerequisite. This does not block the reviewed custody/boundary checks.

Actual unpatched ST03 score matches every stored score field; aggregate matches the saved result: **Gate RS NOT_MET**, **7/466**, coverage **0.015021459227467811**, RMS **0.1981633916341227 H**, median null, all categories shortfall. Gate M remains NOT_MET. Synthetic MET in the trusted-registry mutation probe is explicitly an admission-boundary demonstration, never measured physical success.

Ponytail full: reused original review fixtures, `Tracked`, `score`, registry reader and validators; one standard-library assert harness, no new attestation framework, no product repair. Skipped live GPU/provider verification and dependency setup by scope. Residual risk is trusted-maintainer admission, not an ordinary caller tracker bypass.
