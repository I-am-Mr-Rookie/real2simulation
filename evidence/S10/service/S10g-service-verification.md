# S10g service verification

- Branch: `run/S10g-service`, rebased onto `f409018d27d777f2516660fc0e8951f7a8b33dce`.
- Scope: local synthetic service only; no deployment, browser claim, physical calibration, private setup exposure or public upload.
- Vertical slice: `POST /api/lab` loopback `start(free_fall|projectile, mystery)` -> bounded Python bridge -> S08 `regression_case`/validated export -> Node RK4 observations; ballistic `fit` -> actual `Build.fitter.api.handle` -> trusted Mystery-g handoff/reveal.
- Redaction: Mystery-g start contains observations/hash/units/limitations only; gravity appears only after fit. Normal start may carry explicitly labelled synthetic setup gravity.
- Safety: UUID sessions, 10-minute TTL, 64-entry bound, 4-child concurrency bound, 30-second child timeout, 1 MB request/response bound, finite/shape/sample allowlists, loopback-only non-production route, whitelisted child environment, ignored stderr and clean public errors.
- Fresh checks: Node service/route tests `4/4 PASS`; Python bridge tests `3/3 PASS`; `node --check` for service and route; `git diff --check` PASS.
- Limitation: this is synthetic evidence only. The Node module warning for the standalone route import is expected because the existing web package does not declare a module type; no package/dependency change was made.
