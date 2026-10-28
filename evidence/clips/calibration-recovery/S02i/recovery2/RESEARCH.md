# RP01 electronic inventory — bounded audit complete; metric HOLD unchanged

## What changed

The previously vague electronic-section entry now has an [exact event ledger](inventory.json): upper apparatus handling, manual base/button demonstrations, an isolated timer insert, two held-bearing gestures and the final hand demonstration. Nested detail entries are **not extra trials**. All listed windows were visually inspected through the contact sheets and native apparatus crops; mappings contain exact delivered frame/PTS pairs.

- E01: native n10925–11049. Upper placement and withdrawal; neither hand descent nor motion blur certifies a free ball.
- E02: every fifth frame n11200–11370. Hands operate the flap and button. The brass object on yellow thread is the plumb-line weight, not a falling bearing.
- E03: native n11375–11499. A cut at n11392 (455.684s) changes the view from controls to raised hand. Full-resolution witnesses show why a moving hand alone cannot certify release.
- E04: native n11495–11674, also re-extracted as native-pixel apparatus crops. Pointing and control manipulation are not a separated ball track. Cut at n11666 (466.644s); do not bridge it. Enlarged sheets use nearest-neighbour duplication only, not enhancement/interpolation of motion.
- E05: every fifth frame n11700–11845. Readable-looking LCD is an **edited insert**, not demonstrated continuously advancing acquisition timecode. No numerical elapsed-time transcription is used for qualification.
- E06a/b: native n12560–12599 and n12810–12849. On both downward movements the bearing remains between fingers. These are clear **handled-ball false positives**, not two free-fall benchmarks.
- E07a: native n13125–13164. Lowering a closed/pinched hand does not expose a separated ballistic trajectory; the earlier upper-hand interval is partly cropped.

Coverage: prior five 1-fps sheets cover 420.004–534.004s; fresh targeted maps cover the windows above, including 550 native-cadence frame references (five overlapping references retained). These are delivered image counts, not physical elapsed-time measurements. Other intervals remain overview-only. This is a useful episode inventory, **not proof that no subsecond/offscreen event exists between all overview samples**, nor an exhaustive frame annotation of the whole film. Exact physical trial count remains unknown. Zero certified metric-independent trials, not a claim of zero real falls ever performed.

## Independent calibration evidence and exact missing facts

Producer notes identify a metre-rule bracket for the g-ball and a plumb line for vertical alignment in the electronic apparatus. Neither statement establishes the camera projection or ball/ruler coplanarity. No acquisition-camera timing declaration was found on that page; its absent-camera search is only a bounded negative, not proof none exists anywhere. [NUSTEM apparatus notes](https://nustem.uk/activity/measuring-g/)

The linked institutional procedure measures the ball-bottom-to-flap distance and warns about parallax. It describes apparatus timing, **not RP01 camera calibration**, and cannot supply an unrecorded film height or capture fps. [IOP electronic-timer procedure, within the collection](https://spark.iop.org/collections/acceleration-due-gravity)

The file page establishes attribution/licence and delivered-media provenance, not an independently certified acquisition-to-presentation timing chain. [Commons file record](https://commons.wikimedia.org/wiki/File:A-level_Physics_Core_Practical-_Finding_a_value_for_g_using_a_free_fall_method.webm)

Still required for a metric partial-track fit:

1. Independently supported physical elapsed time per retained image over the chosen continuous shot, including any edit/retiming/frame-drop mapping and its uncertainty. Uniform delivered 0.040s PTS gaps alone do not provide it.
2. A metric reference at the ball's depth/trajectory plane, or sufficient camera/depth geometry to bound projection error, with readable reference endpoints and uncertainty for that shot. Apparatus verticality does not solve this.
3. Resolvable ball centres over a continuous free-flight subset. The retained prior n3189–3193 lead remains valid in principle with free initial velocity/intercept; missing floor contact is **not** a blanket veto. We did not redo that track.

All three calibration uncertainties remain unknown/null, not invented percentages. Never infer clock scale by matching Earth g; never transfer a ruler or timer calibration across montage cuts. No tracker/fitter/GPU or Gate M run occurred.

## Provenance / reproduction

Reuse the retained original S02i 480p derivative read-only; [source.json](source.json) records its exact path, bytes and SHA256. `extract.py` imports the already tracked parent S02i helper, redirects **only its output BASE** here, verifies source identity and the existing full PTS receipt, and checks ffmpeg showinfo mappings. `crop_apparatus.py` cross-checks its 180 raw crop PTS against the original extraction. `verify.py` checks the committed ledger, source, mappings, sheet files and raw receipts.

Example (run in this checkout; substitute the retained evidence path, not a new download):

```powershell
python evidence/clips/calibration-recovery/S02i/recovery2/extract.py '<prior-S02i-evidence>' 437 5
python evidence/clips/calibration-recovery/S02i/recovery2/crop_apparatus.py
python evidence/clips/calibration-recovery/S02i/recovery2/verify.py
```

No raw video copied; intermediate PNGs/logs ignored under media/. Sheets are local evidence, not a public upload or approval. Existing [S02i attribution](../ATTRIBUTION.md) applies: NUSTEM, CC BY 3.0; extracts cropped/tiled/labelled here, no audio, no endorsement. [Licence](https://creativecommons.org/licenses/by/3.0/)

Bounded external review: producer and Commons reopened; exact-title/fps and producer/director/camera searches yielded no shot-specific timing receipt. Unrelated results were not treated as evidence. IOP's producer-linked electronic-timer link resolves to the broader collection; only its relevant electronic subsection was used. No contact, new media acquisition or broader source hunt.
