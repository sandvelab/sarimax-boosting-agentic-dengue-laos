"""Stage 2 of the candidate's configuration: which climate covariates, at which lags.

**All three climate columns, each at one, two and three months' lag** -- nine
standardised columns rather than the main path's two. The position is that the
covariate set and the lag are not knowledge this project has, so they should be
estimated rather than borrowed: the fit is penalised on the province and province-year
effects but not on these coefficients, so a lag that carries nothing gets a small
coefficient rather than being excluded by a decision made in advance.

What it costs is in the premise. Every extra lag drops the rows at the start of each
province's record where that lag falls before the data begins, and every extra column
is a coefficient estimated on the same 2 040 rows. This child is where over-fitting
would show up first, and the held-out year is what would catch it -- which is the
project's own warning about selecting hard on development CRPS, applied to itself.

The main path `a_lagged` takes the reference family's published Lao configuration --
rainfall and mean temperature at lag two. The sibling `c_climateFree` takes none.

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

# Every column the file carries, at every lag a monthly transmission signal could
# plausibly take. They are the choice this node *is*, not values carried in from
# another step.
COVARIATES = ("rainfall", "mean_temperature", "mean_relative_humidity")
LAGS = (1, 2, 3)



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

    missing = {c: int(frame[c].isna().sum()) for c in COVARIATES if c in frame.columns}
    absent = [c for c in COVARIATES if c not in frame.columns]
    if absent:
        raise SystemExit(f"the assembled dataset has no column(s) {absent}; this child "
                         f"cannot be taken on combination {COMBO!r}")

    premise = {
        "columns_present": list(COVARIATES),
        "lags": list(LAGS),
        "design_columns_added": len(COVARIATES) * len(LAGS),
        "missing_values": missing,
        "rows": int(len(frame)),
        "provinces": int(frame["location"].nunique()),
        # The longest lag decides how much of each province's record is unusable, so
        # this is what the richer covariate set costs in observations.
        "rows_lost_to_the_longest_lag": int(frame["location"].nunique() * max(LAGS)),
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "covariates",
        "order": 2,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_rich",
        "description": "all three climate columns at lags 1, 2 and 3, standardised",
        "user_option_values": {"covariates": list(COVARIATES), "covariate_lags": list(LAGS)},
        "additional_continuous_covariates": list(COVARIATES),
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"covariates/b_rich[{COMBO}]: {len(COVARIATES)} covariates x {len(LAGS)} lags "
          f"= {premise['design_columns_added']} columns; missing values {missing} -> {out}")



if __name__ == "__main__":
    main()
