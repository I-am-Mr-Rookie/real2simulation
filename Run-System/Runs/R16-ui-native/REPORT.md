# R16-ui-native REPORT — DONE
- Lane/model: native Claude, anthropic/claude-opus-5-5 medium inside Codex (not ClaudeCode). Tokens/cost: unknown (unobservable). Coding quota: OpenCodex-managed; not polled.
- UTC start 2026-10-29T08:08:43Z (worker clock 08:08:53Z); end 2026-10-29T08:11:11Z. Branch run/R16-ui-native from fe79f61 (base 9eece42; oracle a79e135 read via git show, not rewritten).
- Scope: ONLY Build/web/src/lab/fit-contract.mjs diff. No product/tests/oracle/control edits.

## Verdict: no P0-P2 findings.

Evidence:
1. Uncertainty metadata: real producer (Build/fitter/api.py:121) emits exact string `standard uncertainty (one sigma), not a 95% interval`; session-service.mjs:92 forwards it as body.fit → accepted. Minimal DTO without the key accepted (compat kept). Present-but-different/null/undefined/''/trailing-space → null. Matches static UI text LabClient.jsx:100.
2. Sparse assumptions: hole → null; hole check exits at first hole, so `length=2^32-1` sparse rejects in <100ms (no loop DoS). Non-string → null. JSON input cannot be sparse, so no legit producer loss.
3. Plot span: finite-span branch byte-identical arithmetic to base (ordinary 0/0.1/0.3 points exact vs base formula). Overflow branch only when span is Infinity; halves are finite and difference ≤ MAX_VALUE → [-MAX,0,MAX] gives exact 24/320/616 and 190/110/30. Subnormal [-MIN,0,MIN] exact (uses unhalved branch). Degenerate single point & ±0 → centre 320,110. All outputs finite and within [24,616]×[30,190].
4. Large arrays: loop min/max replaces spread; 300000 rows → full domain, N points, no truncation/RangeError.
- Commands: `node Run-System/Runs/R16-ui-native/independent-check.mjs` → ALL 42 checks pass (independent-check.txt). `node --test` temp copy of a79e135 oracle + ui-helper-recovery + ui-contract + r14-ui-invariants → 59/59 pass (targeted-tests.txt); temp copy deleted, worktree clean.

## P3 / compat notes (non-blocking)
- `'quantity_uncertainty' in uncertainty` also sees prototype-chain props (polluted Object.prototype → rejects): fail-closed, acceptable.
- Only quantity_uncertainty is cross-checked; other producer fields (covariance.interval, residual dof) not validated by the reveal — outside this diff.
- Object.hasOwn is ES2022 runtime API (Chrome 93+/Safari 15.4+); fine for Next default targets, not polyfill-verified here.
- Overflow branch: halving loses 1 ulp for odd subnormal values only when span overflows — invisible at that scale.

## Ponytail (full/default) applied
- Reuse: existing exported helpers + frozen oracle run via git show/temp copy, no new harness or deps; one ~45-line check script.
- Smallest change: review-only; zero product edits. Skipped: full suite/IAB/build (parent owns), prior-gate audit, privacy/security, physical Gate M/S12/GPU/deploy.
- Risk: browser rendering not exercised here (parent IAB375).
- Communication: silent; no messages sent; one final line.

