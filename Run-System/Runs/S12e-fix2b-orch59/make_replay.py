from pathlib import Path
d = Path("Run-System/Runs/S12e-fix2b-orch59")
src = Path("evidence/reviews/R-RS/recheck/reproduce.py").read_text(encoding="utf-8")
a = src.index("# Commitment exists BEFORE")
z = src.index("\n\n", src.index('out["F2_nonpublic_synthetic_labeled_image_derived_gate"]')) + 2
new = src[:a] + (d / "f1r_f2r_block.py").read_text(encoding="utf-8") + "\n" + src[z:]
new = new.replace("parents[4]", "parents[3]").replace('read("evidence/S12/prediction-ST03.json")', 'read("evidence/S12/prediction-ST03-v2.json")')
new = new.replace("Run from worktree root: python -B evidence/reviews/R-RS/recheck/reproduce.py",
                  "Replay copy by S12e-fix2b-orch59 (defect probes inverted to refusals; reviewer file untouched).")
(d / "replay.py").write_text(new, encoding="utf-8")

