# Route composition boundary (S04b shell)

Reserve route groups `(public)` for landing/library/sign-in and `(private)` for
workspace. Route groups do not change the URL and are not security boundaries.
Authorize server-side before mounting private content. Public layouts must not
unconditionally require Clerk. Default export/layout conventions are chosen in
S04b uses Next.js 16.4.3 App Router with JavaScript server components.

The root supplies semantic navigation, skip link and local CSS. Public landing
and empty library have no Clerk dependency. Private layout denies with notFound
until server identity/ownership enforcement exists; never add a data fetch in a
child based on the layout guard alone (Next may render children concurrently).
S04c/d must guard every data operation. Unknown routes return a generic 404.
Sign-in and scene-specific public library playback are not connected yet.

Use shell README's `viewer`, `workspace`, `job-status` slots and injected adapters.
Do not implement/copy viewer or workspace modules here. Library fixture mapping
is `../shell/fixture-mounts.json`; fixture inclusion never fakes upload success.
