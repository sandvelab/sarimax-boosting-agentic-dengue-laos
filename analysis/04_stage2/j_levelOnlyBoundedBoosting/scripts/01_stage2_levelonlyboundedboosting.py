#!/usr/bin/env python3
"""Stage 2 candidate `j_levelOnlyBoundedBoosting` (batch 14): the minimal input and the bounded correction together.

**Why.** `h_levelOnlyBoosting` and `i_boundedBoosting` each change one axis of
`g_oosErrorBoosting` and each scored better than it in the stability run. Whether the two
gains add, overlap or interfere is not known from either alone and was not a row of the
frozen v1 manifest; this candidate is the combination. It is also the row the
pre-registered main-path rule (plan section 4b, 2026-09-21) was written before seeing.

**Everything else is `g_oosErrorBoosting`'s**: the target (stage 1's h-step in-window
out-of-sample error from every origin after the warm-up, parameters fixed, standardised by
stage 1's own se and winsorised at +/-3), the pooling across provinces, the gradient-boosted
family and its fixed configuration, the seed, the clip at zero, sigma unchanged, and the
horizon set read from the evaluation scheme. That node's script and provenance carry the
argument for each; this one changes the feature set and the correction bound together.

**How it is computed.** Through `lib.stage2_perturb.run_combination` -- the parametrised
pipeline the stability node built and verified in batch 12 (its `main` configuration
reproduces `g_oosErrorBoosting`'s 408 per-cell rows value for value) -- with this candidate's
configuration. A candidate node that reuses a verified pipeline instead of re-implementing it
is the point of having verified it; the configuration is the whole content of this script.

**Verification (Rule 1)**, as every stage-2 sibling: the stage-1 forecast this run derives is
compared cell for cell with `02_stage1`'s stored `per_cell_scores.csv` before the result is
trusted, and the script refuses to write if they disagree beyond tolerance.

**Seeds (Rule 6)**: `random_state = component_seed("04_stage2/g_oosErrorBoosting")`, the same
seed as the main path it varies, so the difference between the two is the configuration alone
(the stability run showed an alternative seed moves g's margin by 0.1 points).
"""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/j_levelOnlyBoundedBoosting
ANALYSIS = NODE.parents[1]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.stage2_perturb import Stage1Config, SchemeConfig, Stage2Config, run_combination  # noqa: E402

DEV_CSV = ANALYSIS / "01_data" / "01_prepare" / "results" / "development.csv"
STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
RESULTS = NODE / "results"
VERIFY_ATOL = 1e-6

STAGE2 = Stage2Config(features="level_only", bounded_correction=True, bound_floor=10.0)


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    per_cell, conclusion = run_combination(dev_rows, Stage1Config(), SchemeConfig(), STAGE2)

    with STAGE1_CELLS_CSV.open(newline="") as f:
        ref = {(r["province"], r["split"], r["month"]): r for r in csv.DictReader(f)}
    n_verified, max_dm, max_ds = 0, 0.0, 0.0
    for c in per_cell:
        r = ref.get((c["province"], str(c["split"]), c["month"]))
        if r is None or r["fit_failed"] != "False" or c["fit_failed"]:
            continue
        max_dm = max(max_dm, abs(c["stage1_mean"] - float(r["forecast_mean"])))
        max_ds = max(max_ds, abs(c["stage1_se"] - float(r["forecast_se"])))
        n_verified += 1
    if n_verified == 0 or max_dm > VERIFY_ATOL or max_ds > VERIFY_ATOL:
        raise RuntimeError(f"stage-1 forecast disagrees with 02_stage1's stored output: n={n_verified}, "
                           f"max|dmean|={max_dm:.3e}, max|dse|={max_ds:.3e} -- refusing to write")

    RESULTS.mkdir(exist_ok=True)
    fields = ["province", "split", "month", "h", "actual", "stage1_mean", "stage1_se", "stage2_correction",
              "final_mean", "final_se", "crps_stage1", "crps", "fit_failed", "error"]
    with (RESULTS / "per_cell_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(per_cell)
    summary = {
        "model": "stage1 SARIMAX(1,1,1)x(1,0,0,12) + gradient-boosted trees on the standardised h-step in-window out-of-sample error, level-only features; correction zhat*se bounded to |correction| <= max(stage-1 mean, 10), clipped at zero; sigma unchanged",
        "stage2_config": asdict(STAGE2),
        **{k: v for k, v in conclusion.items() if k != "config"},
        "mean_crps": conclusion["two_stage"]["mean_crps"],
        "verification_vs_stage1_stored_forecast": {"n_cells_verified": n_verified, "max_abs_diff_mean": max_dm,
                                                   "max_abs_diff_se": max_ds, "tolerance": VERIFY_ATOL},
    }
    (RESULTS / "conclusion.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("model", "mean_crps", "stage1_alone", "two_stage", "pct_change_vs_stage1",
                                              "n_splits_improved", "verification_vs_stage1_stored_forecast")}, indent=2))


if __name__ == "__main__":
    main()
