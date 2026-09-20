#!/usr/bin/env python3
"""Verify analysis/scripts/lib/crps.py's closed-form Gaussian CRPS two ways.

1. **Exact cross-check** against `properscoring.crps_gaussian`, an independent
   implementation of the same closed form, over a grid of (mu, sigma, y).
2. **Monte-Carlo convergence**: draw N samples from the same Gaussian, score them with
   `properscoring.crps_ensemble` (a general empirical estimator that assumes nothing about
   the distribution's shape), and check the empirical estimate converges to our closed form
   as N grows -- this is the check that does not simply compare two copies of one formula.

Writes results/verification.json; exits non-zero if either check fails its tolerance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import properscoring as ps

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[0] / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402
from lib.project_seed import component_seed  # noqa: E402

RESULTS = NODE / "results"
EXACT_TOL = 1e-10
# properscoring.crps_ensemble has no numba installed here, so it falls back to an O(n^2)
# pairwise-difference implementation (confirmed: ~3.5 GB / 4.5 s at n=10,000). Kept small
# enough to stay fast and memory-safe without adding a compiler-toolchain dependency for a
# one-off verification.
MC_SAMPLE_SIZES = [200, 1_000, 4_000]
# Tolerance as a fraction of sigma (Monte-Carlo error on CRPS scales with the distribution's
# spread, not just n) -- empirically, one draw at these sizes gave relative error up to 0.035
# at n=200 and 0.0094 at n=4000; these keep roughly 3x margin above that while still catching
# a real defect (a sign or factor error produces relative error of order 1, not 0.1).
MC_TOL_REL = {200: 0.12, 1_000: 0.08, 4_000: 0.04}

GRID = [
    (mu, sigma, y)
    for mu in (0.0, 5.0, 50.0)
    for sigma in (0.5, 1.0, 10.0)
    for y in (mu - 3 * sigma, mu - 0.3 * sigma, mu, mu + 0.7 * sigma, mu + 4 * sigma)
]


def exact_check() -> dict:
    rows = []
    worst = 0.0
    for mu, sigma, y in GRID:
        ours = float(crps_gaussian(y, mu, sigma))
        reference = float(ps.crps_gaussian(y, mu, sigma))
        diff = abs(ours - reference)
        worst = max(worst, diff)
        rows.append({"mu": mu, "sigma": sigma, "y": y, "ours": ours,
                     "properscoring": reference, "abs_diff": diff})
    return {"n_cases": len(rows), "max_abs_diff": worst, "tolerance": EXACT_TOL,
            "passed": bool(worst < EXACT_TOL), "rows": rows}


def monte_carlo_check(seed: int) -> dict:
    rng = np.random.default_rng(seed)
    cases = [(3.0, 2.0, 5.0), (50.0, 10.0, 30.0), (0.0, 1.0, 0.0)]
    rows = []
    all_passed = True
    for mu, sigma, y in cases:
        closed_form = crps_gaussian(y, mu, sigma)
        for n in MC_SAMPLE_SIZES:
            samples = rng.normal(mu, sigma, size=n)
            empirical = float(ps.crps_ensemble(y, samples))
            diff = abs(empirical - closed_form)
            rel_diff = float(diff / sigma)
            tol = MC_TOL_REL[n]
            passed = bool(rel_diff < tol)
            all_passed = all_passed and passed
            rows.append({"mu": mu, "sigma": sigma, "y": y, "n": n,
                         "closed_form": closed_form, "empirical": empirical,
                         "abs_diff": diff, "relative_diff": rel_diff,
                         "tolerance_relative": tol, "passed": passed})
    return {"seed": seed, "passed": all_passed, "rows": rows}


if __name__ == "__main__":
    seed = component_seed("00_metric-verify_crps")
    exact = exact_check()
    mc = monte_carlo_check(seed)
    result = {"exact_check": exact, "monte_carlo_check": mc,
              "overall_passed": exact["passed"] and mc["passed"]}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"exact check: max abs diff {exact['max_abs_diff']:.2e} "
          f"(tolerance {EXACT_TOL:.0e}) -- {'PASS' if exact['passed'] else 'FAIL'}")
    print(f"monte carlo check (seed {seed}): {'PASS' if mc['passed'] else 'FAIL'}")
    if not result["overall_passed"]:
        sys.exit(1)
