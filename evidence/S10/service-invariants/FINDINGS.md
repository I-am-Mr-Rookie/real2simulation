# R14 exact-source service boundary audit

Audited baseline: `74c886f`; no product edits. These are **two latent P3 transport robustness gaps**, not demonstrated failures of the current Python producer, a remote exploit, a privacy conclusion, or a physical/product-gate result.

## F1 — chunk-dependent UTF-8 decoding

- Source: `Build/lab/session-service.mjs`, bridge stdout handler: `out += b` converts each Buffer independently to UTF-8 text.
- Minimal input: valid controlled start reply with `limitations: ['synthetic µs timing']`; split the serialized UTF-8 Buffer after the first byte of `µ` (`C2 | B5`).
- Independent expected oracle: valid UTF-8 JSON must decode identically for every partition of the same byte stream, including a partition inside a character. Expected limitation is unchanged `synthetic µs timing`.
- Actual baseline: successful session with `synthetic ��s timing`. Both chunks independently introduce U+FFFD replacements; original bytes are unrecoverable.
- Frozen regression: test `UTF-8 bridge response decoding is independent of stream chunk boundaries`.

## F2 — response ceiling counts UTF-16 code units rather than bytes

- Same source: stdout accumulation checks `out.length > MAX_BODY`, including the final close check; `MAX_BODY = 1_000_000`.
- Input: controlled valid reply with `limitations: ['€'.repeat(340000)]`. UTF-8 serialized bytes exceed 1,000,000, while decoded JavaScript string length is below 1,000,000.
- Expected oracle: bounded bridge response must reject a byte stream larger than its one-million-byte resource ceiling, irrespective of Unicode characters. HTTP ingress correctly implements the byte-based interpretation.
- Actual baseline: `status: 'ok'`; session inserted. This is specifically an output byte-bound gap, not a bypass of the correct HTTP request byte bound.
- Frozen regression: test `bridge response cap rejects more than one million UTF-8 bytes, not just code units`.
- Contract caveat: the source names `MAX_BODY` but does not explicitly document its unit. If the parent intentionally defines an output **code-unit** limit instead, F2 is a byte-bound hardening recommendation rather than a violated published limit. The test deliberately preserves the stricter independent byte-limit oracle; do not silently weaken it to fit existing code.

## Reachability and severity limit

The fixed local Python producer currently serializes with `json.dumps(..., allow_nan=False, separators=(",", ":"))`, leaving default `ensure_ascii=True`. Therefore actual non-ASCII fields are emitted as ASCII escapes, masking both examples. No arbitrary remote bridge producer is exposed by these tests. The observations are finite numeric fields, so this finding does not demonstrate changed fitted physics. Severity is **P3 defensive robustness**, not P0/P1/P2 or a current release blocker on this evidence alone.

Small shared-root repair for parent consideration: retain bounded bytes and decode once after close, or use a stateful UTF-8 decoder with an independent raw-byte counter. No fix is authored here.

## Communication

Immediate nonterminal finding posted in worker commentary. Explicitly authorized parent callback attempted against parent thread `01a1840d-7310-7991-8cb8-8ec4cfb149a7`; app tool returned `MCP tool codex_app/send_message_to_thread is not available to the model`. No delivery claimed; no config/tool-mode/provider change attempted. Disk evidence and final report pointer are the handoff.
