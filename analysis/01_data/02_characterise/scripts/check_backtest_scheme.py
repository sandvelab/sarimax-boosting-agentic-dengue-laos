#!/usr/bin/env python3
"""Fix the backtest scheme, and check it with chap-core's own splitter and filter.

Three things have to be established before any model is built, because a horizon
changed later makes every earlier number incomparable:

  1. Which provinces survive `validate_and_filter_dataset_for_evaluation`. It drops a
     location whose target is entirely missing over the *training* portion, so what
     the headline mean is a mean over is a property of the data and the scheme
     together, not something to be assumed.
  2. What each candidate (n_periods, n_splits, stride) actually evaluates on the
     development file -- the span, the first training window, and how many cells the
     metric ends up averaging.
  3. That the phase-E arrangement puts the evaluated span exactly on 2010.

The third is checked on a **synthetic calendar** -- 18 provinces over 1998-01 to
2010-12 carrying placeholder values -- not on the archived original. The question is
about the split schedule, which depends only on the period range, so answering it
does not require opening the holdout, and the holdout is not opened here.

Both the filter and the splitter are chap-core's own functions, called directly. The
schedule is read off what they return rather than recomputed from the formula in
their docstrings.

Seeds: none. The splitter is a deterministic index calculation and the placeholder
values are constants, so the project seed 20260822 has no surface here.

Usage:  "$PYTHON" scripts/check_backtest_scheme.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from chap_core.assessment.dataset_splitting import train_test_generator
from chap_core.rest_api.db_worker_functions import validate_and_filter_dataset_for_evaluation
from chap_core.spatio_temporal_data.temporal_dataclass import DataSet

NODE = Path(__file__).resolve().parent.parent
DEV = NODE.parent / "01_partition" / "results" / "development_1998-01_2009-12.csv"
RESULTS = NODE / "results"

N_PERIODS = 3
CANDIDATES = [(3, 4, 3), (3, 8, 3), (3, 12, 3), (3, 4, 1), (3, 8, 1), (3, 12, 1), (3, 7, 1)]
CHOSEN = (3, 8, 3)
PHASE_E = (3, 4, 3)
FULL_LAST = "2010-12"


def periods_of(ds: DataSet) -> list[str]:
    """`YYYY-MM`, so periods sort and compare the way the CSV's own column does.
    chap-core's Month renders as `Month(2009-9)`, which sorts lexically wrong."""
    return [f"{p.year:04d}-{p.month:02d}" for p in ds.period_range]


def filter_report(ds: DataSet, n_periods: int, n_splits: int, stride: int) -> dict:
    before = sorted(ds.keys())
    after = sorted(validate_and_filter_dataset_for_evaluation(
        ds, target_name="disease_cases", n_periods=n_periods,
        n_splits=n_splits, stride=stride).keys())
    return {
        "locations_before": len(before),
        "locations_after": len(after),
        "rejected": ",".join(sorted(set(before) - set(after))) or "-",
    }


def schedule(ds: DataSet, n_periods: int, n_splits: int, stride: int) -> list[dict]:
    """The actual split windows, read from what chap-core's generator returns."""
    train_set, splits = train_test_generator(
        ds, prediction_length=n_periods, n_test_sets=n_splits, stride=stride)
    train_periods = periods_of(train_set)
    rows = []
    for i, (historic, _masked, future) in enumerate(splits):
        hp, fp = periods_of(historic), periods_of(future)
        rows.append({
            "split": i,
            "train_set_last_period": train_periods[-1],
            "historic_first": hp[0], "historic_last": hp[-1], "historic_months": len(hp),
            "predicted_first": fp[0], "predicted_last": fp[-1], "predicted_months": len(fp),
        })
    return rows


def synthetic_calendar(template: pd.DataFrame, last_period: str) -> DataSet:
    """A dataset over the full 1998-01 to `last_period` calendar, carrying placeholder
    values. Built by extending the development file's period index, never by reading
    the archived original: only the period range affects a split schedule."""
    locations = sorted(template["location"].unique())
    months = [str(p) for p in pd.period_range(
        template["time_period"].min(), last_period, freq="M")]
    frame = pd.DataFrame(
        [{"location": loc, "time_period": m, "disease_cases": 0.0, "population": 1,
          "rainfall": 0.0, "mean_temperature": 0.0, "mean_relative_humidity": 0.0}
         for loc in locations for m in months])
    return DataSet.from_pandas(frame)


def evaluable_cells(frame: pd.DataFrame, kept: list[str],
                    first: str, last: str, n_periods: int) -> pd.DataFrame:
    """How many cells the metric can actually average over the evaluated span.

    `cells = locations x splits x horizons` is the nominal figure. Missing observations
    are dropped before the metric is computed, so a province that stopped reporting
    contributes nothing however many splits are run, and the headline mean is a mean
    over fewer provinces than the filter left standing."""
    window = frame[(frame["location"].isin(kept))
                   & (frame["time_period"] >= first) & (frame["time_period"] <= last)]
    g = window.groupby(["location", "location_name"], as_index=False).agg(
        months_in_span=("disease_cases", "size"),
        target_observed=("disease_cases", "count"),
    )
    g["target_missing"] = g["months_in_span"] - g["target_observed"]
    # Each observed month is predicted once per split-set when stride == n_periods.
    g["evaluable_cells"] = g["target_observed"]
    g["contributes_to_metric"] = g["evaluable_cells"] > 0
    return g.sort_values("evaluable_cells", ascending=False).reset_index(drop=True)


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    dev_frame = pd.read_csv(DEV, dtype={"time_period": str})
    dev = DataSet.from_csv(str(DEV))
    dev_periods = periods_of(dev)

    rows = []
    for n_periods, n_splits, stride in CANDIDATES:
        span = n_periods + (n_splits - 1) * stride
        sched = schedule(dev, n_periods, n_splits, stride)
        filt = filter_report(dev, n_periods, n_splits, stride)
        evaluated = sorted({p for s in sched for p in (s["predicted_first"], s["predicted_last"])})
        rows.append({
            "n_periods": n_periods, "n_splits": n_splits, "stride": stride,
            "evaluation_span_months": span,
            "evaluated_first": evaluated[0], "evaluated_last": evaluated[-1],
            "train_set_last_period": sched[0]["train_set_last_period"],
            "training_months_before_first_split": sched[0]["historic_months"],
            "splits_overlap": stride < n_periods,
            "cells_metric_averages":
                filt["locations_after"] * n_splits * n_periods,
            **filt,
            "is_chosen": (n_periods, n_splits, stride) == CHOSEN,
        })
    candidates = pd.DataFrame(rows)
    candidates.to_csv(RESULTS / "backtest_scheme_candidates.csv", index=False)

    chosen_sched = pd.DataFrame(schedule(dev, *CHOSEN))
    chosen_sched.insert(0, "dataset", "development")
    calendar = synthetic_calendar(dev_frame, FULL_LAST)
    phase_e_sched = pd.DataFrame(schedule(calendar, *PHASE_E))
    phase_e_sched.insert(0, "dataset", "synthetic full calendar (phase-E arrangement)")
    pd.concat([chosen_sched, phase_e_sched], ignore_index=True).to_csv(
        RESULTS / "split_schedule.csv", index=False)

    e_first = phase_e_sched["predicted_first"].min()
    e_last = phase_e_sched["predicted_last"].max()
    chosen = {
        "development_scheme": dict(zip(("n_periods", "n_splits", "stride"), CHOSEN)),
        "phase_e_scheme": dict(zip(("n_periods", "n_splits", "stride"), PHASE_E)),
        "n_retrain": 1,
        "development_evaluated_span": [
            chosen_sched["predicted_first"].min(), chosen_sched["predicted_last"].max()],
        "development_train_set_last_period": chosen_sched["train_set_last_period"].iloc[0],
        "development_periods_available": len(dev_periods),
        "phase_e_evaluated_span": [e_first, e_last],
        "phase_e_train_set_last_period": phase_e_sched["train_set_last_period"].iloc[0],
        "phase_e_span_is_exactly_2010": [e_first, e_last] == ["2010-01", "2010-12"],
        "phase_e_training_never_reaches_2010":
            phase_e_sched["train_set_last_period"].iloc[0] == "2009-12",
        "locations_evaluated": int(
            candidates.loc[candidates["is_chosen"], "locations_after"].iloc[0]),
        "locations_rejected_by_filter":
            candidates.loc[candidates["is_chosen"], "rejected"].iloc[0],
        "cells_metric_averages_development": int(
            candidates.loc[candidates["is_chosen"], "cells_metric_averages"].iloc[0]),
    }
    kept = sorted(validate_and_filter_dataset_for_evaluation(
        dev, target_name="disease_cases", n_periods=CHOSEN[0],
        n_splits=CHOSEN[1], stride=CHOSEN[2]).keys())
    cells = evaluable_cells(dev_frame, kept, *chosen["development_evaluated_span"], CHOSEN[0])
    cells.to_csv(RESULTS / "evaluable_cells_by_province.csv", index=False)
    chosen["cells_metric_averages_development_effective"] = int(cells["evaluable_cells"].sum())
    chosen["locations_contributing_to_metric"] = int(cells["contributes_to_metric"].sum())
    chosen["locations_kept_by_filter_but_contributing_nothing"] = ",".join(
        cells.loc[~cells["contributes_to_metric"], "location"]) or "-"

    (RESULTS / "backtest_scheme_chosen.json").write_text(json.dumps(chosen, indent=2) + "\n")

    print(f"chosen (n_periods, n_splits, stride) = {CHOSEN}")
    print(f"development evaluates {chosen['development_evaluated_span']}, "
          f"trained through {chosen['development_train_set_last_period']}")
    print(f"phase E evaluates {chosen['phase_e_evaluated_span']}, "
          f"exactly 2010: {chosen['phase_e_span_is_exactly_2010']}")
    print(f"locations evaluated: {chosen['locations_evaluated']}, "
          f"rejected: {chosen['locations_rejected_by_filter']}")
    print(f"cells: {chosen['cells_metric_averages_development']} nominal, "
          f"{chosen['cells_metric_averages_development_effective']} with an observed target, "
          f"over {chosen['locations_contributing_to_metric']} provinces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
