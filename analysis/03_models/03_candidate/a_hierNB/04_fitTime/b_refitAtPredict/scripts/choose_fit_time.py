"""Stage 4 of the candidate's configuration: whether fitting happens in train or predict.

**In predict.** The model is refitted inside every predict call, on the whole
expanding historic window Chap hands it, so a forecast made at the last split is made
by a model that has seen every month up to that split rather than only the training
period.

This is what the reference model does. `chapkit_ewars_model` fits its INLA model inside
its predict endpoint, so at every split of the backtest it is using more data than a
train-time fit of ours is. Under the main path that difference sits inside the
comparison unmeasured; this child is what measures it, and that is the fork's whole
reason for existing.

What it costs: one fit per split instead of one fit per backtest, and a model that is
a different model at every split -- so "the fitted object" is no longer a single thing
the record can point at, and what `train` writes is a stub that says so. The premise
records how much history the main path is leaving on the table, which is the size of
the effect this child is looking for.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path



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

    setup, input_combo = resolve(
        ROOT / "analysis/02_setup/results", "setup_spec.json")
    flags = json.loads(setup.read_text())["eval_flags"]

    premise = {
        "n_retrain": flags["n_retrain"],
        "n_splits": flags["n_splits"],
        "n_periods": flags["n_periods"],
        "stride": flags["stride"],
        # What the main path does not use. chap-core hands predict an expanding
        # historic window whether or not the model looks at it.
        "months_of_history_the_train_time_fit_never_sees_at_the_last_split":
            (flags["n_splits"] - 1) * flags["stride"],
        "fits_per_backtest": flags["n_splits"],
        "matches_what_the_reference_model_does": True,
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "fit_time",
        "order": 4,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_refitAtPredict",
        "description": "refit inside every predict call on the expanded history",
        "user_option_values": {"fit_time": "predict"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"fitTime/b_refitAtPredict[{COMBO}]: refit at predict, "
          f"{premise['fits_per_backtest']} fits per backtest, recovering "
          f"{premise['months_of_history_the_train_time_fit_never_sees_at_the_last_split']} "
          f"months of history the main path ignores -> {out}")



if __name__ == "__main__":
    main()
