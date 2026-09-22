#!/usr/bin/env python3
"""The held-out report, written by the rule frozen in `results/holdout_freeze.json` before the
year was opened. The rule is read from that file at run time and copied into the output, so the
report can be checked against it rather than against a memory of it.

Writes:

- `results/distribution_holdout.json` -- the primary answer (plan §2's two bars on the main
  path), the required baselines beside both stages, the distribution over the tier-2 rows, the
  per-judgment-call groups, the province and horizon concentration, the tier-1 siblings and the
  rows that were never run, and the comparison with development;
- `results/perturbation_effects_holdout.csv` -- one row per tier-2 perturbation with its group,
  margin, deviation from the main path's, coverage change and splits improved;
- `results/province_stability_holdout.csv` and `results/horizon_stability_holdout.csv`;
- `results/development_comparison_holdout.csv` -- every row beside its development v2
  counterpart, which is the pairing the frozen rule asks for.

Nothing is recomputed from raw data: every number is read from a file `08_run_holdout.py` or
`09_collect_holdout.py` wrote. The threshold for "moves the size" is the frozen one, so the
three reports (v1, v2, held out) compare without a rescaling.

Seeds: none drawn.
"""
from __future__ import annotations

import csv
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ANALYSIS = NODE.parents[0]
sys.path.insert(0, str(NODE / "scripts"))
RESULTS = NODE / "results"

GROUPS = {
    "stage 1 specification": ["stage1=airline_011x011", "stage1=nodiff_101x100",
                              "stage1=enforce_stationarity"],
    "training window, scheme, data": ["window=rolling_72m", "window=start_2002",
                                      "scheme=chap_default_7x1", "modelable=36_months"],
    "stage 2 target and combination rule": ["stage2=no_clip", "stage2=zclip2", "stage2=zclip5",
                                            "stage2=no_winsorisation", "stage2=scale_by_residual_rms",
                                            "stage2=bounded_floor0", "stage2=per_horizon"],
    "stage 2 features": ["stage2=plus_recent_and_incidence", "stage2=plus_recent_and_cross",
                         "stage2=full_plus_climate"],
    "stage 2 family hyperparameters and seed": ["stage2=depth2", "stage2=depth4_300trees",
                                                "stage2=lr0.1", "stage2=min_leaf50", "stage2=alt_seed"],
    "how the training errors are made": ["stage2=warmup12", "stage2=warmup36",
                                         "stage2=rolling_refit_oos", "stage2=min_train_rows1000"],
}
GROUP_OF = {c: g for g, cs in GROUPS.items() for c in cs}
SUFFIX = "__holdout"


def base_name(combination: str) -> str:
    """The perturbation a row names, with the holdout suffix and the `@h` version tag removed."""
    c = combination[: -len(SUFFIX)] if combination.endswith(SUFFIX) else combination
    return c[:-2] if c.endswith("@h") else c


def fnum(x):
    return float(x) if x not in ("", None, "-") else None


def q(values, p):
    values = sorted(values)
    k = (len(values) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def conclusion(combination: str) -> dict:
    return json.loads((RESULTS / combination / "conclusion.json").read_text())


def province_deltas(combination: str) -> dict[str, float]:
    with (RESULTS / combination / "per_cell_scores.csv").open(newline="") as f:
        rows = [r for r in csv.DictReader(f)
                if r["fit_failed"] == "False" and r["crps"] not in ("", None)]
    out: dict[str, float] = defaultdict(float)
    for r in rows:
        out[r["province"]] += float(r["crps"]) - float(r["crps_stage1"])
    return dict(out)


def main() -> None:
    freeze = json.loads((RESULTS / "holdout_freeze.json").read_text())
    rule = freeze["reporting_rule"]
    points = json.loads((RESULTS / "manifest_holdout_summary.json").read_text())["sensitivity_points"]
    with (RESULTS / "conclusions_holdout.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))

    main_combo = f"main@h{SUFFIX}"
    main_row = next(r for r in rows if r["combination"] == main_combo)
    main_pct = float(main_row["pct_change_vs_stage1"])
    baselines = [r for r in rows if r["model_type"] == "baseline"]
    t1_run = [r for r in rows if r["tier"] == "1" and r["status"] == "run"]
    t1_not_run = [r for r in rows if r["tier"] == "1" and r["status"] == "not_run"]
    t2 = [r for r in rows if r["tier"] == "2" and r["status"] == "run"]
    t3 = [r for r in rows if r["tier"] == "3"]
    unassigned = [r["combination"] for r in t2 if base_name(r["combination"]) not in GROUP_OF]
    if unassigned:
        raise RuntimeError(f"tier-2 rows without a group: {unassigned}")

    # --- the distribution over the tier-2 rows -------------------------------------------------
    effects = []
    for r in t2:
        pct = float(r["pct_change_vs_stage1"])
        effects.append({
            "combination": r["combination"], "group": GROUP_OF[base_name(r["combination"])],
            "stage1_mean_crps": fnum(r["stage1_mean_crps"]),
            "two_stage_mean_crps": fnum(r["two_stage_mean_crps"]),
            "pct_change_vs_stage1": pct, "deviation_from_main_points": pct - main_pct,
            "moves_size": abs(pct - main_pct) > points,
            "beats_stage1_on_crps": r["beats_stage1_on_crps"] == "True",
            "coverage_change_points": 100 * (float(r["two_stage_coverage_90"]) - float(r["stage1_coverage_90"])),
            "coverage_not_worse": r["coverage_not_worse"] == "True",
            "n_splits_improved": int(r["n_splits_improved"]), "n_splits": int(r["n_splits"]),
            "share_cells_improved": fnum(r["share_cells_improved"]),
            "development_pct_change": fnum(r["development_pct_change"]),
            "shift_points": fnum(r["shift_points"]),
        })
    effects.sort(key=lambda e: e["pct_change_vs_stage1"])
    with (RESULTS / "perturbation_effects_holdout.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(effects[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(effects)

    pcts = [e["pct_change_vs_stage1"] for e in effects]
    by_group = {}
    for g in GROUPS:
        es = [e for e in effects if e["group"] == g]
        if not es:
            continue
        gp = [e["pct_change_vs_stage1"] for e in es]
        by_group[g] = {"n": len(es), "min_pct": min(gp), "median_pct": st.median(gp), "max_pct": max(gp),
                       "all_beat_stage1": all(e["beats_stage1_on_crps"] for e in es),
                       "all_coverage_not_worse": all(e["coverage_not_worse"] for e in es),
                       "rows_moving_size": [e["combination"] for e in es if e["moves_size"]],
                       "splits_improved_range": [min(e["n_splits_improved"] for e in es),
                                                 max(e["n_splits_improved"] for e in es)]}

    # --- province and horizon concentration, over the main path and every tier-2 row ------------
    combos = [main_combo] + [e["combination"] for e in effects]
    prov: dict[str, list[float]] = defaultdict(list)
    horizon: dict[str, list[bool]] = defaultdict(list)
    for c in combos:
        for p, d in province_deltas(c).items():
            prov[p].append(d)
        for h, v in conclusion(c)["by_horizon"].items():
            horizon[h].append(v["two_stage"] < v["stage1"])
    main_deltas = province_deltas(main_combo)
    prov_rows = [{"province": p, "n_combinations": len(ds),
                  "share_combinations_improved": sum(1 for d in ds if d < 0) / len(ds),
                  "median_delta_crps_sum": st.median(ds), "min_delta_crps_sum": min(ds),
                  "max_delta_crps_sum": max(ds), "main_delta_crps_sum": main_deltas.get(p)}
                 for p, ds in sorted(prov.items(), key=lambda kv: st.median(kv[1]))]
    with (RESULTS / "province_stability_holdout.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(prov_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(prov_rows)
    hz_rows = [{"horizon": h, "n_combinations": len(v), "share_combinations_improved": sum(v) / len(v)}
               for h, v in sorted(horizon.items())]
    with (RESULTS / "horizon_stability_holdout.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hz_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(hz_rows)

    # --- the pairing with development ------------------------------------------------------------
    paired = [r for r in rows if r["status"] == "run" and r["model_type"] == "two_stage"
              and fnum(r["development_pct_change"]) is not None]
    with (RESULTS / "development_comparison_holdout.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["combination", "tier", "development_row",
                                          "development_pct_change", "holdout_pct_change",
                                          "shift_points", "holdout_beats_stage1",
                                          "holdout_coverage_not_worse"], lineterminator="\n")
        w.writeheader()
        for r in paired:
            w.writerow({"combination": r["combination"], "tier": r["tier"],
                        "development_row": r["development_row"],
                        "development_pct_change": fnum(r["development_pct_change"]),
                        "holdout_pct_change": fnum(r["pct_change_vs_stage1"]),
                        "shift_points": fnum(r["shift_points"]),
                        "holdout_beats_stage1": r["beats_stage1_on_crps"],
                        "holdout_coverage_not_worse": r["coverage_not_worse"]})
    shifts = [fnum(r["shift_points"]) for r in paired]

    main_c = conclusion(main_combo)
    dev_dist = json.loads((RESULTS / "distribution_v2.json").read_text())
    summary = {
        "phase": "E", "reporting_rule": rule, "sensitivity_points": points,
        "opening": json.loads((RESULTS / "run_summary_holdout.json").read_text()),
        "primary": {
            "combination": main_combo, "main_path": freeze["main_path"],
            "n_cells": main_c["n_cells_scored"], "evaluated_months": main_c["evaluated_months"],
            "stage1_mean_crps": main_c["stage1_alone"]["mean_crps"],
            "two_stage_mean_crps": main_c["two_stage"]["mean_crps"],
            "pct_change_vs_stage1": main_pct,
            "coverage_stage1": main_c["stage1_alone"]["coverage_90"],
            "coverage_two_stage": main_c["two_stage"]["coverage_90"],
            "beats_stage1_on_crps": main_c["two_stage_beats_stage1_on_crps"],
            "coverage_not_worse": main_c["coverage_not_worse_than_stage1"],
            "earns_its_place_on_the_holdout": bool(main_c["two_stage_beats_stage1_on_crps"]
                                                   and main_c["coverage_not_worse_than_stage1"]),
            "n_splits_improved": main_c["n_splits_improved"], "n_splits": main_c["n_splits"],
            "share_cells_improved": main_c["share_cells_improved"],
            "by_split": main_c["by_split"], "by_horizon": main_c["by_horizon"],
            "development_pct_change": fnum(main_row["development_pct_change"]),
            "shift_points_vs_development": fnum(main_row["shift_points"]),
        },
        "required_baselines": [{"combination": b["combination"], "mean_crps": fnum(b["baseline_mean_crps"]),
                                "coverage_90": fnum(b["baseline_coverage_90"]), "n_cells": int(b["n_cells"])}
                               for b in baselines],
        "tier2_distribution_of_pct_change": {
            "n": len(pcts), "min": min(pcts), "q10": q(pcts, 0.10), "q25": q(pcts, 0.25),
            "median": st.median(pcts), "q75": q(pcts, 0.75), "q90": q(pcts, 0.90), "max": max(pcts),
            "n_two_stage_beats_stage1": sum(e["beats_stage1_on_crps"] for e in effects),
            "n_coverage_not_worse": sum(e["coverage_not_worse"] for e in effects),
            "n_sign_flips": sum(1 for e in effects if not e["beats_stage1_on_crps"]),
            "n_moving_size_beyond_points": sum(e["moves_size"] for e in effects),
            "rows_with_larger_margin_than_main": [e["combination"] for e in effects
                                                  if e["pct_change_vs_stage1"] < main_pct - points],
            "rows_with_smaller_margin_than_main": [e["combination"] for e in effects
                                                   if e["pct_change_vs_stage1"] > main_pct + points],
            "splits_improved_distribution": {str(k): sum(1 for e in effects if e["n_splits_improved"] == k)
                                             for k in range(0, 9)},
            "rows_improving_fewer_than_half_the_splits": [e["combination"] for e in effects
                                                          if e["n_splits_improved"] * 2 < e["n_splits"]],
        },
        "by_judgment_call_group": by_group,
        "province_stability": {
            "n_provinces": len(prov_rows),
            "always_improved": [r["province"] for r in prov_rows if r["share_combinations_improved"] == 1.0],
            "never_improved": [r["province"] for r in prov_rows if r["share_combinations_improved"] == 0.0],
            "improved_in_at_least_90pct_of_combinations": [r["province"] for r in prov_rows
                                                           if r["share_combinations_improved"] >= 0.9],
            "improved_in_at_most_10pct_of_combinations": [r["province"] for r in prov_rows
                                                          if r["share_combinations_improved"] <= 0.1]},
        "horizon_stability": hz_rows,
        "tier1_siblings": [{"combination": r["combination"], "pct_change_vs_stage1": fnum(r["pct_change_vs_stage1"]),
                            "two_stage_mean_crps": fnum(r["two_stage_mean_crps"]),
                            "two_stage_coverage_90": fnum(r["two_stage_coverage_90"]),
                            "beats_stage1_on_crps": r["beats_stage1_on_crps"] == "True",
                            "coverage_not_worse": r["coverage_not_worse"] == "True",
                            "development_pct_change": fnum(r["development_pct_change"]),
                            "shift_points": fnum(r["shift_points"])} for r in t1_run],
        "not_run": [{"combination": r["combination"], "tier": r["tier"], "reason": r["reason_if_not_run"]}
                    for r in t1_not_run + t3],
        "versus_development": {
            "development_version": 2, "development_main_pct_change": dev_dist["main_path"]["pct_change_vs_stage1"],
            "holdout_main_pct_change": main_pct,
            "main_path_shift_points": main_pct - dev_dist["main_path"]["pct_change_vs_stage1"],
            "development_tier2_distribution": {k: dev_dist["tier2_distribution_of_pct_change"][k]
                                               for k in ("n", "min", "q25", "median", "q75", "max",
                                                         "n_two_stage_beats_stage1", "n_coverage_not_worse",
                                                         "n_sign_flips", "n_moving_size_beyond_points")},
            "n_rows_paired": len(paired),
            "n_paired_with_larger_margin_on_holdout": sum(1 for s in shifts if s < 0),
            "n_paired_with_smaller_margin_on_holdout": sum(1 for s in shifts if s > 0),
            "shift_points_min": min(shifts), "shift_points_median": st.median(shifts),
            "shift_points_max": max(shifts),
        },
    }
    (RESULTS / "distribution_holdout.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("reporting_rule", "tier1_siblings", "not_run", "opening")}, indent=2))


if __name__ == "__main__":
    main()
