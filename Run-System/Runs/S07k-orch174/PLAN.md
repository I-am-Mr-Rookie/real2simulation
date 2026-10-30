# S07k-orch174 PLAN — pre-registered v2 fall-window rule (committed BEFORE the v2 script exists or runs)

Lane CLAUDE, anthropic/claude-opus-5-5/high (OpenCodex-managed, not polled). Issued 2026-10-30T23:50:31Z,
cutoff 00:15:31Z, deadline 00:20:31Z. Owns: evidence/S07/S07k/, Run-System/Runs/S07k-orch174/.

Objective: a SECOND analysis (v2) of owner clips with a window rule taken only from SAM track signals,
motivated by the S07h v1 failure modes (impact inside window, rotation, colour release with moving scale
frames, short window, SAM loss). Never chosen by g vs 9.79.

Inputs: evidence/S07/S07g/track-own01.json, evidence/S07/S07i/track-own02..06.json. OWN07-OWN11 track files
contain 0 frames at start (CUDA OOM, S07j re-tracking) -> PENDING, not measured. OWN12 excluded.

## v2 rule (fixed; d_k = y_k - y_{k-1} in px on SAM mask-centroid y, consecutive frame indices only)
1. Release R = first tracked frame k with d_k > MOVE_PX = 4 px (2 x declared 2 px detection std) AND d_{k+1} > 4 px
   (sustained descent). No colour threshold, no fall-windows.json.
2. Scale frames = up to 5 contiguous tracked frames ending at R-2 (strictly before release; R-1 excluded since release
   may happen between R-1 and R). Need >= 3 frames, all with boxes, and y range <= STATIC_PX = 6 px (3 x 2 px); else ABSTAIN.
3. Fall window starts at R. It ends at the frame BEFORE the first frame k > R where any holds:
   (a) SAM box width differs from the scale-frame mean width by > WIDTH_TOL = 10 % (rotation/impact; width only,
       because vertical motion blur inflates height); (b) d_k < 0.5 * d_{k-1} (velocity halves = impact/deceleration);
   (c) frame gap or SAM loss (end of contiguous tracked run).
4. N_MIN = 8 fall frames, else ABSTAIN (gives >= 3 held-out frames).
5. Unchanged from S07h/S07i: split train = first floor(2n/3) frames; held-out PASS iff RMSE <= 6 px; frozen S07i
   constants/fit/uncertainty (imported, asserted unchanged), mask_centroid result with |centroid - box| model term,
   coverage vs 9.79 at 1u/2u (comparison only).

Implementation: evidence/S07/S07k/measure_v2.py imports S07i measure_own01 (record/run/assume) and S07h helpers,
temporarily swaps m.window/m.SCALE_FRAMES/m.TRACK (S07h pattern); --self-check on synthetic frames only.
Commit script before its first real run; exactly one run; no edits after results except text.

Forking-paths disclosure: the author read the S07h failure modes and saw the OWN02 y-trace while drafting this rule;
v2 is a second analysis on the same clips, labelled as such, and is not independent confirmation.

Checks: python evidence/S07/S07k/measure_v2.py --self-check; one real run; python -B -m unittest discover -s tests/measurement -t tests/measurement.
