# S19d-dev-orch99 REPORT
Lane CLAUDE; anthropic/claude-sonnet-5-5/medium (OpenCodex-managed; not polled). Start 2026-10-30T06:56Z. Status: DONE. Branch run/S19d-dev-orch99.

## Result
- Dev web redeployed: deployment 61d3a805-cbda-4c33-bf30-e9d3da15a7c3 SUCCESS, source 6af57a0 (main 4969235 + 1 commit). Web service only; no new services/variables.
- Root cause fixed: stage.py allowlist and web.Dockerfile omitted Build/web/public and next.config.js, so PWA assets and the Service-Worker-Allowed header would be missing on Railway. Added both.
- Live (https://web-dev-cd80.up.railway.app): manifest 200 application/manifest+json; sw.js 200 with Service-Worker-Allowed "/"; icons 192/512/maskable 200; HTML has manifest link.
- In-app browser (not Chrome): SW activated at scope "/", cache r2s-static-v1, secure context; installability criteria met (HTTPS + manifest + 192/512 icons + SW).
- 375px: /, /library, /lab scrollWidth 375 = no horizontal scroll. Desktop 1280 fine. Dev/synthetic/no-uploads and illustration banners intact.
- /library on dev is honestly EMPTY ("No demos are published yet", "Viewer not connected"); no per-scene viewer route exists, so /lab (synthetic lab) served as third page. S18c pending.
- verify.py 10/10; infra/railway/dev tests 14 OK.
- Evidence: evidence/S19/s19d-dev-orch99.json; receipt in infra/railway/dev/deployments.json (IDs only).

## Ponytail
Reused existing stage.py/railway up procedure, verify.py, CDP in existing browser; smallest edit (allowlist + COPY); no new scripts or dependencies.

## Not done / risks
- No install prompt exercised, no real device, APK deferred. InstallGuidance still unmounted (outside Owns). /lab Run trial returns local_lab_disabled on Railway (known). Staging dir .tmp-s19d-ctx left untracked at event root. Dev only.
- Communication: silent; one final line to controller.
