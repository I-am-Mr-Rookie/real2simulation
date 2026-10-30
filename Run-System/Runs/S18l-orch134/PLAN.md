# S18l-orch134 PLAN
Objective: fix R-L P2 - Mystery-g library entry must not claim answer secrecy recoverable from public trace/repo.
Owns: Build/library/ (mystery_g.py, validate.py, loader.mjs, README.md), test-data/library-artifacts/mystery-g.json,
tests/library/ (test_mystery_g.py, loader.test.mjs), evidence/S18/S18l-*, Run-System/Runs/S18l-orch134/.
Approach: inspect /lab (read-only); /lab draws server-owned hidden g -> library entry = Earth-g practice shape, blind in /lab; enforce label in validator.
Checks: python -B -m unittest discover -s tests/library -t tests/library; node --test tests/web-library/library.test.mjs (non-owned regression).
