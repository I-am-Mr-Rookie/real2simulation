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
- Added focused real subprocess tests and the missing-source execution receipt.
- Updated runtime README with the reproducible command and explicit boundary.

## Ponytail full/default applied

Reused the existing pinned runtime lock, loader, upstream source identity, BPE
path and adapter; added one small standard-library preflight rather than a new
runner, installer, dependency, download wrapper, or unsupported kernel flag.
Skipped train/dev/notebook extras and all model/runtime execution because they
were not authorized and are unavailable in this checkout.

## Fresh checks

- `python -m unittest tests/measurement/test_sam_runtime.py -v`: 2 PASS.
- `python -m unittest discover -s tests/measurement -p 'test_*.py' -q`: 67 PASS.
- `python -m py_compile Build/measurement/runtime/preflight.py tests/measurement/test_sam_runtime.py`: PASS.
- Missing-source preflight: exit 2, JSON `ok=false`, no import/download; receipt
  `evidence/S07/S07b/swarm7/preflight-missing.json`.
- `git diff --check`: PASS.

## Limits / next action

The preflight can PASS only when a future authorized Linux/Python3.12 checkout
contains the exact source and packaged BPE bytes. It does not verify installed
Torch/CUDA/FlashAttention/cc_torch, checkpoint custody, import, VRAM, media
custody, or physical calibration. Future owner-authorized runtime work should
run this preflight before any checkpoint boundary and preserve its JSON output.
No shared controls were edited; parent serializes integration.

Communication compliance: no coordination messages were sent; this report is
the required final pointer.
