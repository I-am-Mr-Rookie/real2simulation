# S18b free-fall display catalogue

- Output: `test-data/library-artifacts/free-fall.json`, **metadata-only**.
- Four SIMULATED S10hi-gate cases: baseline-short, upward-launch, tiny-height,
  low-gravity-long-horizon. Original accepted acceptance JSON is copied exactly
  once into the digest-addressed store; each entry selects its actual case.
- One RM02 S06d reconstruction descriptor, with original approved source/licence/
  attribution/acquisition hash and successful job custody. It is not a measured
  free-fall fit and is not the origin of the synthetic metrics.
- Gate M: **NOT_MET_INPUT_READINESS**; scale **SCALE_UNVERIFIED**.
  Actual S07f receipt independently reports zero eligible/measured trials and
  physical evaluation NOT_RUN. No metric-eligible real free-fall demo exists here.

## Fresh verification

`library-tests.txt`: 28 tests pass, including all 16 S18a tests and 12 new
free-fall tests. `validation.txt`: 5 local-only demos validate.
`example-regression.txt`: unchanged S18a example generation still succeeds.
`custody.json`: exact current checkout hashes for accepted reports/outputs,
approval, acquisition registry, clip metadata, gate/scale evidence and catalogue.

No new physics output, raw media, GPU/API calls, spend, dependency installation,
routes, deployment or publication. Browser playback and independent gate review
are not tested or claimed. A valid manifest is not scientific validation.
Controller must review source acceptance and integrate this isolated run.
