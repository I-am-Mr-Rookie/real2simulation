# S14g-fix6-orch100 PLAN
Objective: close R-A RECHECK-fix5 F1-R3 (label-adjacent citation launders an invented amount).
Approach: drop the bare label-chain binding (`<units>: <q>`) in contracts/agent/validate.py and independently in
evidence/S14/S14g_fix_oracle.py. A unit word binds only directly after a cited quantity or inside an amount-free
`in <units>` phrase (optionally then `:`/`=` and a cited quantity). Amount words break the chain -> refuse -> fallback.
Owns: Build/agent/ (not record_muse.py); contracts/agent/; tests/agent/ (not test_muse.py); evidence/S14/;
Run-System/Runs/S14g-fix6-orch100/. Offline, $0.
Checks: agent+pipeline unittests; reviewer probe read-only; offline replay of 30 saved turns, honest fallback count.
