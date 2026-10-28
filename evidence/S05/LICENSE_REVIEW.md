# S05a upstream licence review — 2026-10-27 UTC

This is a technical licence screen, not legal advice or acceptance on Koushik's
behalf. Public metadata/text only; no weights, inference or gated access requested.
See `upstream/sources.json` for immutable URLs, raw and saved byte counts/SHA256, and
`upstream/revisions.json` for exact upstream code/model revisions.
Saved text strips upstream trailing whitespace only; wording is unchanged.

## Decision

| Component | Observed code / weight licence | Decision |
|---|---|---|
| MapAnything code | Apache-2.0; Meta copyright | Eligible primary code candidate, retain notices |
| `facebook/map-anything-apache` | Official model-card metadata Apache-2.0; ungated | Select this exact weight family, not default NC |
| `facebook/map-anything` | README identifies CC-BY-NC-4.0 | Exclude from this project route; do not presume prizes/commercial use permitted |
| SAM 3D Objects code and weights | Custom SAM License, dated Nov 19, 2025; HF metadata `other`, gated `manual` | Not Apache/MIT and not an unconditional permissive route; deferred, no installation or use |

MapAnything sources: [code licence](https://github.com/facebookresearch/map-anything/blob/3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9/LICENSE),
[upstream model selection guidance](https://github.com/facebookresearch/map-anything/blob/3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9/README.md#models),
[Apache model card](https://huggingface.co/facebook/map-anything-apache/blob/00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a/README.md).
Its separate weight-repo `/LICENSE` URL returned **404**, not an extra licence
grant: eligibility relies on official model-card declaration plus upstream
guidance/code text. Before distribution retain Apache text and attribution,
mark modifications, preserve relevant NOTICE if present; audit the installed
dependency tree and bundled assets separately. No blanket licence for all extras.

SAM sources: [code/weight scope in README](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/README.md#license),
[actual licence](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/LICENSE),
[model repository](https://huggingface.co/facebook/sam-3d-objects/tree/2e73555018d2741ccd486e56c24fac41155a1dc6).
It grants conditional use/modification/redistribution; redistribution must carry
the agreement, research publication must acknowledge SAM, and legal/privacy,
trade-control and prohibited-use conditions apply. Terms attach to use/access;
owner authorization is required before proceeding. The project must not relabel
it as Apache-2.0. Model access and dependency licences remain unverified.

## Remaining gates

- S05a licence/fixture acceptance only. Gate R, metric accuracy, gravity, runtime,
  GPU/VRAM, installation and reconstruction quality: **NOT RUN**.
- S05b waits for S02 (approved clips), service/budget preflight and permitted
  compute. AWS remains disabled. No SAM approval is needed to use the selected
  Apache-only path; do not ask the owner to accept optional terms just for S05a.
- Synthetic assets have no external footage or model output. Real clip rights
  remain under S02 `clips.csv`; software permission does not grant media rights.
- No dependency licence audit or full event-eligibility legal determination is
  claimed. Reverify source pins/terms before actual installation and packaging.
