#!/usr/bin/env python3
"""Check that the Lao schemes put the sibling backtests where the mirror requires.

The external check is only a mirror of the Lao result if the two arrangements land on the
same months on all three countries. The schemes themselves do not move -- batch 3 fixed
3/8/3 and 3/4/3 and said a horizon changed midway makes every earlier number incomparable
-- so what has to be established here is that applied to the sibling files they evaluate
2008-01 to 2009-12 and exactly 2010, from training sets that stop before each.

That is not automatic. chap-core lays its splits out backwards from the last period of the
file, so it depends on where each file ends, and on which provinces its own filter keeps:
`validate_and_filter_dataset_for_evaluation` drops a location whose target is entirely
missing over the training portion, and how many it drops is a property of the data.

Both the filter and the splitter are chap-core's own functions, called directly, exactly
as `02_characterise/scripts/check_backtest_scheme.py` calls them for Laos. The schedule is
read off what they return rather than recomputed from a formula.

Writes:
  backtest_scheme_external.json   the scheme, span and cell count for each of the four
                                  sibling datasets, in the shape `analysis/scripts/lib/
                                  combos.py` reads
  split_schedule_external.csv     every split window, per dataset
  evaluable_cells_external.csv    per province, how many cells it contributes

Seeds: none. The splitter is a deterministic index calculation.

Usage:  "$PYTHON" scripts/check_external_scheme.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from chap_core.assessment.dataset_splitting import train_test_generator
from chap_core.rest_api.db_worker_functions import validate_and_filter_dataset_for_evaluation
from chap_core.spatio_temporal_data.temporal_dataclass import DataSet

NODE = Path(__file__).resolve().parent.parent
ROOT = NODE.parents[2]
RESULTS = NODE / "results"
LAO_SCHEME = ROOT / "analysis/01_data/02_characterise/results/backtest_scheme_chosen.json"

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
import combos  # noqa: E402

#: The four sibling datasets, in the names `combos` gives them, and which of the two Lao
#: schemes each mirrors. The file each one reads is `combos`'s answer and not a constant
#: here, so a dataset cannot be checked under one file and run under another.
DATASETS = {
    "tha": "development_scheme",
    "thaFinal": "phase_e_scheme",
    "vnm": "development_scheme",
    "vnmFinal": "phase_e_scheme",
}


def periods_of(ds: DataSet) -> list[str]:
    """`YYYY-MM`, so periods sort and compare the way the CSV's own column does."""
    return [f"{p.year:04d}-{p.month:02d}" for p in ds.period_range]


def schedule(ds: DataSet, n_periods: int, n_splits: int, stride: int) -> list[dict]:
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


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    lao = json.loads(LAO_SCHEME.read_text())

    out: dict[str, object] = {
        "what_this_is": (
            "the two schemes batch 3 fixed, applied to the sibling datasets and checked "
            "against chap-core's own splitter and filter. The schemes are not re-chosen "
            "here; what is established is where they land on these calendars"),
        "schemes_read_from": str(LAO_SCHEME.relative_to(ROOT)),
        "n_retrain": lao["n_retrain"],
    }
    schedules, cells_rows = [], []

    for name, lao_key in DATASETS.items():
        scheme = lao[lao_key]
        n_periods, n_splits, stride = (
            scheme["n_periods"], scheme["n_splits"], scheme["stride"])
        source = combos.source_dataset(ROOT, f"main__{name}" if name != "development" else "main")
        frame = pd.read_csv(source, dtype={"time_period": str})
        ds = DataSet.from_csv(str(source))

        before = sorted(ds.keys())
        after = sorted(validate_and_filter_dataset_for_evaluation(
            ds, target_name="disease_cases", n_periods=n_periods,
            n_splits=n_splits, stride=stride).keys())
        sched = pd.DataFrame(schedule(ds, n_periods, n_splits, stride))
        sched.insert(0, "dataset", name)
        schedules.append(sched)

        first = sched["predicted_first"].min()
        last = sched["predicted_last"].max()
        observed = frame.dropna(subset=["disease_cases"])
        in_span = observed[(observed["time_period"] >= first)
                           & (observed["time_period"] <= last)]
        per_province = in_span.groupby(
            ["location", "location_name"], as_index=False).size().rename(
            columns={"size": "evaluable_cells"})
        per_province.insert(0, "dataset", name)
        cells_rows.append(per_province)

        out[f"{name}_scheme"] = {
            "n_periods": n_periods, "n_splits": n_splits, "stride": stride}
        out[f"{name}_evaluated_span"] = [first, last]
        out[f"{name}_train_set_last_period"] = sched["train_set_last_period"].iloc[0]
        out[f"{name}_detail"] = {
            "source": str(source.relative_to(ROOT)),
            "mirrors_lao_scheme": lao_key,
            "mirrors_lao_span": lao[
                "development_evaluated_span" if lao_key == "development_scheme"
                else "phase_e_evaluated_span"],
            "span_matches_lao": [first, last] == lao[
                "development_evaluated_span" if lao_key == "development_scheme"
                else "phase_e_evaluated_span"],
            "periods_available": len(periods_of(ds)),
            "locations_in_file": len(before),
            "locations_evaluated": len(after),
            "locations_rejected_by_filter": ",".join(sorted(set(before) - set(after))) or "-",
            "cells_metric_averages_nominal": len(after) * n_splits * n_periods,
            "cells_metric_averages_effective": int(len(in_span)),
            "locations_contributing_to_metric": int(in_span["location"].nunique()),
            "training_never_reaches_the_evaluated_span":
                bool(sched["train_set_last_period"].iloc[0] < first),
        }

    pd.concat(schedules, ignore_index=True).to_csv(
        RESULTS / "split_schedule_external.csv", index=False)
    pd.concat(cells_rows, ignore_index=True).to_csv(
        RESULTS / "evaluable_cells_external.csv", index=False)
    (RESULTS / "backtest_scheme_external.json").write_text(json.dumps(out, indent=2) + "\n")

    for name in DATASETS:
        d = out[f"{name}_detail"]
        print(f"{name:9s} {out[f'{name}_scheme']} evaluates {out[f'{name}_evaluated_span']} "
              f"(matches Laos: {d['span_matches_lao']}), trained through "
              f"{out[f'{name}_train_set_last_period']}, "
              f"{d['locations_evaluated']}/{d['locations_in_file']} provinces, "
              f"{d['cells_metric_averages_effective']} cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
