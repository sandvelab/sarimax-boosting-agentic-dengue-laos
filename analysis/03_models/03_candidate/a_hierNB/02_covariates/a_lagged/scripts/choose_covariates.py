"""Stage 2 of the candidate's configuration: which climate covariates, at which lag.

Rainfall and mean temperature, each entering the linear predictor at a **two-month lag**,
standardised on whatever period the model is fitted on. Mean relative humidity is in the
file and is left out here.

Where the choice comes from, since it is not ours: the reference model this project is
measured against publishes a configuration for this country -- `laos_eval_config.yaml` in
`chap-models/ewars_plus_template` -- naming exactly these two covariates and a lag of two
months. Taking the same pair at the same lag makes our candidate's first configuration a
comparable one rather than a differently-tuned one, and leaves the question of whether a
richer covariate set helps to this node's siblings, which is where it can be answered by
running them rather than argued about.

Two months is also what the development data supports: `01_data/02_characterise` measured
the lagged rank correlation between each covariate and the counts, and the climate signal
in this dataset is not sharp enough for a lag chosen to the month to mean much.

The siblings: `b_rich` (all three covariates at lags one, two and three) and
`c_climateFree` (no climate at all, so that the seasonal term alone carries the annual
cycle). The third is the one worth stating plainly -- if a climate-free model scores the
same, the covariates are decoration, and that is a finding about the dataset rather than
about the model.

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

# The covariate names and the lag. They are the choice this node *is*, not values carried
# in from another step: the reference's published configuration is the source and it is
# named in the specification this script writes.
COVARIATES = ("rainfall", "mean_temperature")
LAGS = (2,)


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

    dataset, dataset_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})

    missing = [c for c in COVARIATES if c not in frame.columns]
    if missing:
        raise SystemExit(f"the assembled dataset has no column(s) {missing}; this child "
                         f"cannot be taken on combination {COMBO!r}")

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": dataset_combo,
        "stage": "covariates",
        "order": 2,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_lagged",
        "description": (f"{', '.join(COVARIATES)} at a "
                        f"{', '.join(str(l) for l in LAGS)}-month lag, standardised"),
        "user_option_values": {
            "covariates": list(COVARIATES),
            "covariate_lags": list(LAGS),
        },
        # What chap-core is told to hand the model beyond the template's required set.
        "additional_continuous_covariates": list(COVARIATES),
        "source_of_the_choice": (
            "chap-models/ewars_plus_template, laos_eval_config.yaml: the reference "
            "family's own published configuration for this country names rainfall and "
            "mean_temperature at n_lags 2"),
        "premise": {
            "columns_present": list(COVARIATES),
            "columns_left_out": [c for c in ("mean_relative_humidity",)
                                 if c in frame.columns],
            "missing_values": {c: int(frame[c].isna().sum()) for c in COVARIATES},
            "rows": int(len(frame)),
        },
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"covariates/a_lagged[{COMBO}]: {', '.join(COVARIATES)} at lag(s) "
          f"{list(LAGS)}; missing values {spec['premise']['missing_values']} -> {out}")


if __name__ == "__main__":
    main()
