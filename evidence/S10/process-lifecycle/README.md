# Windows process-tree lifecycle evidence

This tests the **actual unchanged** `Build/lab/session-service.mjs` from source
`7708494fed8ae1b3cc23b943b5168e910b58fb9d`, SHA256
`6638dd0f88a0b60af0c9d1c32f969abfe461a2a7da138e33130e4e4dc1c0bacc`.
It is **controlled synthetic bridge lifecycle evidence**, not actual simulation,
physical Gate M, real-scene inference, deployment, or universal platform proof.

## Reproduce (Windows, Node and Python already installed)

```powershell
node --test --test-reporter=tap tests/lab/process-tree.test.mjs
node --test --test-reporter=tap tests/lab/process-tree.test.mjs tests/lab/session-service.test.mjs
```

Run from the checkout root. Non-Windows skips the new OS-specific test.
No dependency installation, server, network, .env, credentials or paid compute.

## Mechanism / safety

- The parent test creates its own validated temporary directory and copies the
  readable authored fixtures there. A separate Node harness changes only its own
  cwd and imports the absolute actual service. Its existing `localRoot()` finds
  that temporary `Build/lab/session-bridge.py`; no production source is copied,
  rewritten, patched, or mocked.
- Python stdlib starts a real idle Node grandchild and records both PIDs. Node
  atomically publishes readiness including its own PID, parent PID and unique
  fixture token. Bounded polling waits on those records, not an arbitrary sleep.
- Before abort, CIM confirms executable paths, exact fixture command lines,
  parent links and process creation timestamps; `process.kill(pid, 0)` confirms
  both exact PIDs alive. The real service receives AbortSignal and selects its
  Windows `taskkill /PID <bridge> /T /F` path. No spawn/close/abort mocks.
- Four real trees fill all slots; a fifth request fails generically and creates
  no tree. Abort/reap one, then a real replacement successfully occupies its
  released slot. Abort all remaining trees. All five requests fail generically,
  both PIDs in every tree die within the 10-second assertion bound, sessions
  stay empty, and active bridges return to zero.
- Fallback cleanup is **after**, not before, OS-death assertions. It queries each
  exact recorded PID again, verifies ownership and creation time when captured,
  and may use `taskkill /PID <exact-owned-PID> /F` without `/T`. Successful runs
  required **zero fallback kills**. Only the validated, non-symlink test temp
  directory is recursively removed. No shared server or unrelated process stops.
- All readiness/settlement/death checks, CIM/taskkill commands and subprocess
  lifetimes are bounded. Fixture Python/Node also self-limit to 60 seconds.

## Saved results

| Evidence | Result |
|---|---|
| `run-1.log` | Initial harness assertion failed because actual Windows command line mixed `Build/lab` slash styles; fixture identity comparison corrected. Not a product failure. Owned tree was aborted and cleaned. |
| `run-2.log` | New standalone OS test PASS; five real trees; zero fallback cleanup. |
| `combined-tests.tap` | **33/33 PASS, zero skipped/cancelled**: new OS test + all 32 existing service tests, run together to check isolation. |
| `final-run.json` | Readable JSON diagnostic extracted from combined TAP (TAP doubles backslashes; decoded once), preserving source hash, actual identities, events and timing. |
| `verification.txt` | Fresh source/scope/process/temp verification and authored-file hashes. |

Final combined run Python bridge PIDs: **12496, 1820, 8268, 4320, 9976**.
Corresponding Node grandchildren: **6432, 22848, 6760, 10440, 28352**.
Observed abort-to-both-dead times: **303–2447 ms**; bound **10000 ms**.
All ten exact PIDs absent in a separate final CIM query; owned temp removed.
Node v24.18.0; Python 3.14.5; Windows `win32`.

## Limits / corrections

An initial evidence-extraction command did not account for TAP backslash escaping
and PowerShell's nonterminating errors; its optimistic console line was invalid
evidence. Re-extracted with `$ErrorActionPreference='Stop'`, decoded TAP escaping,
validated PASS/five trees, and reran the exact-PID CIM check successfully. The
corrected structured evidence and verification file are authoritative.

No ETW/process-audit instrumentation was added: kill method comes from the exact
unmodified service source path, with real descendant death observed. This does
not prove arbitrary detached/reparented descendants, unavailable taskkill/CIM,
timeout killing, every Windows version or non-Windows behavior. Existing mocked
tests were not duplicated or relabeled as OS proof. No actual production bridge
simulation success is claimed by the new fixture.
