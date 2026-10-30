# S18l — Mystery-g library entry decision (fixes R-L P2)

Run S18l-orch134, anthropic/claude-opus-5-5 medium, base main `4e59880`.

## Finding (R-L-orch130 P2)
Library Mystery-g record = S10 acceptance `/cases/0` (Earth g, seed 42). Same g/seed/duration/dt as the
served projectile trace, Earth g is guessable, and acceptance/free-fall evidence is committed (public at
submission). So "answer withheld" was false for the library entry.

## /lab inspection (read-only)
- `Build/lab/session-bridge.py` `_start`: mystery -> `seed = secrets.randbits(32)`,
  `gravity = 4 + 12 * seed/2**32` (server-drawn hidden g per session, 4-16 m/s^2); kept in `private`.
- `Build/lab/session-service.mjs`: mystery sessions omit gravity from the start response and reveal via
  `createMysteryGSession(...).revealFit` only after the server-owned fit.
- => /lab already owns a real per-session hidden g. Decision: library entry points to /lab as the blind
  challenge; library setup is labelled shape-only / Earth-g practice / not a blind test.

## Change (smallest complete)
- `Build/library/validate.py`: `CHALLENGE_TITLE`, `CHALLENGE_LIMITATION`; challenge validation requires
  both and rejects "answer withheld"/"withheld from this artifact" in title/limitations.
- `Build/library/mystery_g.py`: uses those constants; replaces the false secrecy limitation with the
  Earth-g disclosure plus "blind challenge is /lab (server draws hidden g per session)".
- `Build/library/loader.mjs`: guest reason says practice shape, not blind; play blind in /lab.
- Regenerated `test-data/library-artifacts/mystery-g.json` (challenge object bytes/hash unchanged).
- Tests: new `test_s18l_honest_practice_label_enforced`; loader node test asserts the new reason.

Kept: `answer_visibility: "withheld-until-fit"` with `target: "/lab"` - it describes the /lab session answer
(true there); changing the token would break non-owned `tests/web-library`/`Build/web` for no secrecy gain.
No physics, other entries, guest answer fields or /lab code changed.

## Not done / follow-ups
- `Build/web/src/app/(public)/library/LibraryClient.jsx` line 35 ("answer is withheld until your own fit in the
  lab") is outside Owns; true for /lab, but should add "library setup is an Earth-g practice shape".
- `guest.py` free-fall trace withholding reason still says it "supplies the Mystery-g challenge answer"; harmless
  (trace stays withheld), not edited per task file list.
- Historical `evidence/S18/S18h-credits.json` snapshot keeps the old title.

