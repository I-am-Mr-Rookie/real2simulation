"""Local-only standalone Modal admission; never import this inside a remote function."""
import os
from pathlib import Path
from uuid import uuid4

from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.reservations import repository_root, reserve_gpu, claim_gpu

ROOT = Path(__file__).resolve().parents[2]
# Reviewed standalone envelope (evidence/S07/S07j/ENVELOPE-2.md). Envelope 1 = standalone-gpu-ledger.jsonl,
# 2 jobs/$1, exhausted by S07i (rows kept, never released). reserve_gpu also counts EVERY unsettled Modal
# journal row against max_jobs/cap_usd, so envelope 2 is cumulative: 3 jobs/$1.50 with the old $1.00 still
# counted admits exactly one new job <= $0.50. A further envelope needs a new review, not an edit here.
LEDGER, MAX_JOBS, CAP_USD = "evidence/S20/runtime/standalone-gpu-ledger-2.jsonl", 3, "1.50"


def admit_standalone(operation):
    """Require a reviewed all-in bound; admit within the reviewed envelope above, never a release."""
    request_id = os.environ.get("S20_MODAL_REQUEST_ID")
    if request_id is not None:
        return claim_gpu(ROOT, request_id, operation)
    amount = os.environ.get("S20_MODAL_RESERVATION_USD")
    if amount is None:
        raise ReconstructionPaused("S20_MODAL_RESERVATION_USD all-in bound required")
    root = repository_root(ROOT)
    stage = "segment" if operation.startswith("modal-track:") else "reconstruct"
    request_id = reserve_gpu(root, root / LEDGER, stage, operation + ":" + uuid4().hex, amount,
                             max_jobs=MAX_JOBS, cap_usd=CAP_USD)
    return claim_gpu(root, request_id, operation)
