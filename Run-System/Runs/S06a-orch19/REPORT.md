# S06a-orch19 — DONE (pinned MapAnything Modal image built + CPU dry-run contract; $0.0156)

Lane CODEX-1; model anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Issue 11:47:42Z, deadline 12:17:42Z;
worker start 11:48:40Z, work stop see TIMEBOX.json. Worktree .worktrees/S06a-orch19, branch run/S06a-orch19 from main 526ec0c.
Canonical controls untouched; no merge (controller accepts).

## Delivered (Owns only)
- Build/gpu/image_spec.py — pins + offline CPU dry run (no Modal/network): lock LF-sha256, every requirement ==-pinned or
  code-rev zip, core pins (torch 2.8.0/vision 0.23.0/audio 2.8.0/numpy 2.2.6/timm 1.0.20/hf-hub 2.3.0), mapanything @ 3d10cf7,
  agreement with evidence/S05/upstream/revisions.json, weights apache-2.0 + ungated, NC id rejected.
- Build/gpu/test_image_spec.py — 4 tests: current pins pass; CRLF checkout hashes as LF; drift/unpinned rejected; NC/moved weights rejected.
- Build/gpu/modal_image.py — IMAGE = debian_slim py3.11 -> pip lock -> HF_HOME=/weights/hf -> baked snapshot_download(apache @ 00f9c24)
  -> HF_HUB_OFFLINE=1; refuses to build if dry run fails; CPU check() (1 CPU/4 GiB/300 s/retries 0/max 1 container).
- infra/modal/README.md — the contract: inputs, image, offline + remote CPU dry run, how S05c/S06b-d reuse IMAGE, safeguards, measured/unverified.
- evidence/S06/S06a/ — dry-run-offline.json, dry-run-remote.json, run-log.txt, tests.txt, pre/post-verify.txt, billing-pre/post.csv, job-ledger.json.

## Modal job (one, CPU only, within standing auth; <= $0.50 reserved)
App ap-Gf1f5xsIuhpOIGFiwLE1zr 11:52:44Z -> stopped 11:55:14Z, rc 0, retries 0, own containers [] after (only live container
belonged to S05c ap-Pez26...). Layers: pip 93.2 s, weights 28.1 s (4 files, 4,914,071,149 B), envs ~2 s each.
Remote: versions match pins (mapanything 1.1.4); weights loaded local_files_only under HF_HUB_OFFLINE=1; MapAnything importable.
Cost **$0.0156446** (billing report hourly CSV at 11:56:41Z; may lag). Ledger reserve $0.50, release ~$0.48 suggested.
Pre: billing CLI read OK, no own apps running, containers [] (11:51:42Z).

## Fresh checks
- python -m unittest discover -s Build/gpu: 4/4 OK (Python 3.14 local).
- python Build/gpu/image_spec.py: rc 0, errors [].
- modal run Build/gpu/modal_image.py: rc 0 (Modal 1.6.3 via uv py3.11; MODAL_TOKEN_* loaded from .env by key name, values never printed).
- Secret scan of evidence/S06, Build/gpu, infra: 0 hits.

## Limits / not verified
- No GPU ran: CUDA use of this image, A10G warm-start time with cached layers, and the ~155 s saving are NOT measured (S06b/S05c).
- Container dependency licence audit not done (S06b acceptance). Modal image cache retention not checked.
- Lock is referenced from Build/reconstruction/spike/ (S05c-owned); any edit there fails the dry run until re-pinned here (intended).
- No scene, inference, scale, Gate R or physical evidence.

## Ponytail full
Reused: S05b's verified lock + revisions.json (referenced, not copied), Modal's native layer cache and pip_install_from_requirements /
add_local_python_source, huggingface_hub snapshot cache + HF_HUB_OFFLINE instead of a Volume or custom downloader, existing uv/modal
1.6.3 route and billing CLI. Smallest complete: 3 code files (~130 lines) + 1 doc. Skipped: Modal Volume, GPU smoke, separate
lock copy, deployment, wiring into spike/modal_rm02.py (S05c-owned), second warm-start run (contract allowed a single job).
Risk: first GPU job on IMAGE may still expose CUDA/driver issues not seen on CPU.

## Communication
Silent; one completion line to controller.
