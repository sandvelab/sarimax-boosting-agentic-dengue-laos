#!/usr/bin/env python3
"""Stage 1 alone vs. this candidate's two-stage ensemble: mean CRPS and interval coverage.

Plan Sec.2: "A model that wins on mean CRPS while being badly calibrated has not won. Report
interval coverage beside CRPS, for both stages, on both datasets." Coverage here is computed
at the nominal 90% level (two-sided Gaussian, z=1.6448536269514722 from `scipy.stats.norm`)
against each model's own (mean, se) on the matching cell set -- the same 371 cells 02_stage1
and 03_baselines were scored on, since this candidate's own verification step (in
`01_stage2_linear_lags.py`) already confirmed its re-derived stage-1 forecast matches
02_stage1's stored one.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from scipy.stats import norm

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/a_linearLags
ANALYSIS = NODE.parents[1]
STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
OWN_CELLS_CSV = NODE / "results" / "per_cell_scores.csv"
RESULTS = NODE / "results"

NOMINAL_COVERAGE = 0.90
Z = float(norm.ppf(0.5 + NOMINAL_COVERAGE / 2))


def read_scored(path: Path, mean_key: str, se_key: str) -> list[tuple[float, float, float]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        if r["fit_failed"] == "True" or r["actual"] in ("", None):
            continue
        out.append((float(r["actual"]), float(r[mean_key]), float(r[se_key])))
    return out


def crps_mean(cells: list[tuple[float, float, float]]) -> float:
    import sys
    sys.path.insert(0, str(ANALYSIS / "scripts"))
    from lib.crps import mean_crps  # noqa: E402
    return mean_crps(cells)


def coverage(cells: list[tuple[float, float, float]]) -> float:
    covered = sum(1 for y, mu, sigma in cells if mu - Z * sigma <= y <= mu + Z * sigma)
    return covered / len(cells)


def main() -> None:
    stage1 = read_scored(STAGE1_CELLS_CSV, "forecast_mean", "forecast_se")
    two_stage = read_scored(OWN_CELLS_CSV, "final_mean", "final_se")

    if len(stage1) != len(two_stage):
        raise RuntimeError(
            f"cell-set mismatch: stage 1 has {len(stage1)} scored cells, "
            f"this candidate has {len(two_stage)} -- not a comparable ablation"
        )

    stage1_crps = crps_mean(stage1)
    two_stage_crps = crps_mean(two_stage)
    delta = two_stage_crps - stage1_crps
    pct = 100 * delta / stage1_crps

    summary = {
        "n_cells": len(stage1),
        "stage1_alone": {
            "mean_crps": stage1_crps,
            "coverage_nominal": NOMINAL_COVERAGE,
            "coverage_empirical": coverage(stage1),
        },
        "two_stage_ensemble": {
            "mean_crps": two_stage_crps,
            "coverage_nominal": NOMINAL_COVERAGE,
            "coverage_empirical": coverage(two_stage),
        },
        "delta_crps": delta,
        "pct_change_vs_stage1": pct,
        "earns_its_place": delta < 0,
    }
    (RESULTS / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
