# N03-orch251 DONE (branch run/N03-orch251)
- New Build/api/storage/files.py: SQLite (stdlib) files + projects tables, bytes under R2S_DATA_DIR (default ~/.r2s-data; store created lazily so app start/liveness never touch disk).
- Routes (require_owner, API prefix /internal/workspace, web path /api/workspace/...): POST /files (multipart 'file', optional 'project_id'), GET /files (+quota), GET /files/{id}, GET /files/{id}/content (FileResponse, Range -> 206), DELETE /files/{id}; POST/GET /projects, GET /projects/{id} (+files).
- Limits: mp4/mov/webm/jpg/png by extension + magic bytes; <= 200 MB (413 FILE_TOO_LARGE); video <= 120 s via ffprobe when installed (422 VIDEO_TOO_LONG), else size only; 1 GB/user (413 QUOTA_STORAGE); 20 uploads/user/Dhaka day (429 QUOTA_UPLOADS, checked before body read). Errors carry detail.quota (used/remaining/limits, uploads_reset_at UTC). Delete frees storage, does not refund the daily count (row soft-deleted, file unlinked).
- app.py: import + one include_router line (mounted before the Redis branch).
- BFF route.js: POST /files streamed (duplex half, cap 201 MB) instead of 1 MB buffered; forwards range; passes content-length/content-range/accept-ranges/content-disposition back; responses streamed; DELETE export.
## Checks
- tests/api-storage/test_storage.py: 8/8 OK (auth, user isolation, type checks, 200 MB edge, 1 GB edge + delete frees, 20/day + Dhaka midnight reset, projects, real ffprobe 1 s / 121 s / garbage).
- tests/api-storage/proxy_files.test.mjs 3/3; tests/web-workspace-api/proxy.test.mjs 5/5 (existing behaviour unchanged).
- Build/api/health tests + tests/api-workspace/test_jobs.py: 37/38; 1 pre-existing error (local psycopg not installed).
- evidence/N03/loopback_check.py: real uvicorn + Node streamed multipart 5 MB -> 201, Range -> 206 with correct tail (loopback_check.out.txt).
- Build/web npm run build: OK.
## Paid calls: none.
## Needs controller (outside Owns)
- Add python-multipart==0.0.20 to Build/api/health/requirements.txt, else DEV uploads return 500 (app still starts; Starlette imports it lazily).
- Set R2S_DATA_DIR to the volume (N11). If ffprobe is absent on Railway, duration is not enforced (size only).
## Skipped / risks
- No DEV deploy or browser check. Railway edge body limit for 200 MB uploads unverified. Quota lock is per process (one uvicorn worker is safe; multiple workers could race the quota check). No project delete/rename.
