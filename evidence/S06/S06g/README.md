# S06g — CPU dry-run + disabled AWS adapter (fixture/gate evidence only)

- `image-spec-dryrun.json`: `python Build/gpu/image_spec.py` on this Windows PC (no GPU: nvidia-smi absent; torch and modal not installed). ok=true, errors=[], 96 pinned requirements. Validates pins only; no image build, no Modal call.
- `aws-adapter-receipt.json`: `python Build/gpu/aws_adapter.py`. Default (no env flag) refused; on-demand refused even with flag; no gate inputs refused with all six reasons. `launched` is always false: no launcher, no SDK import.
- `tests.txt`: `python -m unittest discover` in Build/gpu: 29 tests OK (7 new in test_aws_adapter.py).
- No AWS API calls were made (not even read-only). OWNER_GATES copies DECISIONS_LOG 2026-10-29 (owner-recorded spot quota 8 vCPU, "Real2Sim EC2 50 USD" budget, alerts 50/80/100% + forecast 100%); not re-verified live in this run.
- Not evidence of any GPU run, AWS launch, real scene or physical result.

