"""Stage 1 of the candidate's configuration: the observation model for the counts.

A **zero-inflated negative binomial**: with probability pi a province-month reports
nothing whatever the transmission process did, and with probability 1 - pi it is a
draw from the same negative binomial the main path uses. pi is estimated by the EM
step inside the fit, not set here, so this child's claim is testable by running it --
if pi comes out near zero the mixture has answered the fork against itself.

The position it takes is that some of this record's zeros are **reporting** zeros. The
premise below is the evidence available for that without assuming it: a province-year
in which nothing at all was reported is a different object from a quiet month inside a
year that reported, and the two are counted separately. Neither count proves a
reporting process exists -- no column in this dataset distinguishes a true zero from
an unreturned form -- which is exactly why this is a fork and not a correction.

The main path `a_negBinomial` says one stretched distribution carries both the zeros
and the over-dispersion; the sibling `c_hurdle` says reporting and magnitude are two
processes with their own regressions rather than one process with a mixing weight.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]



def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import resolve  # noqa: E402


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    dataset, input_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})

    counts = frame["disease_cases"].dropna()
    per_year = (frame.dropna(subset=["disease_cases"])
                .assign(year=lambda f: f["time_period"].str[:4])
                .groupby(["location", "year"])["disease_cases"])
    silent_years = per_year.sum() == 0
    in_silent_year = per_year.transform("sum") == 0

    premise = {
        "observed_cells": int(len(counts)),
        "zero_share": float((counts == 0).mean()),
        # A zero inside a year the province did report in is the kind of zero a
        # stretched count distribution explains comfortably. A zero inside a year with
        # no reported case at all is the kind a mixture is posited for.
        "province_years": int(len(silent_years)),
        "province_years_with_nothing_reported": int(silent_years.sum()),
        "zeros_in_a_year_with_nothing_reported":
            int(((counts == 0) & in_silent_year.reindex(counts.index)).sum()),
        "zeros_in_a_year_that_did_report":
            int(((counts == 0) & ~in_silent_year.reindex(counts.index)).sum()),
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "observation",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_zeroInflated",
        "description": "negative binomial mixed with a point mass at zero; the mixing weight is fitted",
        "user_option_values": {"observation": "zero_inflated"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"observation/b_zeroInflated[{COMBO}]: zero_inflated; "
          f"{premise['province_years_with_nothing_reported']} of "
          f"{premise['province_years']} province-years reported nothing -> {out}")



if __name__ == "__main__":
    main()
