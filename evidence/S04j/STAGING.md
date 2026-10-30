# S04j deploy-staging note for S15k (stage.py NOT edited here)

/api/library/* spawns `python -c ... Build.library.guest.load_guest()` with cwd = repo root
(`R2S_REPO_ROOT` overrides; default `<Build/web>/../..`; `R2S_PYTHON` overrides interpreter).
For the dev image the route needs, in addition to Build/web:
- python3 + fastapi (guest.py imports it at module top)
- Build/library/*.py (guest, playable, validate, example, ...) and Build/library/loader.mjs (client import, bundled at build)
- test-data/library-artifacts/ (catalogues, playable.json, objects/sha256/*)
- whatever custody files Build/library/playable.load_index / validate.validate_file re-hash (evidence paths named in
  playable.json custody/producers, e.g. evidence/S10/acceptance/acceptance.json, Build/simulator/*.mjs)
If any is missing the route fails closed: 503 library_unavailable; page shows "Library unavailable".
Verify against infra/railway/dev/stage.py allowlist; S15k owns that change and the redeploy.

