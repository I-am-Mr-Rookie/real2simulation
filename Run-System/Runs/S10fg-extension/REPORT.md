# S10fg-extension report

- **Result:** DONE after reviewer P1 corrections. Branch `run/S10fg-extension`; no shared controls/manifests changed.
- **Mystery-g hardening:** exact version `s10-mystery-g-v1`; descriptors/symbols/nonenumerable/accessors rejected before reads; public samples are only finite `{time_s, position_m}`. Trusted handoff deep-sanitizes/freezes the actual S11 `gravity` quantity and preserves `source.label: simulated` plus uncertainty. Handoff is bound to the exact session observation hash, preventing cross-session reuse or caller mutation effects.
- **Replay hardening:** browser-compatible `globalThis.crypto.subtle` SHA-256; rejects accessors, cycles, symbols, sparse/extra/out-of-range array keys and unsupported values; deep-clones before freezing.
- **Checks:** replay/Mystery-g tests pass, including actual Python `Build.fitter.api.handle` cross-language response and mutation/cross-session/version cases; previous simulator suite remains passing. `git diff --check` passed.
- **Skipped:** no template/browser integration; no model-authored success, spend, deployment, or shared-control edits.
