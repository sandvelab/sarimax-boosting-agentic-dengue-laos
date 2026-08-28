"""Stage 1 of candidate 3's configuration: the weights that minimise the pooled CRPS.

The members' predictive distributions are pooled linearly, as in the sibling, but the
weights are the point on the simplex at which the pool's own CRPS is smallest on a
validation period **held back from inside the training frame**. Nothing from the period
the backtest scores is used, and nothing from the leaderboard reaches the model: the
weights are estimated inside `train`, from data the model was going to be fitted on
anyway, and re-estimated wherever the backtest refits.

**Why minimum-CRPS rather than something proportional to a member's score.** Weights
proportional to `1/CRPS` are the obvious construction and they are almost inert here: the
members' scores span roughly 21 to 25, so the inverse-score weights would run from about
0.22 to 0.27 and the pool would be an equal pool with a rounding error -- the fork would
then measure nothing, and would say so only after the compute had been spent. The
minimum-CRPS pool is the standard construction (Gneiting and Ranjan's optimal linear
pool) and it can put a member at zero, which is what makes it a genuinely different
answer from the sibling rather than a perturbation of it.

**It is computed exactly, not searched for.** For a sample-based forecast the CRPS is
`E|X - y| - 0.5 E|X - X'|`, so for a pool `F = sum_m w_m F_m` it is

    CRPS(w) = sum_m w_m A_m  -  0.5 * w' B w,
    A_m   = E_{F_m}|X - y|,        B_mk = E|X_m - X'_k|,

with `A` and `B` averaged over the validation cells. That is a quadratic in `w` whose
coefficients are means of absolute differences between stored draws, and it is convex on
the simplex because the matrix of expected absolute differences is conditionally negative
definite. So the weights are the solution of a small convex problem rather than the output
of a search whose stopping point would be another judgment call.

**The one judgment call, logged rather than forked.** How much of the training frame is
held back: four three-month blocks, one per forecast block, matching the horizon the
backtest asks for and the arithmetic `02_setup` fixed. A validation period shorter than
the horizon would fit weights for a problem the model is not asked to solve; a longer one
would take more of the training data away from the members whose weights are being fitted.
Four is the smallest number of blocks that gives each member more than one block to be
wrong in. `AGENTS.md` §3 allows a judgment call to be a node or a logged decision; this is
the second, and it is logged here, in the node's claim and in the provenance record.

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

# The validation period held back inside the training frame, in forecast blocks of the
# length the backtest uses. Read from 02_setup rather than written as a number of months,
# so a combination that changed the horizon would move this with it.
VALIDATION_BLOCKS = 4

# Draws per member per validation cell used to form A and B. The members produce 1 000;
# the pairwise term is quadratic in that count, and 200 draws put the Monte Carlo error
# of each entry of B two orders of magnitude below the differences between members that
# the weights turn on. Reduced deliberately and recorded, rather than being whatever ran
# fast enough.
WEIGHT_SAMPLES = 200


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

    setup_path, setup_combo = resolve(
        ROOT / "analysis/02_setup/results", "setup_spec.json")
    setup = json.loads(setup_path.read_text())
    horizon = int(setup["eval_flags"]["n_periods"])

    dataset, _ = resolve(ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})
    periods = sorted(frame["time_period"].unique())

    # What the weights will be fitted on, stated in periods rather than in months, so the
    # record says which part of the file the pool is allowed to learn its weights from.
    held_back = VALIDATION_BLOCKS * horizon
    counts = pd.to_numeric(frame["disease_cases"], errors="coerce")
    validation_rows = frame[frame["time_period"].isin(periods[-held_back:])]

    spec = {
        "combo": COMBO,
        "input_from_combo": setup_combo,
        "stage": "weighting",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_crpsWeighted",
        "description": ("the weights on the simplex that minimise the pool's own CRPS "
                        "on a validation period held back from inside the training "
                        "frame; computed exactly from the sample-based CRPS identity"),
        "user_option_values": {
            "weighting": "min_crps",
            "validation_blocks": VALIDATION_BLOCKS,
            "weight_samples": WEIGHT_SAMPLES,
        },
        "additional_continuous_covariates": [],
        "premise": {
            "source": str(setup_path.relative_to(ROOT)),
            "forecast_horizon_months": horizon,
            "validation_blocks": VALIDATION_BLOCKS,
            "validation_months_held_back": held_back,
            # The whole file's last periods; inside a backtest split the training frame
            # ends earlier, and the same arithmetic is applied to whatever frame `train`
            # is handed. These figures describe the shape of the hold-back, not the rows
            # any one fit will see.
            "file_last_period": periods[-1],
            "file_periods": len(periods),
            "validation_cells_at_file_end": int(len(validation_rows)),
            "target_zero_share_whole_file": float(
                (counts.fillna(-1) == 0).sum() / max(int(counts.notna().sum()), 1)),
            "weight_samples_per_member_per_cell": WEIGHT_SAMPLES,
            "objective": "mean over validation cells of sum_m w_m A_m - 0.5 w' B w",
        },
        # Registered before the run, and checked afterwards by
        # ../../scripts/check_weight_premise.py against the fitted weights.
        "what_the_premise_implies": (
            "the minimum-CRPS pool is a corner-seeking solution: it is predicted to put "
            "at least one member at a weight below 0.05, which the sibling cannot do at "
            "all. It is predicted to place more weight on the two candidate families "
            "than on the two required baselines. And because the weights are fitted on "
            "the last few blocks of the training frame while the score is taken on the "
            "blocks after it, the fitted weights are predicted to be a worse guide to "
            "the evaluated period than to the validation period -- so the pool is "
            "predicted to beat the equal pool by less than the difference between them "
            "on the validation period"),
    }
    (out / "model_option_spec.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"weighting/b_crpsWeighted[{COMBO}]: minimum-CRPS weights on "
          f"{VALIDATION_BLOCKS} blocks of {horizon} months held back inside the training "
          f"frame, {WEIGHT_SAMPLES} draws per member per cell -> {out}")


if __name__ == "__main__":
    main()
