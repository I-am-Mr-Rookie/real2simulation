# SAM3.1 identity — observed metadata, NOT verified model bytes

Observed 2026-10-28, approximately14:08–14:11 UTC. Official HF pages were read in
the signed-in ChatGPT in-app browser only. Account identifiers were not exported.
No download/copy wizard, model transfer, token read or authentication change.

## Exact repository/files

Repository: [facebook/sam3.1](https://huggingface.co/facebook/sam3.1/tree/main).
Observed repository head: `daa63191845a41281374e725f4c9e51c7a824460`.
The file-specific commits below are distinct from that repository head.

| Item | Actual observation |
|---|---|
| [sam3.1_multiplex.pt](https://huggingface.co/facebook/sam3.1/blob/main/sam3.1_multiplex.pt) | Xet, displayed3.5GB; file commit `1f6f2c756fc7fb4b5d4ef2f83a6a2f2e5aeefc4b` |
| [Small raw pointer](https://huggingface.co/facebook/sam3.1/raw/main/sam3.1_multiplex.pt) | `size 3502755717`, `oid sha256:0567debeec80ba4ac6369540c6c248025283cb3ff2b92827509e57e2b3541cb6` |
| Xet pointer details | Xet hash `850acf278dd67da448a025b7a74899ca26914e56051cd88e7b168c362dd63f00`; not interchangeable with SHA256 |
| [config.json](https://huggingface.co/facebook/sam3.1/blob/main/config.json) | displayed25.8kB; file commit `c0508563cbfea1c9d02ea53e095e54406bab8e78`; raw text25843 characters, NOT an asserted byte count or SHA256 |

Raw configuration parsed successfully in the browser: `architectures=["Sam3VideoModel"]`,
`model_type="sam3_video"`, `transformers_version="5.0.0.dev0"`.
Includes detector/tracker configuration and tracking thresholds. This metadata
does not require installing Transformers for the project's official native loader.
No authoritative config digest was obtained. File revisions and model pointer
digest are upstream metadata, not a checksum of bytes downloaded by this worker.

Other listed files include processor/tokenizer assets and LICENSE. The repository
labels its licence `other`; reuse existing custom-SAM agreement decision/owner
acceptance, not MIT/Apache assumptions or pyproject classifier text.

## Software and loader comparison

Exact official software revision inspected/reused:
`facebookresearch/sam3@f1647e8d0c1d280991f4d1b7d974c2704537fe66`.
This immutable known revision was freshly readable; current GitHub main SHA was
not established (public commit-history retrieval failed). Do not label this the
latest release or replace it by floating main in a later run.

[Pinned builder](https://raw.githubusercontent.com/facebookresearch/sam3/f1647e8d0c1d280991f4d1b7d974c2704537fe66/sam3/model_builder.py)
lines618–633 select the exact HF repository, config and checkpoint above. Its
automatic download helper has **no revision argument**: later retrieval must
explicitly pin the HF revision separately, then supply the verified local path.

`Build/measurement/tracking.py:139–153` already uses the recommended
`build_sam3_multiplex_video_predictor`, explicit local checkpoint and execution
opt-in; compilation, warm-up and asynchronous frame loading disabled. Reuse it.
The pinned builder constructs architecture in code, resolves packaged BPE
`sam3/assets/bpe_simple_vocab_16e6.txt.gz`, reads checkpoint with
`torch.load(..., map_location="cpu", weights_only=True)`, then moves model to CUDA.
The config is fetched by its automatic helper but not parsed into this native
builder's architecture. Preserve both config/source identity; don't invent a
Transformers loader or substitute an older sam3 checkpoint.

Important untested defaults: `use_fa3=True`, `use_rope_real=True`,16 objects and
multiplex16. Project wrapper does not override these. `compile=False` alone does
not establish optional CUDA-kernel availability or GPU compatibility. No runtime
patch is authorized here. Missing/unexpected state keys are not strict fatal
checks everywhere upstream: a later run must capture and review them explicitly.

## Requirements versus existing S05b proof

[Pinned README](https://raw.githubusercontent.com/facebookresearch/sam3/f1647e8d0c1d280991f4d1b7d974c2704537fe66/README.md)
specifies Python>=3.12, Torch>=2.7, CUDA>=12.6 with CUDA GPU. Its current example
uses torch2.10.0/cu128; that is not evidence this project's2.8 stack ran SAM.
[Pinned package manifest](https://raw.githubusercontent.com/facebookresearch/sam3/f1647e8d0c1d280991f4d1b7d974c2704537fe66/pyproject.toml)
declares Python>=3.8 but NumPy>=1.26,<2, timm>=1.0.17, ftfy6.1.1, regex, iopath,
typing_extensions, huggingface_hub. Prefer stricter README runtime prerequisite;
record metadata conflict, not a supported-Python3.11 claim.

Reused `evidence/S05/S05b/recovery5/cpu-import-result.json`: actual Python3.11.12,
Torch2.8.0+cu128, torchvision0.23.0+cu128, torchaudio2.8.0+cu128, NumPy2.2.6,
MapAnything1.1.4, CPU imports only. Python is below SAM README minimum; NumPy
violates SAM manifest bound. CUDA-tagged wheels do not prove a GPU/driver or
SAM import. A SAM-specific Python3.12/NumPy<2 environment and targeted dependency
validation are necessary; do not mutate the already proven MapAnything lock.
No authoritative minimum VRAM was established. The3.5GB file size is not a VRAM
requirement, and S05b's L4 request is not SAM sizing evidence.

## Evidence layers

1. Owner screenshot: SAM3 gating collection ACCEPTED, preserved prior receipt.
2. This browser: signed-in HF experience (Liked/repository UI), gated pointer and
   actual config text accessible; no fresh personal/profile export.
3. File identity: authoritative names/revisions/pointer metadata above.
4. Checkpoint bytes: NOT fetched, NOT hashed, NOT authorized-download tested.
5. Remote HF authentication / SAM imports / CUDA / inference: NOT verified.
6. Prefix custody remains recovery3 receipt only; no media opened/copied/hashed.
   Metric/calibration approvals absent; GateM physics NOT_RUN, S12 locked.
