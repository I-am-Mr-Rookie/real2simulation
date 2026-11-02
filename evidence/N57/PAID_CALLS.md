# N57 paid-job ledger

| UTC requested | Job | Model/provider | Units reported by API | USD reported by API |
|---|---|---|---|---|
| 2026-11-02T11:24:28Z | Measurement `0ac7c8592779473daa5e939057824940`, public `ST03-trim.mp4`, target apple, no asserted metric scale | SAM 3.1 / hosted Meta Model API | 120 video frames | 0.024 |

One job, no retry. Admission checked the code rate USD 0.0002/frame and the default 3600-frame reserve of USD 0.72, below the USD 1 allowance; actual probe length was 120 frames. Result completed successfully. No Modal, room reconstruction, shell, SF3D or agent inference call was requested by this run.

Receipts: `receipts.json` entries `paid-job-admission`, `real-job-progress-files`, `paid-job-result`. This is the QA ledger; the server's global ledger was not separately read or modified.
