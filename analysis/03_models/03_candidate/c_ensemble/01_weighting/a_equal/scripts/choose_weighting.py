"""Stage 1 of candidate 3's configuration: every member of the pool weighs the same.

The pool is a linear opinion pool -- the members' predictive distributions averaged, not
their point forecasts. With equal weights it is told nothing at all about how well its
members forecast, which is the whole content of this child: **no weight in this model is
a quantity estimated from data**, so there is no route by which the pool can overfit the
period it is scored on, and no weight that has to be defended as having been fitted
honestly. That is what a default looks like when the alternative is an estimate.

What it buys and what it costs are both structural, and both were written down here before
the model ran. A linear pool's variance is the average of its members' variances *plus*
the spread between their means, so pooling widens the forecast whether or not that is
wanted; every model of ours before candidate 2 under-covered, so widening is the direction
the project's calibration errors have mostly pointed. Against that, equal weights put as
much of the pool on the two required baselines as on the two candidates, and the baselines
are the two worst models on the board.

**The premise below reads the leaderboard; the model does not.** What the members scored on
the development backtest is already a reported result of this project, and reading it to
register a prediction about what the pool will do is analysis. It would be something else
entirely to let one of those numbers set a weight -- which is exactly what the sibling
does, from a validation period held back inside the training frame rather than from these
figures.

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

    board_path, board_combo = resolve(
        ROOT / "analysis/04_score/03_compare/results", "leaderboard.csv")
    board = pd.read_csv(board_path)
    ours = board[board.origin == "ours"].sort_values("mean_crps")
    scores = {str(row.model): float(row.mean_crps) for row in ours.itertuples()}

    spec = {
        "combo": COMBO,
        "input_from_combo": board_combo,
        "stage": "weighting",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_equal",
        "description": ("every member of the pool carries weight 1/M; no weight in this "
                        "model is estimated from data"),
        "user_option_values": {"weighting": "equal"},
        "additional_continuous_covariates": [],
        "premise": {
            "source": str(board_path.relative_to(ROOT)),
            "members_are_weighted_by_this": False,
            "development_mean_crps_of_our_models": scores,
            "best_of_ours": min(scores, key=scores.get) if scores else None,
            "worst_of_ours": max(scores, key=scores.get) if scores else None,
            "spread_best_to_worst": (max(scores.values()) - min(scores.values())
                                     if scores else None),
            "coverage_10_90_of_our_models": {
                str(row.model): float(row.coverage_10_90) for row in ours.itertuples()},
            "nominal_coverage_10_90": 0.80,
        },
        # Registered before the run, and checked afterwards by
        # ../../scripts/check_weight_premise.py against what the pool actually scored.
        "what_the_premise_implies": (
            "an equally weighted pool puts half its mass on the two required baselines, "
            "which are the two worst-scoring models of ours, so it is predicted to score "
            "worse than the best member and better than the mean of the members; and "
            "because a linear pool's variance is the mean of its members' variances plus "
            "the spread between their means, its 10-90 coverage is predicted to be at "
            "least the largest of its members' -- that is, wider than any member, and so "
            "over-covering if any member already over-covers"),
    }
    (out / "model_option_spec.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")

    order = " < ".join(f"{name} {value:.3f}" for name, value in
                       sorted(scores.items(), key=lambda kv: kv[1]))
    print(f"weighting/a_equal[{COMBO}]: equal weights, nothing estimated; "
          f"members on the board {order} -> {out}")


if __name__ == "__main__":
    main()
