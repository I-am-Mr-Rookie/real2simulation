# S14a-orch14 plan

Objective: define agent scene-context, question and tool-output contracts plus a
structured response schema whose text cannot carry numbers; every number is a
reference to a validated fitter/simulator tool output labelled measured/simulated.

Owns: Build/agent/; contracts/agent/; tests/agent/; evidence/S14/; Run-System/Runs/S14a-orch14/.
Reuse: contracts/fit/quantity.validate_quantity (S11 quantity), contracts/experiment parse_json
(strict JSON), contracts/scene validate (bundle gate), Build/fitter/api.handle + Build/instruments
synthetic observations for the end-to-end fixture. No live LLM calls/spend. Fixture-only; no gate claim.

Checks: python -m unittest discover -s tests/agent -t . -v ; rejection tests for untraced numbers.
