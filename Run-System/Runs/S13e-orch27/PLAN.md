# S13e-orch27 PLAN — Connect Muse Wonder understanding

Model: anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled). Start 2026-10-29T15:31:21Z, base main 7aff0fa.
Objective: `understand` stage worker over S13c keyframe manifest + S13d JobRunner key: try clip video once,
explicit keyframe-image fallback (capped/sampled frames), validate actual Muse reply with the S14 agent contract.
Owns: Build/pipeline/; contracts/jobs/; tests/pipeline/; Run-System/Runs/S13e-orch27/.
Reuse: Build/agent/muse (request, output_text, validator, ask_user), record_muse price constants, S13c extract, S13d StageError.
Checks: offline tests (fake post) for video ok / video fail->keyframes / cap / number rejection; <=6 live calls, <=$1, approved clip ST03 only, ledgered.
No Modal/GPU, no installs, no deploys, no canonical-control edits.
