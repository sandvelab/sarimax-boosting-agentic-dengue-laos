#!/usr/bin/env python3
"""Stage 1 alone vs. this candidate on the identical cell set: mean CRPS, 90% coverage, the
combination-rule decomposition (stage 1 / clipped / corrected unclipped / corrected and
clipped), by horizon, by split, by province -- and the one axis this candidate changes,
against `g_oosErrorBoosting` on the same cells.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

NODE = Path(__file__).resolve().parents[1]
STAGE2 = NODE.parents[0]
ANALYSIS = NODE.parents[1]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402

STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
OWN_CELLS_CSV = NODE / "results" / "per_cell_scores.csv"
PARENT_COMPARISON = STAGE2 / "g_oosErrorBoosting" / "results" / "comparison.json"
RESULTS = NODE / "results"
NOMINAL = 0.90
Z = 1.6448536269514722


def read_rows(path):
    with path.open(newline="") as f:
        return [r for r in csv.DictReader(f) if r["fit_failed"] == "False" and r["actual"] not in ("", None)]


def score(cells):
    return {"mean_crps": float(np.mean([crps_gaussian(y, mu, max(s, 1e-6)) for y, mu, s in cells])),
            "coverage_empirical": float(np.mean([abs(y - mu) <= Z * s for y, mu, s in cells])),
            "share_mean_negative": float(np.mean([mu < 0 for _, mu, _ in cells]))}


def main() -> None:
    s1 = read_rows(STAGE1_CELLS_CSV)
    own = read_rows(OWN_CELLS_CSV)
    if len(own) != len(s1):
        raise RuntimeError(f"cell-set mismatch: stage 1 {len(s1)} scored cells, candidate {len(own)}")

    def cells(kind):
        out = []
        for r in own:
            y, mu1, se = float(r["actual"]), float(r["stage1_mean"]), float(r["stage1_se"])
            unclipped = mu1 + float(r["stage2_correction"])
            mu = {"stage1": mu1, "stage1_clipped": max(mu1, 0.0), "corrected_unclipped": unclipped,
                  "corrected_clipped (this candidate)": float(r["final_mean"])}[kind]
            out.append((y, mu, se))
        return out

    variants = {k: score(cells(k)) for k in ("stage1", "stage1_clipped", "corrected_unclipped", "corrected_clipped (this candidate)")}
    stage1_crps = variants["stage1"]["mean_crps"]
    cand = variants["corrected_clipped (this candidate)"]
    for v in variants.values():
        v["pct_change_vs_stage1"] = 100 * (v["mean_crps"] - stage1_crps) / stage1_crps

    def crps1(r):
        return float(r["crps_stage1"])

    by_h = {f"h{h}": {"n": len(sub), "stage1_mean_crps": float(np.mean([crps1(r) for r in sub])),
                        "candidate_mean_crps": float(np.mean([float(r["crps"]) for r in sub]))}
            for h in ("1", "2", "3") for sub in [[r for r in own if r["h"] == h]]}
    by_split = {}
    for s in sorted({r["split"] for r in own}, key=int):
        sub = [r for r in own if r["split"] == s]
        c1, c2 = float(np.mean([crps1(r) for r in sub])), float(np.mean([float(r["crps"]) for r in sub]))
        by_split[f"split{s}"] = {"n": len(sub), "stage1_mean_crps": c1, "candidate_mean_crps": c2, "pct_change": 100 * (c2 - c1) / c1}
    n_splits_improved = sum(1 for v in by_split.values() if v["candidate_mean_crps"] < v["stage1_mean_crps"])
    deltas = [float(r["crps"]) - crps1(r) for r in own]
    by_province = []
    for p in sorted({r["province"] for r in own}):
        sub = [r for r in own if r["province"] == p]
        c1, c2 = float(np.sum([crps1(r) for r in sub])), float(np.sum([float(r["crps"]) for r in sub]))
        by_province.append({"province": p, "n": len(sub), "mean_actual": float(np.mean([float(r["actual"]) for r in sub])),
                            "stage1_crps_sum": c1, "candidate_crps_sum": c2, "delta_crps_sum": c2 - c1,
                            "mean_abs_correction": float(np.mean([abs(float(r["stage2_correction"])) for r in sub]))})
    by_province.sort(key=lambda r: r["delta_crps_sum"])

    parent = json.loads(PARENT_COMPARISON.read_text())
    parent_crps = parent["two_stage_ensemble"]["mean_crps"]
    summary = {
        "n_cells": len(own),
        "stage1_alone": {"mean_crps": stage1_crps, "coverage_nominal": NOMINAL, "coverage_empirical": variants["stage1"]["coverage_empirical"]},
        "two_stage_ensemble": {"mean_crps": cand["mean_crps"], "coverage_nominal": NOMINAL, "coverage_empirical": cand["coverage_empirical"]},
        "delta_crps": cand["mean_crps"] - stage1_crps,
        "pct_change_vs_stage1": cand["pct_change_vs_stage1"],
        "earns_its_place": bool(cand["mean_crps"] < stage1_crps),
        "coverage_not_worse_than_stage1": bool(cand["coverage_empirical"] >= variants["stage1"]["coverage_empirical"]),
        "vs_g_oosErrorBoosting": {"parent_mean_crps": parent_crps, "delta_crps": cand["mean_crps"] - parent_crps,
                        "pct_change_vs_parent": 100 * (cand["mean_crps"] - parent_crps) / parent_crps,
                        "parent_coverage_empirical": parent["two_stage_ensemble"]["coverage_empirical"],
                        "better_than_parent_on_crps": bool(cand["mean_crps"] < parent_crps)},
        "combination_rule_decomposition": variants,
        "by_horizon": by_h, "by_split": by_split, "n_splits_improved_of_8": n_splits_improved,
        "share_cells_improved": float(np.mean([d < 0 for d in deltas])),
        "by_province_sorted_by_gain": by_province,
    }
    (RESULTS / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("by_province_sorted_by_gain", "by_split")}, indent=2))


if __name__ == "__main__":
    main()
