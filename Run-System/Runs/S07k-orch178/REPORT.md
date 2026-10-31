# S07k-orch178 REPORT — DONE

- Lane CLAUDE; anthropic/claude-opus-5-5 medium; OpenCodex-managed, not polled. UTC start 00:05:03Z, end 2026-10-31T00:07:32+00:00. Tokens/cost: unknown (not observable); $0 compute (no Modal/GPU/Meta).
- Base main cc644ac1; branch run/S07k-orch178; commits 42e736a0 (pre-registered mapping + asserts, before the real run) and the final commit.
- Files: evidence/S07/S07k/measure_v2.py (TRACKS/SCENES += OWN07–11 → S07j tracks; V2_FROZEN + OWN01–06 SHA asserts in run() and --self-check; table "pending S07h"), results.json (one real run, 11 clips), README.md (11-clip table, coverage, 05a–d, robustness, caveat); this PLAN/REPORT/TIMEBOX.
- Result (MEASURED, SECOND ANALYSIS v2): 6 measured / 5 ABSTAIN; 1u 4/6, 2u 5/6; **held-out pass 0/6**. New: OWN07 9.51 ± 0.93 (held 7.0 px FAIL), OWN08 8.82 ± 0.27 (z −3.54, held 17.8 FAIL), OWN09/10/11 ABSTAIN. 05a/c/d mean 9.32, SD 0.43 (05b flagged, abstain). v1 OWN07–11 pending S07h (orch176 not merged).
- Checks (fresh): `measure_v2.py --self-check` OK (OWN01–06 rows byte-identical to orch174, constants unchanged); `python -B -m unittest discover -s tests/measurement -t tests/measurement` 90 OK (1 skip); worker_timebox check below.
- Ponytail: reused orch174 script/rule and S07h/S07i imports unchanged; only a 3-line mapping extension + 2 asserts + 1 table cell; byte-identity via one SHA over existing rows instead of a fixture file. Skipped: any rule fix for the OWN09 SAM width outlier (forbidden post-hoc), viewing frames for OWN10/11.
- Risks/limits: OWN10/11 "track does not follow the fall" is inferred from centroid/width only; OWN09 abstain is a SAM glitch the frozen rule cannot reject; per-clip u under-states drop-to-drop spread (OWN08); forking-paths caveat retained. No canonical controls edited; not merged (controller acceptance).
- Communication: silent; one completion line to controller chat.
