# Identity boundary (planned S04c/d)

- Server verifies Clerk session and derives user ID. Never trust client audience,
  scene access fields, owner IDs or an unverified JWT. Clerk shared Google + email
  OTP only; no custom OAuth client/secret in browser bundles.
- Public `/library` and its explicit allowlisted artifacts require no sign-in.
  Guests cannot list/read private scenes, get private jobs, upload or mutate data.
- Missing Clerk configuration: library stays available; private routes and
  mutations fail closed with explicit auth-unavailable state. Never convert a
  missing/malformed session into a demo-user identity.
- Server authorizes ownership for each private scene, job and asset resolution.
  Signed asset transport, if later used, must be narrowly scoped and short-lived;
  never put credentials or storage-root URLs in a scene manifest or public DTO.
- Authenticated writes need same-origin/CSRF protections and rate limits at the
  server boundary; sign-in alone is not upload approval or spend authorization.
- HTTP boundary: 401 unauthenticated, 403 authenticated forbidden; private IDs may
  use uniform 404 to avoid enumeration. Errors must not leak tokens or existence.

S04c implements SDK/provider/sign-in/sign-up configuration wiring only; see README.md.
S04d adds a server-only resource guard backed by a tested ownership policy.
S04i connects it to a read-only per-user development fixture repository and the
standard Clerk session-context proxy, matched only to `/workspace/:path*`.
Each leaf authorizes before reading its client DTO; the layout is composition,
not an access boundary. Missing sessions/configuration, nonowners, unknown IDs,
repository failures and non-development environments uniformly deny with 404.
The fixture is an empty scene container, not reconstructed geometry or a live
workflow. S15k/S22 still need real signed-in browser/deployment verification.
Shell DTO contract: `../shell/integration.schema.json` and `../shell/README.md`.
