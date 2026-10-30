# S14g-fix3-orch64 PLAN
Objective: finish R-A F3/F4: Gate A over 10 distinct recorded approved-clip scenes (+30 Spark turns), persisted re-auditable.
Owns: Build/agent/; contracts/agent/; tests/agent/; evidence/S14/; Run-System/Runs/S14g-fix3-orch64/.
Window (controller reissue): issued 04:58:49Z, cutoff 05:23:49Z, deadline 05:28:49Z (original 04:31:37Z window superseded; thread started late).
Steps: reuse S14g_fix_gate_a (oracle/turn/summary/live_post) + S13c keyframes + S13e clip_context/build -> offline (stub plumbing) -> live (record) -> offline replay of recorded.
