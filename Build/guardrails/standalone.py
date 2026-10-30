"""Local-only standalone Modal admission; never import this inside a remote function."""
import os
from pathlib import Path
from uuid import uuid4

from Build.guardrails.admission import ReconstructionPaused
from Build.guardrails.reservations import repository_root, reserve_gpu

ROOT = Path(__file__).resolve().parents[2]


def admit_standalone(operation):
    """Require a reviewed all-in bound; share pipeline's two-job/$1 envelope, not a new allocation."""
    amount = os.environ.get("S20_MODAL_RESERVATION_USD")
    if amount is None:
        raise ReconstructionPaused("S20_MODAL_RESERVATION_USD all-in bound required")
    root = repository_root(ROOT)
    reserve_gpu(root, root / "evidence/S20/runtime/standalone-gpu-ledger.jsonl",
                "reconstruct", operation + ":" + uuid4().hex, amount, max_jobs=2, cap_usd="1")
