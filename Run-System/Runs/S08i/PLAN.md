# S08i — numeric guard repair

Solo direct authorization; CODEX-1 Sol/medium requested, runtime identity/effort
not independently exposed. OpenCodex-managed; not polled. Existing project/root.
Issued16:37:20Z, full deadline17:07:20Z=23:07:20BDT, minute25 cutoff17:02:20Z;
earlier owner/session stop16:58:00Z, no new implementation after16:53Z.
Verified DONE may finish early; incomplete requires recorded owner-stop exception.

Owns: contracts/experiment/validate_experiment.py and README.md;
Build/templates/free_fall.py; tests/spec/test_free_fall.py and test_setup_validation.py;
evidence/S08/numeric-guards/; this report/timebox; serialized canonical controls.
No new features, dependencies, environment changes, service/model/paid call.

Fix already-reproduced review P1/P2 at shared boundaries: reject signed giant
times before float conversion; reject requested fall/launch height whose stop
plane equals its origin in world coordinates. Both templates share this setup
path. Preserve numerical/geometry validation, provenance and input immutability.
Acceptance: red regression then smallest production edits, one-ULP controls for
two origins/both templates, full spec and scene/measurement regression, optimized
checks, source audit, verified FF and timing. Synthetic oracles NOT physics/gates.
Apply Ponytail full and TDD/verification skills already read in this session.
