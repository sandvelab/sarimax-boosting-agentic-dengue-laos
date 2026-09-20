#!/usr/bin/env python3
"""Stage 1 alone vs. this candidate's two-stage ensemble: mean CRPS and interval coverage.

Same comparison logic as the sibling candidates' `02_compare_to_stage1.py`, against this
node's own `per_cell_scores.csv`. Plan Sec.2: "A model that wins on mean CRPS while being
badly calibrated has not won. Report interval coverage beside CRPS, for both stages, on both
datasets." Also reads the two prior candidates' own `comparison.json` (their closed records,
not recomputed) to report all three stage-2 candidates side by side -- this is the file-grounded
basis batch 7's main-path decision will use, so it is produced here rather than left implicit.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from scipy.stats import norm

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/c_bayesianRidge
STAGE2_NODE = NODE.parents[0]  # analysis/04_stage2
ANALYSIS = NODE.parents[1]
STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
OWN_CELLS_CSV = NODE / "results" / "per_cell_scores.csv"
A_COMPARISON = STAGE2_NODE / "a_linearLags" / "results" / "comparison.json"
B_COMPARISON = STAGE2_NODE / "b_gradientBoosting" / "results" / "comparison.json"
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
        "earns_its_place": bool(delta < 0),
    }
    (RESULTS / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Side-by-side of all three stage-2 candidates built so far, from each one's own closed
    # record (never recomputed from a sibling's raw cells -- AGENTS.md Sec.1, each node's
    # result is that node's own file).
    a = json.loads(A_COMPARISON.read_text())
    b = json.loads(B_COMPARISON.read_text())
    side_by_side = {
        "stage1_alone_mean_crps": stage1_crps,
        "a_linearLags": {
            "mean_crps": a["two_stage_ensemble"]["mean_crps"],
            "pct_change_vs_stage1": a["pct_change_vs_stage1"],
            "coverage_empirical": a["two_stage_ensemble"]["coverage_empirical"],
        },
        "b_gradientBoosting": {
            "mean_crps": b["two_stage_ensemble"]["mean_crps"],
            "pct_change_vs_stage1": b["pct_change_vs_stage1"],
            "coverage_empirical": b["two_stage_ensemble"]["coverage_empirical"],
        },
        "c_bayesianRidge": {
            "mean_crps": two_stage_crps,
            "pct_change_vs_stage1": pct,
            "coverage_empirical": summary["two_stage_ensemble"]["coverage_empirical"],
        },
        "any_candidate_earns_its_place": bool(
            a["earns_its_place"] or b["earns_its_place"] or summary["earns_its_place"]
        ),
    }
    (RESULTS / "all_candidates_comparison.json").write_text(json.dumps(side_by_side, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(json.dumps(side_by_side, indent=2))


if __name__ == "__main__":
    main()
