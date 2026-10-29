# S05b-orch13 — PARTIAL (two real L4 RM02 launches; no container admitted; all stopped)

Lane/model: anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). UTC 10:56:00 issue -> work stop ~11:17.
Branch run/S05b-orch13 from main 7303bc5, worktree `.worktrees/S05b-orch13`. Canonical controls untouched.

## What actually ran (Modal 1.6.3, uv-cached Python 3.11; MODAL_TOKEN_* key names only)
| Step | App | Result |
|---|---|---|
| Pre-check 11:00Z | - | `app list` [] / `container list` [] |
| CPU import preflight (cpu_import_probe.py, unchanged) | ap-jY2WvGtvkoq4Q9VGbqkSAw | **CPU_IMPORTS_OK** torch 2.8.0+cu128, vision 0.23.0, audio 2.8.0, NumPy 2.2.6, MapAnything 1.1.4; function 141.37s; stopped 11:02:41Z |
| Billing (in-app browser, read-only) 11:01Z & 11:09Z | - | Total spend $0.00; usage $0.01 all in credits, $0 charges; credits $129.99; limit $155 (Set by Modal) |
| GPU #1 L4, 4 hashed RM02 frames, admission 90s | ap-SwALWzKXg4Sxptguav9Jor | no container admitted -> client TimeoutError; stopped 11:06:03Z; exact-ID info stopped, containers [] |
| GPU #2 (controller-approved), admission 210s | ap-zZCFtM3w0bXRY08n6BjvhS | no container admitted -> TimeoutError; stopped 11:12:36Z; watchdog independent_stop_confirmed=true, resource_incident=false |
| Final 11:13:10Z | - | all 3 own apps stopped; own containers []; only other worker's s07b-orch13 container live |

No GPU type/VRAM/runtime/output measured (container never started). Controller decision: no third attempt;
record as **Modal L4 capacity/admission evidence** (same pattern as recovery5 Oct28: pending, no allocation). Cause
beyond "not admitted within bound" is not established. Gate R NOT RUN; S05c/physical holds unchanged.

Cost: reserve $0.95 (<= $1 cumulative, both attempts) in `evidence/S05/S05b/orch13/job-ledger.json`; total retained
$3.80 / $30. Actual: CPU job ~2.5 min (est. < $0.04); 0 GPU containers observed, so GPU billed time expected ~0 —
exact charge unknown until billing reconciles. No purchase/billing/limit change.

## Code changes (Owns: Build/reconstruction/spike/)
- `rm02_watchdog.py` + `modal_rm02.py`: phase receipt adds `ppid`; watchdog accepts Popen PID == pid or ppid.
  Root cause of attempt #1's false ResourceIncident: Windows uv/venv `Scripts/python.exe` is a launcher whose
  child is the interpreter (receipt pid 19068, Popen pid 29492). Token binding unchanged. Verified live in #2.
- `rm02_deadline.py` TOTAL 1200->900, EXECUTION 900->480 and `modal_rm02` function timeout 480: the only way the
  controller-approved retry (admission <=300s) fit the unchanged 11:26Z deadline; admission window = 210s.
  Stricter bound; may be too short for pip+4.9GB weights+inference — revisit before the next scheduled attempt.
- Tests: new trampoline test; deadline policy fixtures pin the original 1200/900 numbers; planned compute $0.255348.

## Fresh checks
- Spike suite normal **66/66 OK**, optimized (-O) **66/66 OK** (`evidence/S05/S05b/orch13/spike-tests*.txt`).
- `git diff --check` PASS. Frames: 4/4 SHA256 match input.json before copy into gitignored recovery5/local.
- Evidence: `evidence/S05/S05b/orch13/` (BILLING-PREFLIGHT.md, cpu-*, gpu*-runtime.txt, pre-attempt2/post/final-verify)
  and `evidence/S05/S05b/recovery8/attempt-a3cba62b.../`, `attempt-afb31566.../` (worker/watchdog/phase receipts).

## Ponytail full
Reused existing runner/watchdog/CPU probe/frames unchanged in design; one-token PID fix at the existing check;
constants changed in place, no new config/env knob/dependency. Skipped: GPU-type fallback list, third attempt,
scene-contract tests (untouched), new image/volume caching. Risks: 480s execution may cut a slow first run;
L4 admission on this account failed 3 times across 2 days — next try needs controller choice (other GPU type,
longer admission window in a longer session, or retry at another time).

## Communication
One nonterminal blocker message + one completion line to controller (authorized). Early finish under controller's
explicit "stop, no third attempt" decision after GPU #2; remaining window used for verification/evidence only.
