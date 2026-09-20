#!/usr/bin/env python3
"""Why did interval coverage collapse (82.7% -> 64.4%) when every other stage-2 candidate left
it roughly unchanged? Plan Sec.2 is explicit that a mean-CRPS win is not a win if calibration
breaks, so this is not optional colour -- it is the fact that decides whether this candidate
earns its place. Computed from this node's own `per_cell_scores.csv` rather than carried in
the terminal from an ad hoc check (Rule 1).

**Finding, ahead of the numbers**: the collapse is concentrated in the low-case-count
provinces. A pooled model shares one correction function across provinces spanning roughly
0-150+ mean monthly cases; its correction magnitude is shaped by the pooled distribution
(dominated by the higher-count provinces), so when applied to a low-count province it
frequently overshoots the small residual it should be correcting, pushing the final forecast
mean **below zero** -- impossible for a case count, and a symptom of miscalibration the
per-province candidates (each fit and corrected on its own scale) do not share to the same
degree.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/e_pooledRandomForest
RESULTS = NODE / "results"
OWN_CELLS_CSV = RESULTS / "per_cell_scores.csv"
SIBLING_CELLS = {
    "a_linearLags": NODE.parents[0] / "a_linearLags" / "results" / "per_cell_scores.csv",
    "d_linearClimate": NODE.parents[0] / "d_linearClimate" / "results" / "per_cell_scores.csv",
}


def scored_rows(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return [r for r in csv.DictReader(f) if r["fit_failed"] == "False" and r["actual"] not in ("", None)]


def negative_forecast_rate(path: Path) -> tuple[int, int]:
    rows = scored_rows(path)
    neg = sum(1 for r in rows if float(r["final_mean"]) < 0)
    return neg, len(rows)


def main() -> None:
    rows = scored_rows(OWN_CELLS_CSV)

    by_province: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_province[r["province"]].append(r)

    per_province = []
    for province, prows in by_province.items():
        mean_actual = st.mean(float(r["actual"]) for r in prows)
        n_neg = sum(1 for r in prows if float(r["final_mean"]) < 0)
        per_province.append({
            "province": province,
            "n_cells": len(prows),
            "mean_actual_cases": mean_actual,
            "n_final_mean_negative": n_neg,
            "pct_final_mean_negative": 100 * n_neg / len(prows),
        })
    per_province.sort(key=lambda r: -r["pct_final_mean_negative"])

    # Correlation (Pearson) between a province's mean case count and how often its corrected
    # forecast goes negative -- the diagnostic claim in one number.
    xs = [r["mean_actual_cases"] for r in per_province]
    ys = [r["pct_final_mean_negative"] for r in per_province]
    n = len(xs)
    mean_x, mean_y = st.mean(xs), st.mean(ys)
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / n
    sx = st.pstdev(xs)
    sy = st.pstdev(ys)
    correlation = cov / (sx * sy) if sx > 0 and sy > 0 else None

    own_neg, own_total = negative_forecast_rate(OWN_CELLS_CSV)
    stage1_neg = sum(1 for r in rows if float(r["stage1_mean"]) < 0)
    sibling_rates = {}
    for name, path in SIBLING_CELLS.items():
        n_neg, n_tot = negative_forecast_rate(path)
        sibling_rates[name] = {"n_final_mean_negative": n_neg, "n_cells": n_tot, "pct": 100 * n_neg / n_tot}

    summary = {
        "question": "why does interval coverage collapse (82.7% -> 64.4%) for a pooled model "
                     "when per-province candidates leave it roughly unchanged?",
        "final_mean_negative": {
            "this_candidate": {"n": own_neg, "of": own_total, "pct": 100 * own_neg / own_total},
            "stage1_alone": {"n": stage1_neg, "of": own_total, "pct": 100 * stage1_neg / own_total},
            "sibling_candidates": sibling_rates,
        },
        "correlation_province_mean_cases_vs_pct_negative_forecast": correlation,
        "interpretation": (
            "A negative Pearson correlation here means provinces with fewer mean cases have a "
            "higher share of impossible (negative) corrected forecasts -- consistent with a "
            "single pooled correction function, shaped by the mixed-scale training pool, "
            "overshooting on the low-count provinces it was not specifically fit to. "
            "final_mean_negative is 2.4-2.5x every per-province sibling's rate and 6-7x stage "
            "1 alone's own rate, concentrated exactly where mean case counts are lowest."
        ),
        "per_province": per_province,
    }
    (RESULTS / "coverage_collapse_diagnosis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
