# RP01 — partial trajectories exist; metric clock/plane not recovered

## Contract check

QUEUE S07a requires candidate scale/timebase uncertainty; S07/S07c in the approved
plan fits tracked positions, not necessarily release-to-impact endpoints. The
earlier127s crop losing the floor is **not sufficient grounds to reject a fitted
partial-flight track**. This audit finds a real partial track and corrects that
overstrict inference. No product/queue changes made here.

For an endpoint method, however, the applicable height and start/stop physical
events really must be paired with that timer reading. A stopped timer elsewhere
in the montage cannot calibrate the timestamps of an unrelated partial segment.
No fit, tracking, g estimate or Earth-g-derived video speed was attempted.

## Coverage and exact evidence

Full film overview from S02f (0–600s,15s sampling) was inspected read-only.
Own overview covers60–570s every5s. Practical sections90–300 and300–555s have
1fps overview sheets;90–180 and180–285 have2fps sheets from480p. These overview
sheets are discovery only: fps sampling is not proof that a short event is absent.
The native-* labelled sheets and mapping-*.json use actual source PTS checked
against the complete15361-frame timestamp list; indices are zero-based.

| Apparatus | Exact reviewed delivered window / useful finding |
|---|---|
| Stopwatch fall | n3175–3224,127.004–128.964s, all frames. Conservative clearly falling subset **n3189–3193,127.564–127.724s**. Ball reaches lower crop atn3194. Same-shot ruler; strong blur. Do not reject merely for missing release/floor. |
| G-ball first shown release | n5110–5134,204.404–205.364s. Close-to-wide edit precedes release~204.7; hand follows/occludes ball. |
| G-ball possible offscreen trial |211–217s, every3rd frame. Raises/arms, then cut to Christina; no certified visible trajectory. Not another benchmark. |
| G-ball next release | n5525–5549,221.004–221.964s; release~221.2, hand overlap. Prior close/wide change not spliced into a track. |
| G-ball close release | n5755–5779,230.204–231.164s; release~230.4–230.5, very short visible fall then crop exit. |
| G-ball last reviewed release | n5865–5889,234.604–235.564s; release~234.8, cut at235.044. |
| Light-gate setup |323–326s every2nd frame. Held ball/placement, not certified ballistic motion. |
| Light-gate drop-like view |352–355s every2nd frame; movement353.8–354 then close/wide cut at354.084. Ruler is on desk, not a calibrated shared trajectory plane. |
| Light-gate manual demonstration |371–374s every2nd frame: fingers visibly retain ball as it crosses gate. Not free flight. |
| Electronic timer |420–535s every25th frame: sphere handling438–441 and456–458; trapdoor/base switch448–455; separately cut stopped stopwatch469–473. No certified paired dimension/endpoints/clock. Tiny-ball trial inventory not exhaustively frame-annotated. |

The four g-ball release episodes above are distinguishable handling/reset events,
not four independent camera sources. Hidden releases, alternate angles and
montage cuts are not extra certified trials. No replay identity/unique-take
analysis proves that all edited views are independent; use one capture family.
**Zero metric-qualified independent trials; exact complete trial count unknown.**

## Scale, geometry and timebase

- Producer identifies the bracket's **metre rule**, independently of gravity.
  Full480p witness ruler-230.204-full480p.png resolves numbered graduations and
  bracket; fall-127.644-full480p.png shows the ball/ruler offset and blur.
  This is a legitimate scale lead, not an assumed standard ball diameter.
- Rule face and moving ball centre are offset in image/depth; a single side-ish
  camera angle does not prove coplanarity, frontoparallel geometry or constant
  depth. Perspective/metric scale error is **unbounded here**, not assigned an
  invented percentage. Different camera angles require separate calibration.
  No pixels-per-metre value or uncertainty is certified.
- Delivered file:854×480,25fps, first videoPTS0.004s, last614.404s;15360
  consecutive intervals exactly0.040s. This is **presentation mapping only**.
  Source camera cadence, dropped/duplicated acquisition frames, retiming and
  exposure/shutter mapping remain unknown. No source declaration was identified
  in the producer/Commons reads. Ordinary-speed dialogue is not clock proof.
- G-ball's source-stated0.01s resolution is not absolute accuracy, and is not
  video capture fps. Its start is release-switch actuation; stop is floor contact.
  None of these inspected cropped falls has a demonstrated matching height,
  impact and readable event-associated display. Its moving LCD was not recovered.
- The separately edited electronic stopwatch is a stopped elapsed-time display,
  not a visible continuously advancing per-frame timecode. Timer/base/upper sphere
  are not shown with a readable independent vertical dimension and certified
  start/stop endpoints for one trial. Do not substitute plumb bob/string length,
  gate size, ball size, table height or assumed Earth-g into missing calibration.
- No explicit slow-motion label recovered in RP01 sections; **unknown retiming
  is not proof that it is slow motion**, and absence of a label is not proof of
  real time. Cuts are visibly present; never track across them as continuous.

## Determination and stop

The127.564–127.724s segment is a better partial-track lead than S02f's floor-loss
summary suggested, but no useful segment currently combines certified metric
projection and physical-time mapping. **Do not promote RP01 to S07a/Gate M.**
Higher480p resolved ruler/hand context; another larger download cannot by itself
supply acquisition provenance. No1080p download, broad hunt, tracker/fitter/GPU,
creator message or new approval request. RP03 and FF01/02 were not investigated.

This run is **PARTIAL for exhaustive exact-trial inventory**, not simply because
qualification is negative. Native-frame annotation of the entire electronic
section and all short events was not completed within the bounded continuation.
Controller may accept the demonstrated current clock/plane HOLD without further
downloads; reopening needs an explicit bounded question, not a generic hunt.
