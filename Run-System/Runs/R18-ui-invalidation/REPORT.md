# R18 — DONE (actual UI verification supplement only)

Actual IAB375 normal-mode reset was observed during both pending Run and pending Fit, followed by clean successor trials. **No product change, queue completion or seventh round.**89/217 and six rounds remain. Exact Build/contracts diff against reviewedfe79f61 empty; base67fd702 is docs-only after accepted3f43e4b.

## Fresh actual UI evidence

1. Free-fall Run showed disabled Running / Generating simulated observations. First pending observation was not immediately reset and is not counted as a successful cancellation. A second natural Run was observed pending, then Projectile selected immediately in the same browser call: UI cleared observations/reveal, enabledRun, disabledFit, resetmessage. No request/producer delay or mocks.
2. Successor Projectile real Run returned Projectile samples, not old Free-fall samples or stale error. Fit was invoked; the actual Fitting state was observed and Ramp selected immediately in the same call. UI cleared old plot/reveal, disabledFit for Ramp, resetmessage.
3. Successor Ramp Run completed with Ramp samples after the old fit's normal completion window. Actual reveal-heading count0; no stale ballistic fit/error committed. Final innerWidth375/client360/scroll360. This is a bounded observed UI sequence, not universal race proof or evidence that a CPU process was killed.

All phase AX states/order and finalDOMmeasurements: `evidence/S10/ui-invalidation/iab-375.json`; derived check summary `observation-summary.json`. Screenshots `reset-pending-375.png` (selectedProjectile and cleared currenttrial) and `successor-ramp-375.png` (context/selectedRamp) were visually inspected. No fabricated numerical output/response injection. Browser tabclosed andviewportreset. Owned dev14936 stopped byCtrlC; fresh3101socketprobe closed. Natural dev access logs included200 responses even for abandoned UI work; these logs alone do not establish server cancellation either way.

## Boundary / timing / preservation

The separateR17-normal-http worker owns actual NextHTTP/CPU child-abort proof. Its current observations do not yet prove cancellation; an exit0 after attemptedabort must not be renamed successful cancellation. Do not conflate passing UI stale-result protection with process termination. Previous controlledprocess/source tests remain their own narrower evidence, not a substitute.

Controllerissue08:25:04UTC, deadline08:55:04UTC/14:55:04Dhaka, minute25cutoff08:50:04; actual verification/ownedserverstop completed08:32:52UTC. First issue command had wrongwebcwd and failed beforemanifestcreation; corrected root issue, not backdated. No sourceimplementation or newClaude review needed because code/gate unchanged. No repeated passing physics/fitter/buildsuite.

Ponytailfull applied by reusing actual UI/server/currenthelpers and existing browserbindings, no code/dependency/wrapper/framework. Preserved raw timing uncertainty, distinct evidence layers and all safetyholds. Costs/tokens unknown, OpenCodexmanagednotpolled. No Mystery/private/auth audit, modelrouting/quota/provider/credential/policy change, physicalGateM/S12/real-scene/paidGPU/deploy/publish/account/terms actions. Goal remains active through10:00UTC/16:00Dhaka.

An old ignored `controller-controls.txt` receipt was inadvertently staged with an earlier whole-runfolder controladd. It is historical31-test output, NOT fresh evidence for this run. Removed only from current Gitindex; physicalfile retained unchanged/ignored, priorcommit recoverable. Subsequent adds use exact owned paths. Mandatory findings only; no optional duplicated chatlogs.
