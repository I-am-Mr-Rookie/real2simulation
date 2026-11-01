# N16 Guess the Gravity: DONE
- Build/api/experiment/share.py: owner POST/DELETE /internal/workspace/experiments/{id}/share; public GET /public/guess/{token}, POST .../reveal. Mounted in Build/api/health/app.py (one line).
- Share row (guess_shares, N03 SQLite) stores only trajectory, quantity+label, motion. No file id, video, user id. Token_urlsafe(24), revocable, idempotent while active. Only measured m/s^2 results (known size given) are shareable.
- Public view withholds the answer; reveal validates guess (0..1000) and returns value, uncertainty, label, difference.
- Public BFF: Build/web/src/app/api/guess/ (token regex, only /public/guess paths, no auth headers, 1 KB body cap). Page: (public)/guess/[token] titled "Guess the Gravity", SVG replay of points, no video.
- Checks: pytest test_share.py 2 pass, test_live_experiment.py 8 pass; node --test guess.test.mjs 3 pass; npm run build OK (guess routes listed).
- Paid calls: none.
- Integration note for N21 (live-view.mjs): button POSTs /api/workspace/experiments/<id>/share, shows location.origin + response.path, DELETE same URL to revoke.
- Skipped: no browser run on DEV, no deploy, no rate limit on public reads/reveal, no view counts. Public routes bypass Clerk (proxy matcher excludes /guess and /api/guess).
- Risks: reveal can be brute-forced by a token holder (answer is shareable anyway); jitter added in test fixture because noiseless fits give -inf AIC that JSON cannot store (real tracks unaffected; worth a guard in N07 _set).
