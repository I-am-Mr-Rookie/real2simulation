# N15-orch263 REPORT
Status: DONE (stretch row N15: agent-proposed equation fitted safely)
Changed:
- Build/fitter/proposed.py: ast allowlist grammar compiled to closures (no eval): t, agent parameter names, numbers, pi, + - * / ^ (literal exponent |e|<=10), sin cos exp sqrt log; float-only math.pow; node/char/param caps. Pure-Python Levenberg-Marquardt (scaled normal equations, reuses core._invert), 1 sigma from s^2 (J^T J)^-1, AIC via core._aic vs built-in degree 1/2 (core.select_model).
- Build/api/agent/equation_handlers.py: fit_equation(trajectory_id, equation, parameters, initial_guess, axis x|y default y) on the stored track via live_experiment.analyse (no SAM call, no spend); keeps the track label/units; FitError -> BAD_EQUATION.
- Build/agent/core.py: appended fit_equation schema to TOOLS + its REQUIRED entry. Build/api/health/app.py: import + handler dict merge (2 lines, not 1: the import is needed).
- tests/fitter/test_proposed.py (24 tests): grammar rejects attribute access, __import__/abs/math.sin calls, t^1000, power towers, parameter exponents, subscripts, lambda, unknown/unused names; damped oscillation recovers A,g,w,p within 4 sigma; undefined/no-effect guesses error cleanly; schema + handler wiring with monkeypatched store.
- evidence/N15/damped_oscillation_fit.json: SIMULATED fixture fit (A 0.1200+/-0.0006, g 0.2981+/-0.0025, w 4.4004+/-0.0025, p 0.2002+/-0.0049; dAIC vs best built-in -1232).
Checks (uv --no-project with pytest, fastapi, httpx, jsonschema, python-multipart, python-dotenv, numpy; no pytest in system Python):
- tests/fitter: 89 passed. tests/agent: 74 passed. Build.api.health.app imports; TOOL_SPECS has fit_equation (9 tools).
- tests/fitter + tests/agent in one pytest call collide on test_core.py basename (pre-existing); run separately.
Paid calls: none. Optional live agent turn skipped.
Skipped: web UI rendering of fit_equation output; agent INSTRUCTIONS unchanged (tool description carries the grammar).
Risks: LM finds a local minimum, so bad initial guesses (e.g. wrong frequency) can converge to a poor fit; the AIC comparison exposes it. Sigma is the local linear estimate, scale/clock errors not propagated. Pendulum clips need axis=x.
