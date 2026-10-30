# S15q root cause (reproduced, offline)
- Web sent `{"answers": [{"questionId","chipId","text"}, ...]}` (interviewAnswers() array, verbatim) — Build/web/src/workspace/controller.mjs submitAnswers.
- API analysis.spec requires `answers` to be an object -> 422 INVALID_INPUT "body must be {answers: {...}}" (`answers: expected object`).
- Proof: tests/api-workspace/test_jobs.py::test_web_spec_body_rm04_200_and_old_array_body_422 posts the OLD array body over a ready RM04 recorded job (jobs.scene_resolver, real analysis router) -> 422; and the NEW body -> 200, label 'scale unverified, not setup-validated', drop_height 1.5.
- The NEW body is produced by the real reducers + controller + PrivateWorkspace.routeAction over the real RM04 questions (tests/workspace/spec-body.test.mjs) and pinned in tests/workspace/fixtures/rm04-spec-body.json, which the Python test reads:
  `{"answers": {"drop_height": {"text": "1.5"}, "initial_vertical_velocity": {"chip": "at-rest"}}}`
- Fix side: web (API validation unchanged).
- Silent stall cause: view.mjs showed `view.error ?? jobStatus.error`, so the viewer LOAD_FAILED masked the spec error; the stage panel never rendered it.

