"""Stage 4 of the candidate's configuration: whether fitting happens in train or predict.

In train. The model is fitted once, on the training period Chap hands to the `train`
entry point, and `predict` applies the stored fit -- reading the expanded historic frame
only for the covariate lags a forecast month needs, never to re-estimate anything.

What is being given up is stated plainly: chap-core hands `predict` an expanding historic
window at every split, so by the last split of the development backtest there are two more
years of observations than the fit ever saw, and this child ignores them. The sibling
`b_refitAtPredict` uses them, at the cost of a fit per split and of being a different
model at each split. The reference model refits inside predict, which is one reason its
scores and ours are not comparable in the way two fits of the same model would be -- and
that is the fork's whole point.

The choice interacts with an evaluation flag that is **not** ours to set here.
`02_setup/04_retrain` decides `n-retrain`, and "fit once" only means what it says while
that flag is 1. This script therefore reads the assembled evaluation flags and records
the value it actually ran under, so a combination that moved `n-retrain` cannot silently
leave this specification claiming something that is no longer true.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the flag it depends on
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

    setup, setup_combo = resolve(
        ROOT / "analysis/02_setup/results", "setup_spec.json")
    flags = json.loads(setup.read_text())["eval_flags"]

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": setup_combo,
        "stage": "fit_time",
        "order": 4,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_trainOnly",
        "description": "fit once in train; predict applies the stored fit",
        "user_option_values": {"fit_time": "train"},
        "additional_continuous_covariates": [],
        "premise": {
            "n_retrain": flags["n_retrain"],
            "one_fit_serves_every_split": flags["n_retrain"] == 1,
            "n_splits": flags["n_splits"],
            "n_periods": flags["n_periods"],
            "months_of_history_the_fit_never_sees_at_the_last_split":
                (flags["n_splits"] - 1) * flags["stride"],
        },
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"fitTime/a_trainOnly[{COMBO}]: fit in train, n_retrain {flags['n_retrain']}, "
          f"{spec['premise']['months_of_history_the_fit_never_sees_at_the_last_split']} "
          f"months of later history unused -> {out}")


if __name__ == "__main__":
    main()
