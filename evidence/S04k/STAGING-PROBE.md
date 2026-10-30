# S04k staged-context probe (local only, no deploy)

Commit afbdae4. `python -B infra/railway/dev/stage.py web %TEMP%/s04k-stage-03cac8bb` -> 106 files incl.
`Build/library/loader.mjs` and `Build/web/library-snapshot/guest.json` (sha256 630cda22...a2035, in context-manifest.json).
Built inside staged `Build/web` (same layout as new web.Dockerfile WORKDIR /app/Build/web; node_modules junctioned
from main checkout, removed afterwards): `npm run build` exit 0, routes /api/library/manifest + /artifacts/[id] present.

`next start` with NODE_ENV=production, R2S_PYTHON=C:/no-python-here.exe (python spawn impossible), 127.0.0.1:8093:
- GET /api/library/manifest -> 200, cache-control no-cache, ETag "9d8d77a6...0688", 18 demos (2 SIMULATED playable,
  simulated-mystery-g SIMULATED metadata-only, rest UNAVAILABLE); body has no `true_g`.
- GET /api/library/artifacts/13e00f7f...1608 -> 200, immutable, ETag = sha, 16858 bytes.
- unknown 64-hex id -> 404; `..%2Fx` -> 400; /library page -> 200.
- Snapshot file removed + restart: manifest 503 library_unavailable, artifact 503 (fail closed, no python fallback in production).
Server stopped (port 8093 no listeners); snapshot restored. Docker itself was NOT built (no docker run here).
