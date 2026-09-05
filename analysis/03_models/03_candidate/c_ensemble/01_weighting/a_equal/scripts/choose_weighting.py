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

**The premise below reads nothing downstream of this node.** An earlier version of it read
`04_score`'s leaderboard, to say in the specification what the members had scored. That was
a model node depending on a scoring node -- the same shape of error as a result that has no
provenance, and it failed the moment the node was run under a combination whose scoring
chain had not run. What the premise needs is not the members' scores but the *shape* of the
pool: how many members there are and which of them are the plan's required baselines. The
prediction is registered here in words, and `../../scripts/check_pool.py` measures it
afterwards against the members' own stored evaluations, which is where a number about a
member belongs.

**With equal weights, that shape is the whole model.** The member count is the weight each
member carries; the share of the members that are required baselines is the share of the
pool's mass sitting on the two worst models on the board, which is exactly what the
registered prediction below is about. So getting the membership wrong is not getting a
description wrong -- it is registering a prediction about a different model.

**Which is why the membership is not computed here.** It comes from
`03_models/scripts/lib/pool_shape.py`, the same call `prepare_members.py` builds the pool
from a few seconds later. This file used to run its own glob over contract directories,
which was the same answer until batch 22 gave the persistence baseline and the climatology
baseline a second published construction each. From then until batch 32 it recorded **six
members at 1/6 each with two-thirds of the mass on required baselines**, where **four at
1/4** ran, and both statements were printed by the same run three lines apart. No score
moved -- nothing in `user_option_values` depends on the count -- but the model's registered
prediction rested on a premise the same file contradicted, and it contradicted itself:
`share_of_the_pool_on_the_required_baselines` said two-thirds while the prediction beneath
it said half.

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

sys.path.insert(0, str(ROOT / "analysis" / "03_models" / "scripts" / "lib"))
import pool_shape  # noqa: E402


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    rows = pool_shape.selection()
    pool = pool_shape.members(rows)
    baselines = pool_shape.required_baselines(pool)
    elsewhere = pool_shape.not_members(rows)

    spec = {
        "combo": COMBO,
        "input_from_combo": COMBO,
        "stage": "weighting",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_equal",
        "description": ("every member of the pool carries weight 1/M; no weight in this "
                        "model is estimated from data"),
        "user_option_values": {"weighting": "equal"},
        "additional_continuous_covariates": [],
        "premise": {
            "source": ("the shape of the tree, by analysis/03_models/scripts/lib/"
                       "pool_shape.py: every Chap contract directory under "
                       "analysis/03_models except the pool's own, with every "
                       "alternatives fork above one resolved to the child this "
                       "combination takes. It is the same call prepare_members.py "
                       "builds the pool from, so the pool this specification is about "
                       "and the pool that runs are one answer and not two"),
            "members": pool,
            "member_count": len(pool),
            "weight_each_member_will_carry": 1.0 / len(pool),
            "required_baselines_among_them": baselines,
            "share_of_the_pool_on_the_required_baselines": len(baselines) / len(pool),
            # The contracts the glob found that this combination's pool does not contain:
            # the constructions of a member that this combination did not take. Recorded
            # because a premise that says only what is in the pool cannot be read against
            # what the tree holds, and reading those two against each other is what would
            # have caught this file's own defect at any point in the ten days it stood.
            "contracts_not_on_this_combinations_path": elsewhere,
            "nothing_downstream_is_read": (
                "no score, no leaderboard, no evaluation. Resolving a fork reads the "
                "model specifications of models that run before this node -- the same "
                "lookup prepare_members.py uses a few seconds later, and answered by "
                "the fork's own main path where nothing has run. This node runs before "
                "04_score, and a model node that read a scoring node would be a "
                "circular dependency that only shows up when the scoring node has not "
                "run yet"),
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

    print(f"weighting/a_equal[{COMBO}]: equal weights, nothing estimated; "
          f"{len(pool)} members at {1 / len(pool):.3f} each, "
          f"{len(baselines)} of them required baselines"
          + (f"; not on this combination's path: {elsewhere}" if elsewhere else "")
          + f" -> {out}")


if __name__ == "__main__":
    main()
