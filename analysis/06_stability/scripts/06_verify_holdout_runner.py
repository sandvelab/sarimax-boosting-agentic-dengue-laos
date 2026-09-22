#!/usr/bin/env python3
"""Gate the phase-E machinery on development data, before the manifest that will use it is
frozen and long before the held-out year is opened.

**Why this runs in batch 16 and not in batch 17.** Plan §3 lets the holdout be opened once.
If the code that opens it is also the code being debugged, the first failure is repaired with
a number from the held-out year already on screen, and the second run is no longer the first
opening. So every line phase E will execute is written and checked here, against results this
repository already has, and the only thing batch 17 adds is the file.

**What is checked.** `lib/holdout_eval.py` is run in *development mode* -- the development
rows, the development scheme (`n_splits=8`, `stride=3`) -- and its output is compared value
for value with what is already stored in the tree:

1. the two-stage pipeline at the main path's configuration against
   `04_stage2/h_levelOnlyBoosting/results/per_cell_scores.csv` (the same 408-row gate the
   development combination runner passes);
2. persistence against `03_baselines/01_persistence/results/per_cell_scores.csv`;
3. seasonal climatology against `03_baselines/02_climatology/results/per_cell_scores.csv`.

(2) and (3) are the ones that matter most: they are a second implementation of forecasts whose
first implementation cannot read another file, and nothing but this comparison says the two
agree.

**What is also checked**: that every row `holdout_combinations()` names is constructible, that
the holdout scheme resolves over the combined 1998-01..2010-12 span to the four 2010 blocks it
is meant to (from the month index alone -- no case value is read), and that the frozen province
set is development's seventeen.

Nothing here opens `01_data/01_prepare/results/holdout.csv`. The span check reads the holdout
file's `time_period` column only, as `01_data/03_backtest_scheme` reads development's.

Seeds: none drawn; the gradient-boosted comparison seeds from the project seed inside
`lib.stage2_perturb`, exactly as the stored result did.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/06_stability
ANALYSIS = NODE.parents[0]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.holdout_eval import (  # noqa: E402
    HOLDOUT_SCHEME, MAIN_CONFIG, SUFFIX, climatology, development_provinces,
    holdout_combinations, persistence, two_stage,
)
from lib.backtest import rolling_splits  # noqa: E402
from lib.stage2_perturb import SchemeConfig, Stage1Config  # noqa: E402

RESULTS = NODE / "results"
PREPARE = ANALYSIS / "01_data" / "01_prepare" / "results"
DEV_CSV = PREPARE / "development.csv"
HOLDOUT_CSV = PREPARE / "holdout.csv"
MAIN_CELLS = ANALYSIS / "04_stage2" / "h_levelOnlyBoosting" / "results" / "per_cell_scores.csv"
PERSISTENCE_CELLS = ANALYSIS / "03_baselines" / "01_persistence" / "results" / "per_cell_scores.csv"
CLIMATOLOGY_CELLS = ANALYSIS / "03_baselines" / "02_climatology" / "results" / "per_cell_scores.csv"

TWO_STAGE_COLUMNS = ["province", "split", "month", "h", "actual", "stage1_mean", "stage1_se",
                     "stage2_correction", "final_mean", "final_se", "crps"]
BASELINE_COLUMNS = ["province", "split", "month", "actual", "forecast_mean", "forecast_se", "crps"]


def compare(ours: list[dict], stored: Path, columns: list[str]) -> dict:
    with stored.open(newline="") as f:
        theirs = list(csv.DictReader(f))
    mine = [{k: ("" if r.get(k) is None else str(r[k])) for k in columns} for r in ours]
    yours = [{k: r[k] for k in columns} for r in theirs]
    mismatches = [(i, k, a[k], b[k]) for i, (a, b) in enumerate(zip(mine, yours))
                  for k in columns if a[k] != b[k]]
    return {"compared_with": str(stored.relative_to(ANALYSIS.parent)), "n_rows_ours": len(mine),
            "n_rows_stored": len(yours), "n_mismatched_values": len(mismatches),
            "identical_on_shared_columns": bool(len(mine) == len(yours) and not mismatches),
            "first_mismatches": mismatches[:5]}


def holdout_span() -> dict:
    """What the frozen scheme resolves to over the combined span. Reads month labels only."""
    with DEV_CSV.open(newline="") as f:
        dev_months = sorted({r["time_period"] for r in csv.DictReader(f)})
    with HOLDOUT_CSV.open(newline="") as f:
        holdout_months = sorted({r["time_period"] for r in csv.DictReader(f)})
    months = sorted(set(dev_months) | set(holdout_months))
    splits = rolling_splits(months, HOLDOUT_SCHEME.n_periods, HOLDOUT_SCHEME.n_splits,
                            HOLDOUT_SCHEME.stride)
    evaluated = sorted({m for s in splits for m in s["test_months"]})
    return {"n_months_combined": len(months), "combined_span": [months[0], months[-1]],
            "n_periods": HOLDOUT_SCHEME.n_periods, "n_splits": HOLDOUT_SCHEME.n_splits,
            "stride": HOLDOUT_SCHEME.stride,
            "splits": [{"split": s["split"], "train_start": s["train_months"][0],
                        "train_end": s["train_months"][-1], "n_train_months": len(s["train_months"]),
                        "test_months": s["test_months"]} for s in splits],
            "evaluated_months": evaluated,
            "covers_the_holdout_year_exactly_once": evaluated == holdout_months}


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    dev_scheme = SchemeConfig()  # the development scheme: 8 splits, stride 3

    # Each check is timed: its wall-clock on the development scheme is the only measured cost
    # the holdout manifest has for a row with no development counterpart (the two baselines).
    checks: dict[str, dict] = {}
    t_all = time.perf_counter()
    for name, run, stored, columns in (
        ("two_stage_main_path", lambda: two_stage(dev_rows, dev_rows, Stage1Config(), dev_scheme, MAIN_CONFIG),
         MAIN_CELLS, TWO_STAGE_COLUMNS),
        ("baseline_persistence", lambda: persistence(dev_rows, dev_rows, dev_scheme),
         PERSISTENCE_CELLS, BASELINE_COLUMNS),
        ("baseline_climatology", lambda: climatology(dev_rows, dev_rows, dev_scheme),
         CLIMATOLOGY_CELLS, BASELINE_COLUMNS),
    ):
        t0 = time.perf_counter()
        per_cell, _ = run()
        checks[name] = {**compare(per_cell, stored, columns),
                        "wall_seconds_on_development": round(time.perf_counter() - t0, 1)}

    combos = holdout_combinations()
    malformed = [name for name, spec in combos.items()
                 if not ((spec[0] == "baseline" and callable(spec[1]))
                         or (len(spec) == 3 and isinstance(spec[0], Stage1Config)
                             and isinstance(spec[1], SchemeConfig)))]
    provinces = development_provinces(dev_rows, HOLDOUT_SCHEME.min_modelable_months)
    report = {
        "verified_on": "development data only; no holdout case value is read by this script",
        "development_scheme": {"n_periods": dev_scheme.n_periods, "n_splits": dev_scheme.n_splits,
                               "stride": dev_scheme.stride},
        "reproduction_checks": checks,
        "all_reproductions_identical": all(c["identical_on_shared_columns"] for c in checks.values()),
        "row_set": {"n_rows": len(combos), "suffix": SUFFIX, "rows": sorted(combos),
                    "malformed_rows": malformed, "all_constructible": not malformed},
        "frozen_province_set": {"n_provinces": len(provinces), "provinces": provinces},
        "holdout_schedule": holdout_span(),
        "wall_seconds": round(time.perf_counter() - t_all, 1),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "holdout_runner_verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("row_set", "frozen_province_set")},
                     indent=2))
    if malformed:
        raise RuntimeError(f"rows with no executable configuration: {malformed}")
    if not report["all_reproductions_identical"]:
        raise RuntimeError("the phase-E machinery does not reproduce the stored development "
                           "results; it must not be frozen into a manifest")
    if not report["holdout_schedule"]["covers_the_holdout_year_exactly_once"]:
        raise RuntimeError("the holdout scheme does not resolve to the held-out months exactly once")


if __name__ == "__main__":
    main()
