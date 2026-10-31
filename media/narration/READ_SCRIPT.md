# Voice-over read sheet

Source: [DEMO_SCRIPT_DRAFT.md](../script/DEMO_SCRIPT_DRAFT.md) (v5, final VO wording, punctuation only changed). Target total 3:00 including on-screen-only gaps. Pace about 2.5 words per second.

## How to record

- Quiet room, phone voice recorder or PC mic. Mic 15 cm from mouth, same spot every take.
- One take per segment, from click to click. Full sentence or short phrase, exactly the words in the table.
- Leave 1 s of silence before and after each take.
- Re-record any segment: save it again under the same file name (overwrites).
- Any format: m4a, wav or mp3. Keep the segment id as the file name, e.g. b01-01.m4a.
- Drop files into `media/narration/takes/` (local only, gitignored).
- Say numbers exactly as written. "g" is the letter g. "Real to Simulation" is the product name.
- Do not add words like "validated", "accurate" or "matches g".

## Beat 1: Hook: measure, don't guess (window 12 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b01-01 | Real to Simulation measures physics from real video. | PD02 clip, SAM 3.1 track dot over the bob (default: track plot only, no raw frames). Caption: Real video → measured track → simulation → honest error | 3.2 (8 w) | b01-01.m4a |
| b01-02 | And it tells you exactly what it could not measure. | (same shot) | 4 (10 w) | b01-02.m4a |

Beat spoken 7.2 s of 12 s window. Running total (windows): 12 s (0:12).

## Beat 2: Measurement: tracking (window 22 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b02-01 | Meta's SAM three point one segments and tracks the object in every frame on a Modal GPU. | PD02 full swing with per-frame mask/track overlay, small A10G tag. Caption: SAM 3.1 · 439/439 frames tracked · Modal A10G | 6.8 (17 w) | b02-01.m4a |

Beat spoken 6.8 s of 22 s window. Running total (windows): 34 s (0:34).

## Beat 3: Reconstruction + gravity direction (window 14 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b03-01 | MapAnything finds the floor. | RM02 classroom to MapAnything point cloud, floor plane, badge scale: ABSTAINED. Caption: Metric scale: ABSTAINED (unverified) | 1.6 (4 w) | b03-01.m4a |
| b03-02 | When metric scale can't be sourced, the system abstains. | (same shot) | 3.6 (9 w) | b03-02.m4a |

Beat spoken 5.2 s of 14 s window. Running total (windows): 48 s (0:48).

## Beat 4: Fit with uncertainty (window 25 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b04-01 | A deterministic fitter, not a language model, fits the fall and reports its uncertainty. | ST03 apple drop; fitter panel with track points, fitted parabola, 1σ band. Caption: Image-space g fit, precision not accuracy | 5.6 (14 w) | b04-01.m4a |
| b04-02 | It's image-space only. The clip is probably slow motion, so this is not g in metres per second squared. | (same shot) | 7.6 (19 w) | b04-02.m4a |

Beat spoken 13.2 s of 25 s window. Running total (windows): 73 s (1:13).

## Beat 5: Predict, then check (window 25 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b05-01 | We seal a prediction before seeing the rest of the clip. | ST03: sealed prediction drawn before suffix reveal, suffix overlaid, error meter. Caption: Gate RS: NOT_MET, diagnostic only, 7/466 frames scored | 4.4 (11 w) | b05-01.m4a |
| b05-02 | Today it misses. The full tracking job ran out of GPU memory, and the ballistic fit has no floor. | (same shot) | 7.6 (19 w) | b05-02.m4a |
| b05-03 | The apple lands. The prediction keeps falling. | (same shot) | 2.8 (7 w) | b05-03.m4a |

Beat spoken 14.8 s of 25 s window. Running total (windows): 98 s (1:38).

## Beat 5b: System measures fall time and drop height (no stopwatch) (window 20 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b05b-01 | The system finds release and impact in the phone clip, with the scale you declare. | OWN07 face-free snippet (owner approved): SAM track, release/impact markers, parabola, then S07n table row OWN07; then OWN01 hero row with ABSTAIN, lower bounds, fit 10.96 ± 0.77 failing its own check. Caption: SYSTEM-ESTIMATED, MEASURED (conditional), scale user-declared, phone clock unverified, approximate, not calibrated | 6 (15 w) | b05b-01.m4a |
| b05b-02 | Fall time, zero point four three three plus or minus zero point zero two seven seconds. | (same shot) | 6.4 (16 w) | b05b-02.m4a |
| b05b-03 | Height, zero point nine two three plus or minus zero point zero one zero metres. | (same shot) | 6 (15 w) | b05b-03.m4a |
| b05b-04 | g, nine point eight four plus or minus one point two four metres per second squared. | (same shot) | 6.4 (16 w) | b05b-04.m4a |
| b05b-05 | Hero take: the track ends before impact, so lower bounds only. | (same shot) | 4.4 (11 w) | b05b-05.m4a |
| b05b-06 | Approximate, not calibrated. | (same shot) | 1.2 (3 w) | b05b-06.m4a |

Beat spoken 30.4 s of 20 s window OVER. Running total (windows): 118 s (1:58).

## Beat 6: Muse interview, numbers from tools (window 25 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b06-01 | Muse Spark interviews you about the setup, but every number it shows comes from a tool. | Workspace chat: Muse asks setup questions, number chips tagged tool. Caption: Gate A: MET_AMENDED_Q16, scale unverified, not setup-validated | 6.4 (16 w) | b06-01.m4a |
| b06-02 | Our checker flagged zero invented numbers across thirty replayed turns, on recorded scenes, not validated setups. | (same shot) | 6.4 (16 w) | b06-02.m4a |

Beat spoken 12.8 s of 25 s window. Running total (windows): 143 s (2:23).

## Beat 7: Virtual lab + library (window 16 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b07-01 | The library holds simulated experiments, clearly labelled. | /library card tagged SIMULATED; Mystery-g practice card; cut to /lab blind round; sidebar search result. Caption: SIMULATED library traces, Mystery-g practice is not the blind /lab | 2.8 (7 w) | b07-01.m4a |
| b07-02 | The Mystery-g card is practice at Earth g. | (same shot) | 3.2 (8 w) | b07-02.m4a |
| b07-03 | The lab draws a hidden g each session for a real blind test. | (same shot) | 5.2 (13 w) | b07-03.m4a |

Beat spoken 11.2 s of 16 s window. Running total (windows): 159 s (2:39).

## Beat 8: Cost + honest misses (window 11 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b08-01 | Modal bill so far: under a dollar. | Static checklist card. Caption: Modal billed to date $0.599594 · Gate M ✗ · Gate RS ✗ · scale unverified | 2.8 (7 w) | b08-01.m4a |
| b08-02 | Not proven: no calibrated metric source, so no physical-accuracy claim. | (same shot) | 4 (10 w) | b08-02.m4a |

Beat spoken 6.8 s of 11 s window. Running total (windows): 170 s (2:50).

## Beat 9: Close (window 10 s)

| Segment | Say | On screen | Target s | File |
|---|---|---|---|---|
| b09-01 | Every number you saw is a pointer into the repo's benchmark. | Judging URL + repo + BENCHMARK.md. Caption: Built Oct 27 – Nov 4 · every number links to BENCHMARK.md | 4.4 (11 w) | b09-01.m4a |
| b09-02 | Try it. | (same shot) | 0.8 (2 w) | b09-02.m4a |

Beat spoken 5.2 s of 10 s window. Running total (windows): 180 s (3:00).

Total 180 s = 3:00.

## Timing note

Spoken total about 113 s of 180 s; the rest is on-screen-only gaps. Beat 5b spoken (30.4 s, numbers read out in full) exceeds its 20 s window by about 10 s. At edit time lengthen the 5b window to about 31 s and take 10 s from the gaps in beat 2 (15 s slack) and beat 4/6; total stays 3:00. If still tight, drop b05b-05 and b05b-06 only after keeping the "approximate, not calibrated" caption on screen.
