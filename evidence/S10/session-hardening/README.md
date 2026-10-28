# R10 lab session hardening

All results are local/simulation-only. Controlled process events are not proof of OS process-tree death.

| Evidence | Command/result |
|---|---|
| `red.txt` | Before service edits: `node --test tests/lab/session-service.test.mjs`: 6 pass / 6 fail. Includes observed live-abort success race, pre-aborted cached fit, evicted fit success, abort-zero-close success, early stdin slot release and synchronous-spawn slot leak. |
| `red-hash.txt` | Before service edits: `node --test --test-name-pattern='during trusted\|during start hashing' tests/lab/session-service.test.mjs`: 4 fail; expiry/eviction/abort while hashing could still reveal, aborted start could insert. |
| `green.txt` | Intermediate expanded service check: 23/23 pass. |
| `targeted-final.txt` | Final source: `node --test tests/lab/session-service.test.mjs tests/lab/ui-contract.test.mjs tests/simulator/mystery-g.test.mjs tests/simulator/replay.test.mjs`: 34/34 pass (25 service). |
| `abort-stress.txt` | After owner relayed native-review cancellation finding: five fresh processes running `node --test --test-name-pattern='aborting an active bridge\|abort cannot become success\|abort during start hashing' tests/lab/session-service.test.mjs`: 15/15 pass. Existing actual-bridge abort test strengthened to require exact error envelope, aborted signal, no inserted session and zero retained slots. Includes deterministic exit-zero and post-close/hash cancellation. |
| `python-bridge.txt` | `python -m unittest discover -s tests/lab -p 'test_session_bridge.py' -v`: 4/4 pass, actual four-template bridge and S11 fitter. |
| `node-suite.txt` | Broader `node --test tests/simulator/*.test.mjs tests/lab/*.test.mjs`: 48 pass / 2 file-load failures, missing existing `@dimforge/rapier3d-compat` in this worktree. No install/manifest edits. Predates last two lifecycle tests. |

Node v24.18.0; Python 3.14.5. Existing module-type warning from route.js is unchanged; no manifest edits authorized. No browser, paid GPU, real-scene/physical calibration or native gate review performed by this worker. Parent must obtain native Claude review before acceptance.
