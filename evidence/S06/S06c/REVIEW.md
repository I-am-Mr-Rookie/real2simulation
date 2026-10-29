# S06c SAM 3D Objects — licence + VRAM review (2026-10-29, S06c-orch22)

Technical screen, not legal advice; no terms accepted, no access requested, no weights/code installed,
no GPU/Modal job. Fetched public, unauthenticated text only (SHA256 of saved bytes):

| File | Source (pinned) | SHA256 |
|---|---|---|
| upstream-README.md | github facebookresearch/sam-3d-objects @ f91db411c50e README.md | F41A81A0...CCA1 |
| upstream-SETUP.md | same rev doc/setup.md | B2C6D257...5895 |
| hf-model-info.json | https://huggingface.co/api/models/facebook/sam-3d-objects (sha 2e735550) | EC800B36...A624 |

## Licence (checked first)
- README @ f91db411: "checkpoints and code are licensed under SAM License" (custom, not Apache/MIT). Same as
  S05a evidence/S05/LICENSE_REVIEW.md; nothing changed.
- HF API today: `gated: "manual"`, `license:other`, sha 2e73555018d2 (= S05a pinned weight rev), not private/disabled.
- setup.md: must request access, then authenticated download; sanctioned-jurisdiction requests rejected.
- evidence/owner/: NO SAM 3D Objects access/terms receipt. evidence/owner/S07/SAM31-ACCESS.md covers the
  "SAM3" gating group collection for SAM 3.1 tracking; whether that group includes facebook/sam-3d-objects is
  UNVERIFIED (would need authenticated check) and is not treated as SAM 3D access.
=> Licence gate: FAIL (owner action needed). Path stays disabled.

## VRAM (checked second)
- Upstream requirement: "NVIDIA GPU with at least 32 Gb of VRAM" (setup.md) -> MIN_VRAM_MIB = 32768.
- Our measured GPU: A10G 23028 MiB (evidence/S06/S06b/smoke-remote.json, image_spec.GPU) -> FAIL.
- Needs a >=32 GB class (e.g. Modal L40S 48 GB / A100 / H100, or owner-planned AWS g6e.xlarge L40S); cost NOT
  measured or priced here. AWS stays off for agents.
- Environment: upstream uses mamba env + torch 2.5.1/cu121 + pytorch3d + kaolin; incompatible with the S06a
  lock (torch 2.8.0/cu128). A SAM 3D path would need its own separate image + licence audit (not attempted).

## Delivered fallback
Build/gpu/sam3d_option.py: off by default (R2S_ENABLE_SAM3D=1 required) AND owner receipt
evidence/owner/S06/SAM3D-ACCESS.md AND VRAM >= 32768 MiB AND a packaged runner; any unmet gate or runner
exception returns scene-schema box colliders (primitive path). Receipt: gate-default.json (synthetic box input).
Tests: tests.txt.

