# SAM3.1 dependency-only candidate (not a verified runtime)

Separate Linux x86_64/Python3.12 environment; never merge this NumPy1.26 lock
into S05b's Python3.11/NumPy2 environment. Torch2.8/vision0.23 retain the existing
aligned family and meet the pinned upstream README's Torch>=2.7 floor. This is
resolver evidence, not proof of imports, CUDA, kernels, memory or SAM inference.

Source: `facebookresearch/sam3@f1647e8d0c1d280991f4d1b7d974c2704537fe66`.
[Pinned package manifest](https://raw.githubusercontent.com/facebookresearch/sam3/f1647e8d0c1d280991f4d1b7d974c2704537fe66/pyproject.toml),
[pinned installation prerequisites](https://raw.githubusercontent.com/facebookresearch/sam3/f1647e8d0c1d280991f4d1b7d974c2704537fe66/README.md).
All8 declared base dependency constraints were checked against this input.
README Python>=3.12/CUDA>=12.6 requirements take precedence over the package's
looser Python metadata. Existing custom-SAM rights/access receipt still applies;
do not interpret the package classifier as a new MIT checkpoint licence.

Reproduce dependency resolution only (no target-environment installation):

```powershell
uv pip compile Build/measurement/runtime/requirements.in --python-version 3.12 --python-platform x86_64-manylinux_2_28 --no-python-downloads --no-config --default-index https://pypi.org/simple --generate-hashes --no-header --output-file Build/measurement/runtime/requirements-linux-py312.txt
```

The hash-locked file covers47 base/transitive distributions, NOT the SAM source
distribution. Future scoped runtime must separately install the EXACT source
revision above without floating dependency upgrades, capture actual installed
revision/BPE asset, and verify imports before any checkpoint/model execution.
Source packaging/build requirements and optional inference kernels are not covered
by this base lock. In particular upstream builder defaults `use_fa3=True` and
`use_rope_real=True` remain unverified; no kernel-disable flag/patch is inferred.
No train/dev/notebook extras, flash-attention install or checkpoint retrieval ran.

Resolution obtained small package metadata/source metadata, not model weights;
it did not install a target environment or download the multi-GB CUDA runtime.
Actual installation may require source builds and substantial downloads/time.
Receipts: evidence/S07/S07b/recovery6/resolve.json and verification.json, including
an exact offline repeat and immutable upstream manifest bytes/SHA256. This removes
the known dependency-spec mismatch only. Existing budget, bounded stop, auth,
checkpoint identity, input custody and independent review gates remain unchanged.
