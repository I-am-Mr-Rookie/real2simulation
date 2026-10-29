# S14b-orch16 PLAN

- Issued 2026-10-29T11:34:25Z; deadline 12:04:25Z; cutoff 11:59:25Z. Opus 5.5 high (OpenCodex-managed; not polled).
- Objective: Muse Wonder scene understanding adapter: synthetic scene_context -> Meta Model API (structured output) -> validated agent-response (scene_id, segments, candidates). Record sanitized live responses as fixtures; offline tests validate them and reject invalid / untraced-number responses.
- Owns: Build/agent/; contracts/agent/; tests/agent/; evidence/S14/; Run-System/Runs/S14b-orch16/.
- Budget: <=20 small Meta calls, conservative total <=$1, ledger per call in evidence/S14/S14b-ledger.md. Input only test-data/synthetic/scene/. Key by NAME only.
- Reuse: S14a scene_context, validate_response, response.schema.json, parse_json. No new deps if openai/httpx present.
- Checks: python -m unittest discover -s tests/agent; mutation that drops validation must fail tests.
- No Gate A claim; fixture validity is not real-scene evidence.
