"""Stage 2 of candidate 2's configuration: a ladder of quantile boosters.

Fifteen boosters, each fitted to a different quantile of log1p(count) under the pinball
loss, made monotone and inverted at a uniform draw. Where the sibling derives the width of
a forecast from its level, this head learns it: nothing ties the fifteen fits together, so
a cell the boosters place confidently gets a narrow ladder and a cell they do not gets a
wide one, whatever their means.

**This is the head batch 4 named as where this family fails**, and the premise below is
where the reason is registered — before the run, so that what the score says afterwards can
be read against a prediction rather than against a story told after the fact.

## The prediction being registered

A quantile booster starts from the marginal quantile of its target and moves off it by
splitting on residuals. Where the target is a count and a large share of the counts are
**exactly zero**, every level below that share starts at zero, and at every zero-valued row
the residual is exactly zero — the kink of the pinball loss, where the gradient carries no
information about which way to move. The boosters at those levels have nothing to descend
and stay at zero for every province, including provinces that never report a zero at all.

So the prediction is arithmetic, not a guess: **the ladder is flat at zero for every level
below the zero share of the target**, and the premise records that share and counts how
many of the fifteen levels fall under it. If the prediction is right, the lower part of
every forecast distribution collapses onto zero and the head is badly calibrated for
exactly the high-burden provinces the headline mean is most sensitive to.

The prediction is registered rather than pre-emptively repaired. The repair — a separate
model for whether the month reports at all, with the ladder fitted only to the months that
do — is the construction candidate 1's `01_observation` fork calls a hurdle, and it would
be a third child of this fork rather than a change to this one. A child quietly rebuilt
until it worked would leave the tree with no record that the plain construction does not.

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

# The ladder the model fits. Kept here as well as in the model so that the premise can
# count how many of these levels the zero share is predicted to strand, which is the whole
# point of computing the premise before the run.
QUANTILES = (0.01, 0.05, 0.10, 0.20, 0.25, 0.30, 0.40, 0.50,
             0.60, 0.70, 0.75, 0.80, 0.90, 0.95, 0.99)


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
    counts = pd.to_numeric(frame["disease_cases"], errors="coerce").dropna()
    zero_share = float((counts == 0).mean())

    # Which provinces the prediction bites hardest for: the ones that never report a zero
    # and whose forecasts would therefore be given a lower half they can never realise.
    never_zero = sorted(
        str(location) for location, block in frame.groupby("location")
        if (y := pd.to_numeric(block["disease_cases"], errors="coerce").dropna()).size
        and not (y == 0).any())

    stranded = [q for q in QUANTILES if q < zero_share]

    spec = {
        "combo": COMBO,
        "input_from_combo": dataset_combo,
        "stage": "head",
        "order": 2,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_quantileEnsemble",
        "description": (f"{len(QUANTILES)} boosters, one per quantile of log1p(count), "
                        f"made monotone and inverted at a uniform draw"),
        "user_option_values": {"head": "quantile_ensemble"},
        "additional_continuous_covariates": [],
        "premise": {
            "rows": int(len(frame)),
            "target_observed": int(len(counts)),
            "target_zero_share": zero_share,
            "quantile_levels": list(QUANTILES),
            "levels_below_the_zero_share": stranded,
            "n_levels_below_the_zero_share": len(stranded),
            "n_levels": len(QUANTILES),
            "provinces_that_never_report_a_zero": never_zero,
            "marginal_quantiles_of_the_target": {
                str(q): float(counts.quantile(q)) for q in QUANTILES},
        },
        # Registered before the run. `AGENTS.md` §4 asks for the alternatives considered
        # and the basis; this is the same discipline applied to what a child is expected
        # to do, so that the run confirms or refutes something rather than merely
        # producing a number.
        "predicted_before_the_run": (
            f"{len(stranded)} of the {len(QUANTILES)} ladder levels sit below the "
            f"target's zero share of {zero_share:.3f}. A pinball loss at those levels "
            f"starts at the marginal quantile — zero — and finds a residual of exactly "
            f"zero at {zero_share:.0%} of rows, where its gradient is at the kink and "
            f"says nothing about direction. Those levels are predicted to stay flat at "
            f"zero for every province, so the lower "
            f"{100 * max(stranded, default=0):.0f} % of every forecast distribution "
            f"collapses onto zero — including for "
            f"{len(never_zero)} province(s) that never report one."),
    }
    (out / "model_option_spec.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"head/b_quantileEnsemble[{COMBO}]: zero share {zero_share:.3f}; "
          f"{len(stranded)} of {len(QUANTILES)} ladder levels predicted flat at zero; "
          f"{len(never_zero)} province(s) never report a zero -> {out}")


if __name__ == "__main__":
    main()
