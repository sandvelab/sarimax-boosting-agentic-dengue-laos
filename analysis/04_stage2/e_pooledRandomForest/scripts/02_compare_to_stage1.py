#!/usr/bin/env python3
"""Stage 1 alone vs. this candidate's two-stage ensemble: mean CRPS and interval coverage.

Same comparison logic as every sibling candidate's `02_compare_to_stage1.py`. Also reports
all five stage-2 candidates side by side, and isolates the one axis this candidate changes
relative to `d_linearClimate` (pooling across provinces vs. independent per-province fits, on
the identical input) since that is this candidate's actual question, not just "does it beat
stage 1 alone" -- plan §2 and 04_stage2/claim.md's fork log both hold pooling out as a
distinct kind of judgment call from a raw input feature.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from scipy.stats import norm

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/e_pooledRandomForest
STAGE2_NODE = NODE.parents[0]  # analysis/04_stage2
ANALYSIS = NODE.parents[1]
STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
OWN_CELLS_CSV = NODE / "results" / "per_cell_scores.csv"
A_COMPARISON = STAGE2_NODE / "a_linearLags" / "results" / "comparison.json"
B_COMPARISON = STAGE2_NODE / "b_gradientBoosting" / "results" / "comparison.json"
C_COMPARISON = STAGE2_NODE / "c_bayesianRidge" / "results" / "comparison.json"
D_COMPARISON = STAGE2_NODE / "d_linearClimate" / "results" / "comparison.json"
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

    d = json.loads(D_COMPARISON.read_text())
    delta_vs_d = two_stage_crps - d["two_stage_ensemble"]["mean_crps"]
    pct_vs_d = 100 * delta_vs_d / d["two_stage_ensemble"]["mean_crps"]

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
        "vs_d_linearClimate": {
            "d_linearClimate_mean_crps": d["two_stage_ensemble"]["mean_crps"],
            "delta_crps": delta_vs_d,
            "pct_change_vs_d_linearClimate": pct_vs_d,
            "pooling_helps_over_per_province_on_same_input": bool(delta_vs_d < 0),
        },
    }
    (RESULTS / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")

    a = json.loads(A_COMPARISON.read_text())
    b = json.loads(B_COMPARISON.read_text())
    c = json.loads(C_COMPARISON.read_text())
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
            "mean_crps": c["two_stage_ensemble"]["mean_crps"],
            "pct_change_vs_stage1": c["pct_change_vs_stage1"],
            "coverage_empirical": c["two_stage_ensemble"]["coverage_empirical"],
        },
        "d_linearClimate": {
            "mean_crps": d["two_stage_ensemble"]["mean_crps"],
            "pct_change_vs_stage1": d["pct_change_vs_stage1"],
            "coverage_empirical": d["two_stage_ensemble"]["coverage_empirical"],
        },
        "e_pooledRandomForest": {
            "mean_crps": two_stage_crps,
            "pct_change_vs_stage1": pct,
            "coverage_empirical": summary["two_stage_ensemble"]["coverage_empirical"],
        },
        "any_candidate_earns_its_place": bool(
            a["earns_its_place"] or b["earns_its_place"] or c["earns_its_place"]
            or d["earns_its_place"] or summary["earns_its_place"]
        ),
    }
    (RESULTS / "all_candidates_comparison.json").write_text(json.dumps(side_by_side, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(json.dumps(side_by_side, indent=2))


if __name__ == "__main__":
    main()
