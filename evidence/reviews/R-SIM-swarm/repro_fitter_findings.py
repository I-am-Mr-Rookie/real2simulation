"""Minimal read-only repros for the S11 fitter review.

Run from the review worktree with the peer fitter root as the first argument:
    python repro_fitter_findings.py "C:/.../swarm-s11-fitter/..."
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
sys.path.insert(0, str(root))
from Build.fitter import FitError, fit_least_squares, select_model  # noqa: E402


def main():
    # P1: overflow in the QR projection escapes the public FitError boundary.
    try:
        fit_least_squares(
            (1e308, 1e308 - 1e292, 1e308 - 2e292), (1.0, 2.0, 3.0), 2
        )
    except FitError:
        print("P1 fixed: FitError")
    except Exception as exc:
        print(f"P1 present: {type(exc).__name__}: {exc}")
    else:
        print("P1 absent: unexpectedly accepted")

    # P2: a non-zero residual is reported as exact because _aic uses an
    # absolute machine-epsilon threshold rather than rss == 0.
    t = tuple(i / 10 for i in range(8))
    y = tuple(1 + 2 * x + 3 * x * x + 1e-15 * ((-1) ** i) for i, x in enumerate(t))
    fit = select_model(t, y).candidates[1]
    print(f"P2 rss={fit.rss!r}; quadratic_aic={select_model(t, y).aic[1]!r}")


if __name__ == "__main__":
    main()
