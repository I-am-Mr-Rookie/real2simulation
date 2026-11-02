# N61 in-app-browser DEV recheck

## Method and boundaries

- Koushik attached the browser after the initial local-only run. All final checks below used the ChatGPT in-app browser, not an external browser or automation script.
- DEV: https://real2simulation.up.railway.app. Controller reported web deployment 5ad1fa2f at main f7cf60ae and a passing verify.py. This worker independently verified the rendered behavior, not Railway control-plane state.
- Rebased run/N61-orch306 onto main. No application code changed during this follow-up.
- Final checks used the existing N46/N57/N60 QA fixture, at 1366 x 900 and 375 x 850. Only its existing sample/result/snapshot data was used. Quota displayed 0 of 20 uploads left.
- Navigation, clicks, menu choices, scrolling, slider keyboard seeking, resizing, and visual screenshots were done through the in-app browser. Read-only DOM/CDP inspection supported the visible observations and source identity, without injecting app state or network mutations.
- The placeholder login failed once; the controller supplied the exact existing test identity, which signed in successfully. This cost less than five minutes. No new account was created.
- No paid call, upload, tracking/reconstruction job, agent turn, microphone action, purchase, account-settings change, deployment, or deletion. Existing private owner projects, the prohibited room and N06 were not opened.
- Screenshots listed below are local and uncommitted, complying with the worker contract's no-media-binaries commit boundary.

## Results

| N60 finding | 1366 px desktop | 375 px phone |
|---|---|---|
| F01 | CONFIRMED: sample menu has Open and Open experiment. Open navigates to the classroom room editor; Open experiment shows the apple result, whose replay link opens the measured track. | CONFIRMED: separate experiment action is usable; clicking the sample card opens the classroom room editor, not the apple result. |
| F02 | CONFIRMED: both the N60 Saved lab card and Open menu open its project editor. | CONFIRMED: both the card and Open menu open the same project editor, not the agent drawer. |
| F03 | CONFIRMED: recorded trace seek index 4 displays the full value, unit, time and MEASURED label with wrapping, not ellipsis. | CONFIRMED: same readout remains visible and wraps compactly; the uncertainty and scale/playback caveats remain visible below it. |
| F04 | CONFIRMED: ST03 card shows its decoded source video and matching frame-pixel track. | CONFIRMED: the same video and track remain visible in the phone card. |

### F01 steps and evidence

1. In Projects, open Project actions for classroom room and falling apple.
2. Open navigates to /lab?editor=1&room=e704985d4073435fb816941a6ab12e82; the actual editor loads the classroom reconstruction with MODEL-ESTIMATED geometry and scale-unverified labels.
3. Return to the workspace and choose Open experiment. Recent activity shows SAMPLE (RECORDED): falling apple, its MEASURED result with uncertainty, and the 3D replay, redo with changes link.
4. That link opens /lab?editor=1&experiment=be1e91a551a046c5a73436e45b069aa0.
5. Repeat the menu choice and room-card click at 375 px. Both destinations remain reachable.
6. Screenshots: fixture-sample-menu-1366.jpg, fixture-room-open-1366.jpg, fixture-sample-menu-375.jpg, fixture-room-open-375.jpg.

### F02 steps and evidence

1. Click the existing N60 QA snapshot-only lab card, marked Saved lab.
2. Confirm /lab?editor=1&project=17f7acaaed9945aab6b782b3c93c91cc and the loaded editor.
3. Return and use Project actions > Open. It opens the same project editor.
4. Repeat the card and menu paths at the other viewport width.
5. Screenshots: fixture-saved-open-1366.jpg, fixture-saved-open-375.jpg. This confirms navigation, not project-scene persistence/isolation semantics.

### F03 steps and evidence

1. Open the existing recorded apple replay through the F01 experiment path. Do not start another measurement.
2. Focus Recorded trace, press Home, then ArrowRight four times.
3. Slider index 4 displays: Tracked object reading (px): -49.500 at t = 0.17 s. MEASURED.
4. Desktop caption: display block, white-space normal, 35.8125 px height, client/scroll width both 251 px.
5. Phone caption: display block, white-space normal, 27.5 px height, client/scroll width both 263 px, left 10 and right 272.828125 within the 375 px viewport.
6. The recorded fit remains 2330 +/- 110 px/s^2 with 1 sigma, scale-unverified and playback-clock caveats. These are existing fitter/API outputs, not a physical metric-accuracy claim.
7. Screenshots: fixture-recorded-1366.jpg, fixture-recorded-375.jpg.

### F04 steps and evidence

1. Inspect Experiment: ST03-trim.mp4 in Projects at both widths.
2. Its rendered video src is /api/workspace/files/42fcf3760e5742efa729285887bbbe13/content#t=0.5.
3. At both widths, the video has readyState 4, natural width 720 and no media error. The matching SVG viewBox is 0 0 720 1366, labelled MEASURED: hosted SAM 3.1 box centres in image pixels.
4. Read-only inspection of the page's already-observed 200 files/experiments responses confirms that exact file has project_id null, while experiment 2cbda1fbacce400bbe77cd3395156657 references it from project d32a8c7c10674e7ea9e1efae4be28058. No unrelated video was substituted.
5. Screenshots: fixture-st03-preview-1366.jpg, fixture-st03-preview-375.jpg.
6. Missing-source/nonmatching-video negative cases remain covered by the prior regression tests, not destructive manipulation of DEV data.

## New problems and limits

- No new reproducible finding within the requested four UI paths.
- Initially some saved/sample thumbnails showed their fallback icons. On subsequent ordinary navigation, their snapshot requests returned 200; the N60 image decoded at natural width 375. Not enough evidence for a new ranked defect, consistent with N60's earlier transient observation.
- No claim about new uploads, paid inference, calibration, physical accuracy, or broader application behavior. No source tests/build were rerun because this follow-up changed evidence only.

## Supplemental work before the reissued test-account-only window

- Confirmed F03 on the current local production build using a new SIMULATED ball trace at both widths; screenshots readout-1366.jpg and readout-375.jpg.
- Before the reissued instruction, the browser initially held the owner's session. Only its public sample and a newly created, clearly named QA lab were opened, not existing private owner projects.
- The new QA project, N61 UI snapshot-only lab, id c46d33ba096a4dd6b0a786d69b6eda3e, was created/renamed through the UI, then received one simulated canvas snapshot (PUT 200). It remains retained, not deleted. No existing owner recording was opened and no saved backend scene was edited.
- All final F01 to F04 confirmations above were repeated in the required existing QA fixture, so none depend on this supplemental session.
- The temporary loopback Next server was stopped, and the browser viewport override reset.
