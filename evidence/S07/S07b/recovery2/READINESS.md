# S07b recovery2 readiness — NO-PAID, not execution-ready

Observed 2026-10-28 ~12:59–13:03 UTC. Read-only official pages and existing project records; no checkpoint/config download, login, terms acceptance or inference.

## Exact identity and access

Pinned software revision: `facebookresearch/sam3@f1647e8d0c1d280991f4d1b7d974c2704537fe66`, reused from [TRACKING.md](../../../../Build/measurement/TRACKING.md).

| Item | Current evidence / disposition |
|---|---|
| Release | [Pinned release](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/RELEASE_SAM3p1.md) links exactly `facebook/sam3.1`; do not substitute SAM3 weights. |
| Checkpoint identity | [Pinned builder](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/sam3/model_builder.py), `download_ckpt_from_hf(version="sam3.1")`: repository `facebook/sam3.1`, filename `sam3.1_multiplex.pt`, companion `config.json`. Actual checkpoint/config revision, bytes and SHA-256 remain UNKNOWN. Code naming is not possession/licence proof. |
| Normal access attempt | ONE navigation to [official model card](https://huggingface.co/facebook/sam3.1) using supported in-app browser. Card readable, browser visibly logged out of Hugging Face. Gate requires agreeing to share HF information and logging in/signing up to review conditions. No login/acceptance/download attempted; stopped that access path. This proves current public-card readability, NOT owner access approval or weight availability. No separate file/download endpoint attempted. |
| Model service | Card says checkpoints only, no Transformers integration and no inference provider. Local adapter is not hosted Meta Model API proof. |
| Licence | [Pinned SAM License](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/LICENSE), last updated 2025-11-19, is custom, not MIT/Apache. Covers software and weights; use/access can engage agreement obligations. Redistribution requires the agreement; publication of research results requires acknowledgement; applicable legal/privacy/trade restrictions remain. Human review/authority and actual gated conditions are unresolved; no legal eligibility determination or rights clearance asserted. |

Browser evidence: release AX showed exact model-card link; model-card AX showed gate, Log In/Sign Up, custom licence label and checkpoint-only text. Builder's DOM-backed `file content` exposed exact checkpoint selection and factory defaults. Licence first textbox read timed out; same loaded page's DOM snapshot then exposed agreement, without re-navigation or access bypass. These are observation notes, not a raw page export/screenshot.

## Runtime/config identity

[Pinned installation README](https://github.com/facebookresearch/sam3/blob/f1647e8d0c1d280991f4d1b7d974c2704537fe66/README.md) requires Python >=3.12, PyTorch >=2.7, CUDA-capable GPU/CUDA >=12.6. Its current pinned install example uses Torch 2.10.0/cu128 and lists FlashAttention3/cc_torch optimization installation. No commands installed or executed.

Factory `build_sam3_multiplex_video_predictor` defaults observed in pinned code: max objects16, multiplex16, FA3=true, real RoPE=true, compile=false, warm_up=false, session expiration1200s, probability threshold0.5, asynchronous frame loading=true. Local adapter overrides explicit checkpoint path, compile=false, warm_up=false, asynchronous loading=false; other factory defaults remain inherited. Packaged BPE asset is `assets/bpe_simple_vocab_16e6.txt.gz`. These code defaults plus software revision define intended configuration, not an observed installed/configured runtime or checkpoint digest. Actual GPU/FA3 capability, dependency lock and runtime compatibility remain unverified.

[Fresh local inventory](local-runtime.json): default Python3.14.5, NumPy discoverable; Torch/SAM absent. Exact standard HF model-cache directory `C:/Users/HP/.cache/huggingface/hub/models--facebook--sam3.1` absent. Search restricted to that exact model namespace; no personal/archive scan, custom environment/cache discovery, secret read or heavy import. No approved local SAM3.1 checkpoint path is documented in the inspected tracking/run records. Not a claim that all disks/custom runtimes lack weights.

Reuse [S05b CPU receipt](../../../S05/S05b/recovery5/cpu-import-result.json), not installation: Python3.11.12, Torch2.8.0/vision0.23/audio2.8/NumPy2.2.6/MapAnything1.1.4 actually imported remotely. This is NOT SAM3.1 proof: Python3.11 is below SAM's stated minimum, no SAM import, no observed GPU allocation/output. Recovery5 report records both apps stopped/tasks0/containers empty; this run makes no service-state refresh/call. Retain $1.90 + $0.95 = $2.85 reserves and unchanged $30 authority.

## Prefix/custody and rights

Reuse [S02 owner approval](../../../owner/S02/APPROVAL.md): RM02,RM04,RM05,PD02,PD03,PD04,PD06,PJ03,ST03,BN01 approved for scoped local scene/tracking only. Receipt explicitly supersedes old CSV NO flags only in that scope. No renewed footage approval requested. RM05 is ISS; AP15 NOT_TRACKABLE and ST05 HOLD excluded. This is not calibrated measurement/public redistribution approval.

Inspected existing `clips.csv`, [metadata audit](../../../clips/S02d-metadata-scale-audit.md), S07a/adapter contract and [RM02 integrity receipt](../../../S05/S05b/recovery5/input-integrity.json). Four approved reconstruction PNGs have recorded hashes, e.g. RM02-01 `4848625e64501a230d9b73df7c4b6fc72239bb10cda057d1d61ceb323c962195`, manifest SHA256 `6dc5ada973a7e03e09c56d36f3ac18f29f8221d16a3ccaf30461e120ec417af0`. These are reused historical receipts, NOT fresh media-byte verification. Four sparse reconstruction PNGs do not establish a frozen ordered training-only JPEG prefix or a withheld evaluation suffix.

No real S07 training-prefix custody manifest/resource was supplied or found in the inspected S07/project evidence. This checkout has no `test-data/public` directory; canonical CSV source paths are metadata, not media availability in this checkout. No media recovered, copied, decoded, hashed or uploaded.

Before live SAM: custodian must freeze exact approved clip/segment, original source SHA256, licence/approval receipt, dimensions/unmodified geometry, original frame-index+actual PTS map, final training frame, explicit prompt/object ID, software/config/checkpoint hashes, training JPEG hashes, independent suffix custody and non-mutation controls. JPEG directory must contain only mapped `00000.jpg` onward, at least3 mappings, no symlinks/extra files. Filenames/counts do not attest contents. Do not send a full video and rely on propagation bounds; session creation loads the resource. No suffix-driven tuning/calibration. Physical scale/capture clock remain unknown unless separately evidenced; scene-only tracking may preserve nulls, not invent metric eligibility.

## Decision

PARTIAL readiness clarification. Concrete blockers: HF access/human conditions, unavailable attested checkpoint/config hashes, no validated SAM runtime/GPU capability, and no frozen real training-prefix/suffix custody package. No paid/live run is execution-ready. After owner access review, next bounded step is separately scoped checkpoint/config identity + prefix-custody preparation and supported runtime planning; this contract does not authorize downloads, acceptance, export or execution. GateM remains NOT_MET_INPUT_READINESS / physics NOT_RUN; S12 locked.
