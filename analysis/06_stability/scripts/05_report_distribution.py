#!/usr/bin/env python3
"""`/perturb report`: the distribution of the central conclusion across the perturbation set
-- not the best row, and not one headline with a robustness footnote.

Reads `results/conclusions.csv` and each combination's `conclusion.json` and per-cell file;
writes:

- `results/distribution.json` -- the whole-set summary: how the two-stage-vs-stage-1 margin
  is distributed over the 29 tier-2 perturbations (quantiles, sign, coverage), per judgment-
  call group (stage 1 specification; window, scheme and data; the stage-2 target and
  combination rule; features; family hyperparameters and seed; how the training errors are
  made), which rows move the margin's *size* by more than SENSITIVITY_POINTS percentage
  points from the main path's, whether any row moves its *sign*, and the tier-1 and tier-3
  rows restated;
- `results/perturbation_effects.csv` -- one row per tier-2 perturbation with its group, its
  margin, its deviation from the main path's margin, coverage change and splits improved;
- `results/province_stability.csv` -- per province, the share of combinations in which the
  two-stage ensemble lowers that province's summed CRPS, and the median change -- because
  batch 10 found the gains and losses concentrated in a few provinces, and a margin that
  depends on one province is a different finding from one that does not;
- `results/horizon_stability.csv` -- per horizon, the share of combinations in which the
  ensemble improves it.

Groups are assigned by combination name, from the manifest's own naming. Nothing is
recomputed from raw data; every number here is read from a file another script wrote.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
RESULTS = NODE / "results"
SENSITIVITY_POINTS = 2.0  # reporting threshold: a margin this many points away (either way) counts as moving the size

GROUPS = {
    "stage 1 specification": ["stage1=airline_011x011", "stage1=nodiff_101x100", "stage1=enforce_stationarity"],
    "training window, scheme, data": ["window=rolling_72m", "window=start_2002", "scheme=chap_default_7x1", "modelable=36_months"],
    "stage 2 target and combination rule": ["stage2=g_no_clip", "stage2=g_zclip2", "stage2=g_zclip5", "stage2=g_no_winsorisation",
                                            "stage2=g_scale_by_residual_rms", "stage2=g_bounded_correction", "stage2=g_per_horizon"],
    "stage 2 features": ["stage2=g_no_cross_province", "stage2=g_no_incidence_terms", "stage2=g_level_month_horizon_only",
                         "stage2=g_with_climate_anomalies"],
    "stage 2 family hyperparameters and seed": ["stage2=g_depth2", "stage2=g_depth4_300trees", "stage2=g_lr0.1", "stage2=g_min_leaf50",
                                                "stage2=g_alt_seed", "stage2=f_alpha1", "stage2=f_alpha100"],
    "how the training errors are made": ["stage2=g_warmup12", "stage2=g_warmup36", "stage2=g_rolling_refit_oos", "stage2=g_min_train_rows1000"],
}
GROUP_OF = {c: g for g, cs in GROUPS.items() for c in cs}


def fnum(x):
    return float(x) if x not in ("", None, "-") else None


def q(values, p):
    values = sorted(values)
    k = (len(values) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def province_deltas(combination: str) -> dict[str, float]:
    with (RESULTS / combination / "per_cell_scores.csv").open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["fit_failed"] == "False" and r["crps"] not in ("", None)]
    out: dict[str, float] = defaultdict(float)
    for r in rows:
        out[r["province"]] += float(r["crps"]) - float(r["crps_stage1"])
    return dict(out)


def main() -> None:
    with (RESULTS / "conclusions.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    main_row = next(r for r in rows if r["tier"] == "0")
    main_pct = float(main_row["pct_change_vs_stage1"])
    t1 = [r for r in rows if r["tier"] == "1"]
    t2 = [r for r in rows if r["tier"] == "2" and r["status"] == "run"]
    t3 = [r for r in rows if r["tier"] == "3"]
    unassigned = [r["combination"] for r in t2 if r["combination"] not in GROUP_OF]
    if unassigned:
        raise RuntimeError(f"tier-2 rows without a group: {unassigned}")

    effects = []
    for r in t2:
        pct = float(r["pct_change_vs_stage1"])
        effects.append({
            "combination": r["combination"], "group": GROUP_OF[r["combination"]],
            "stage1_mean_crps": fnum(r["stage1_mean_crps"]), "two_stage_mean_crps": fnum(r["two_stage_mean_crps"]),
            "pct_change_vs_stage1": pct, "deviation_from_main_points": pct - main_pct,
            "moves_size": abs(pct - main_pct) > SENSITIVITY_POINTS,
            "beats_stage1_on_crps": r["beats_stage1_on_crps"] == "True",
            "coverage_change_points": 100 * (float(r["two_stage_coverage_90"]) - float(r["stage1_coverage_90"])),
            "coverage_not_worse": r["coverage_not_worse"] == "True",
            "n_splits_improved": int(r["n_splits_improved"]), "n_splits": int(r["n_splits"]),
            "share_cells_improved": fnum(r["share_cells_improved"]),
            "informativeness_rank": r["informativeness_rank"],
        })
    effects.sort(key=lambda e: e["pct_change_vs_stage1"])
    with (RESULTS / "perturbation_effects.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(effects[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(effects)

    pcts = [e["pct_change_vs_stage1"] for e in effects]
    by_group = {}
    for g, cs in GROUPS.items():
        es = [e for e in effects if e["group"] == g]
        gp = [e["pct_change_vs_stage1"] for e in es]
        by_group[g] = {
            "n": len(es), "min_pct": min(gp), "median_pct": st.median(gp), "max_pct": max(gp),
            "all_beat_stage1": all(e["beats_stage1_on_crps"] for e in es),
            "all_coverage_not_worse": all(e["coverage_not_worse"] for e in es),
            "rows_moving_size": [e["combination"] for e in es if e["moves_size"]],
            "splits_improved_range": [min(e["n_splits_improved"] for e in es), max(e["n_splits_improved"] for e in es)],
        }

    # Per-province and per-horizon stability across main + every tier-2 combination.
    combos = ["main"] + [e["combination"] for e in effects]
    prov: dict[str, list[float]] = defaultdict(list)
    horizon: dict[str, list[bool]] = defaultdict(list)
    for c in combos:
        for p, d in province_deltas(c).items():
            prov[p].append(d)
        conc = json.loads((RESULTS / c / "conclusion.json").read_text())
        for h, v in conc["by_horizon"].items():
            horizon[h].append(v["two_stage"] < v["stage1"])
    prov_rows = []
    for p, ds in sorted(prov.items(), key=lambda kv: st.median(kv[1])):
        prov_rows.append({"province": p, "n_combinations": len(ds),
                          "share_combinations_improved": sum(1 for d in ds if d < 0) / len(ds),
                          "median_delta_crps_sum": st.median(ds), "min_delta_crps_sum": min(ds), "max_delta_crps_sum": max(ds),
                          "main_delta_crps_sum": province_deltas("main").get(p)})
    with (RESULTS / "province_stability.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(prov_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(prov_rows)
    hz_rows = [{"horizon": h, "n_combinations": len(v), "share_combinations_improved": sum(v) / len(v)} for h, v in sorted(horizon.items())]
    with (RESULTS / "horizon_stability.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hz_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(hz_rows)

    always_improved = [r["province"] for r in prov_rows if r["share_combinations_improved"] == 1.0]
    never_improved = [r["province"] for r in prov_rows if r["share_combinations_improved"] == 0.0]
    summary = {
        "main_path": {"combination": main_row["combination"], "pct_change_vs_stage1": main_pct,
                      "stage1_mean_crps": fnum(main_row["stage1_mean_crps"]), "two_stage_mean_crps": fnum(main_row["two_stage_mean_crps"]),
                      "coverage_stage1": fnum(main_row["stage1_coverage_90"]), "coverage_two_stage": fnum(main_row["two_stage_coverage_90"])},
        "tier2_distribution_of_pct_change": {
            "n": len(pcts), "min": min(pcts), "q10": q(pcts, 0.10), "q25": q(pcts, 0.25), "median": st.median(pcts),
            "q75": q(pcts, 0.75), "q90": q(pcts, 0.90), "max": max(pcts),
            "n_two_stage_beats_stage1": sum(e["beats_stage1_on_crps"] for e in effects),
            "n_coverage_not_worse": sum(e["coverage_not_worse"] for e in effects),
            "n_sign_flips": sum(1 for e in effects if not e["beats_stage1_on_crps"]),
            "n_moving_size_beyond_points": sum(e["moves_size"] for e in effects), "sensitivity_points": SENSITIVITY_POINTS,
            "rows_with_larger_margin_than_main": [e["combination"] for e in effects if e["pct_change_vs_stage1"] < main_pct - SENSITIVITY_POINTS],
            "rows_with_smaller_margin_than_main": [e["combination"] for e in effects if e["pct_change_vs_stage1"] > main_pct + SENSITIVITY_POINTS],
            "splits_improved_distribution": {str(k): sum(1 for e in effects if e["n_splits_improved"] == k) for k in range(0, 9)},
            "rows_improving_fewer_than_half_the_splits": [e["combination"] for e in effects if e["n_splits_improved"] * 2 < e["n_splits"]],
        },
        "by_judgment_call_group": by_group,
        "province_stability": {"n_provinces": len(prov_rows), "always_improved": always_improved, "never_improved": never_improved,
                               "improved_in_at_least_90pct_of_combinations": [r["province"] for r in prov_rows if r["share_combinations_improved"] >= 0.9],
                               "improved_in_at_most_10pct_of_combinations": [r["province"] for r in prov_rows if r["share_combinations_improved"] <= 0.1]},
        "horizon_stability": hz_rows,
        "tier1_siblings": [{"combination": r["combination"], "pct_change_vs_stage1": fnum(r["pct_change_vs_stage1"]),
                            "two_stage_coverage_90": fnum(r["two_stage_coverage_90"]), "beats_stage1_on_crps": r["beats_stage1_on_crps"] == "True",
                            "coverage_not_worse": r["coverage_not_worse"] == "True"} for r in t1],
        "tier3_not_run": [{"combination": r["combination"], "reason": r["reason_if_not_run"]} for r in t3],
    }
    (RESULTS / "distribution.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("tier1_siblings", "tier3_not_run")}, indent=2))


if __name__ == "__main__":
    main()
