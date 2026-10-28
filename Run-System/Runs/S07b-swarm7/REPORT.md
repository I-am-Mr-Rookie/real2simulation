# S07b-swarm7 — DONE (runtime contract/preflight only)

Parent S07b remains PARTIAL. This child did not download checkpoints, install a
target environment, import SAM, run inference, spend money, or establish Gate M.

## Change

- Added `Build/measurement/runtime/preflight.py`: executable fail-closed check for
  exact SAM3 source revision `f1647e8d0c1d280991f4d1b7d974c2704537fe66`, five
  immutable source/BPE SHA-256 identities, Linux x86_64, and Python >=3.12.
- Its manifest records upstream `setuptools>=61`/`wheel` build inputs, optional
  `flash-attn-3` and `cc_torch` kernels, CUDA >=12.6/Torch >=2.7 requirements,
  and the exact builder flags used by the existing adapter.
- Added focused real subprocess tests covering a positive source fixture, every
  pinned key file's changed/missing state, wrong/ancestor git revisions, missing
  dependencies, and an unsafe source symlink (skipped only where Windows denied
  symlink creation). Added immutable URL/time/byte/hash provenance for every new
  hardcoded source/BPE hash.
- Updated runtime README with the reproducible command and explicit boundary.

## Ponytail full/default applied

Reused the existing pinned runtime lock, loader, upstream source identity, BPE
path and adapter; added one small standard-library preflight rather than a new
runner, installer, dependency, download wrapper, or unsupported kernel flag.
Skipped train/dev/notebook extras and all model/runtime execution because they
were not authorized and are unavailable in this checkout.

## Fresh checks

- `python -m unittest tests/measurement/test_sam_runtime.py -v`: 4 PASS, 1
  skipped (Windows symlink privilege).
- `python -m unittest discover -s tests/measurement -p 'test_*.py' -q`: 70 PASS,
  1 skipped.
- `python -m py_compile Build/measurement/runtime/preflight.py tests/measurement/test_sam_runtime.py`: PASS.
- Missing-source preflight: exit 2, `source_ok=false`, `dependency_ok=false`,
  `runtime_ok=false`; actual installed metadata showed NumPy 2.4.6 vs locked
  1.26.4 and Torch absent. Receipt `evidence/S07/S07b/swarm7/runtime-contract.json`;
  initial missing-source receipt is preserved unchanged.
- `git diff --check`: PASS.

## Limits / next action

The preflight reports `source_ok`, `dependency_ok`, and `runtime_ok` separately;
`runtime_ok` is hard-coded false in this child. It can report source/dependency
identity only when a future authorized Linux/Python3.12 checkout
contains the exact source and packaged BPE bytes. It does not verify installed
Torch/CUDA/FlashAttention/cc_torch, checkpoint custody, import, VRAM, media
custody, or physical calibration. Future owner-authorized runtime work should
run this preflight before any checkpoint boundary and preserve its JSON output.
No shared controls were edited; parent serializes integration.

Communication compliance: no coordination messages were sent; this report is
the required final pointer.
