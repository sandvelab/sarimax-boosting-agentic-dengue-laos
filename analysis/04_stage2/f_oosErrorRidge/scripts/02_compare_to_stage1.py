#!/usr/bin/env python3
"""Stage 1 alone vs. this candidate: mean CRPS and 90% interval coverage, on the identical
cell set -- plus the decomposition the combination rule owes.

This candidate changes two things relative to stage 1's mean: it adds a predicted correction
and it clips the result at zero. Both are stored per cell, so the four combinations are scored
here from the same file rather than asserted: stage 1; stage 1 clipped; stage 1 + correction
unclipped; stage 1 + correction clipped (the candidate). The by-horizon and by-province-scale
breakdowns say where any gain or loss sits, since `05_residualStructure` showed the errors are
concentrated in a few large or regime-breaking provinces.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

NODE = Path(__file__).resolve().parents[1]
ANALYSIS = NODE.parents[1]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402

STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
OWN_CELLS_CSV = NODE / "results" / "per_cell_scores.csv"
RESULTS = NODE / "results"
NOMINAL = 0.90
Z = 1.6448536269514722


def read_rows(path):
    with path.open(newline="") as f:
        return [r for r in csv.DictReader(f) if r["fit_failed"] == "False" and r["actual"] not in ("", None)]


def score(cells):
    crps = [crps_gaussian(y, mu, max(s, 1e-6)) for y, mu, s in cells]
    cov = [abs(y - mu) <= Z * s for y, mu, s in cells]
    return {"mean_crps": float(np.mean(crps)), "coverage_empirical": float(np.mean(cov)),
            "share_mean_negative": float(np.mean([mu < 0 for _, mu, _ in cells]))}


def main() -> None:
    s1 = {(r["province"], r["split"], r["month"]): r for r in read_rows(STAGE1_CELLS_CSV)}
    own = read_rows(OWN_CELLS_CSV)
    if len(own) != len(s1):
        raise RuntimeError(f"cell-set mismatch: stage 1 {len(s1)} scored cells, candidate {len(own)}")

    def cells(kind):
        out = []
        for r in own:
            y, mu1, se = float(r["actual"]), float(r["stage1_mean"]), float(r["stage1_se"])
            unclipped, final = float(r["final_mean_unclipped"]), float(r["final_mean"])
            mu = {"stage1": mu1, "stage1_clipped": max(mu1, 0.0), "corrected_unclipped": unclipped,
                  "corrected_clipped (this candidate)": final}[kind]
            out.append((y, mu, se))
        return out

    variants = {k: score(cells(k)) for k in ("stage1", "stage1_clipped", "corrected_unclipped",
                                              "corrected_clipped (this candidate)")}
    stage1_crps = variants["stage1"]["mean_crps"]
    cand = variants["corrected_clipped (this candidate)"]
    for k, v in variants.items():
        v["pct_change_vs_stage1"] = 100 * (v["mean_crps"] - stage1_crps) / stage1_crps

    by_h = {}
    for h in ("1", "2", "3"):
        sub = [r for r in own if r["h"] == h]
        by_h[f"h{h}"] = {
            "n": len(sub),
            "stage1_mean_crps": float(np.mean([crps_gaussian(float(r["actual"]), float(r["stage1_mean"]),
                                                             max(float(r["stage1_se"]), 1e-6)) for r in sub])),
            "candidate_mean_crps": float(np.mean([float(r["crps"]) for r in sub])),
        }

    by_province = []
    for p in sorted({r["province"] for r in own}):
        sub = [r for r in own if r["province"] == p]
        c1 = float(np.sum([crps_gaussian(float(r["actual"]), float(r["stage1_mean"]), max(float(r["stage1_se"]), 1e-6))
                           for r in sub]))
        c2 = float(np.sum([float(r["crps"]) for r in sub]))
        by_province.append({"province": p, "n": len(sub), "mean_actual": float(np.mean([float(r["actual"]) for r in sub])),
                            "stage1_crps_sum": c1, "candidate_crps_sum": c2, "delta_crps_sum": c2 - c1,
                            "mean_abs_zhat": float(np.mean([abs(float(r["stage2_zhat"])) for r in sub]))})
    by_province.sort(key=lambda r: r["delta_crps_sum"])

    summary = {
        "n_cells": len(own),
        "stage1_alone": {"mean_crps": stage1_crps, "coverage_nominal": NOMINAL,
                         "coverage_empirical": variants["stage1"]["coverage_empirical"]},
        "two_stage_ensemble": {"mean_crps": cand["mean_crps"], "coverage_nominal": NOMINAL,
                               "coverage_empirical": cand["coverage_empirical"]},
        "delta_crps": cand["mean_crps"] - stage1_crps,
        "pct_change_vs_stage1": cand["pct_change_vs_stage1"],
        "earns_its_place": bool(cand["mean_crps"] < stage1_crps),
        "coverage_within_5_points_of_stage1": bool(
            abs(cand["coverage_empirical"] - variants["stage1"]["coverage_empirical"]) <= 0.05),
        "combination_rule_decomposition": variants,
        "correction_alone_pct_change_vs_stage1_clipped": 100 * (
            cand["mean_crps"] - variants["stage1_clipped"]["mean_crps"]) / variants["stage1_clipped"]["mean_crps"],
        "by_horizon": by_h,
        "by_province_sorted_by_gain": by_province,
        "mean_abs_zhat": float(np.mean([abs(float(r["stage2_zhat"])) for r in own])),
        "share_abstained": float(np.mean([r["stage2_abstained"] == "True" for r in own])),
    }
    (RESULTS / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "by_province_sorted_by_gain"}, indent=2))
    print(json.dumps(summary["by_province_sorted_by_gain"][:5] + summary["by_province_sorted_by_gain"][-3:], indent=2))


if __name__ == "__main__":
    main()
