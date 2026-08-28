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
pool, and the shape is a property of the tree: how many Chap contract directories there are
and which of them are the plan's required baselines. The prediction is registered here in
words, and `../../scripts/check_pool.py` measures it afterwards against the members' own
stored evaluations, which is where a number about a member belongs.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

import json
import os
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")
MODELS = ROOT / "analysis" / "03_models"
POOL = NODE.parents[1]


def members() -> list[str]:
    """The models the pool will contain, as node paths, from the shape of the tree.

    The same glob `prepare_members.py` uses, for the same reason: a list here would be a
    second statement of what models this project has. Nothing is read from any of them --
    this is a count and a set of paths, so that the prediction below can say what share of
    the pool the plan's required baselines will carry.
    """
    return sorted(
        str(p.parent.parents[1].relative_to(ROOT))
        for p in MODELS.glob("**/scripts/*/MLproject")
        if POOL not in p.parents)


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    pool = members()
    baselines = [n for n in pool if "01_baselines" in n]

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
            "source": ("the shape of the tree: every Chap contract directory under "
                       "analysis/03_models except the pool's own"),
            "members": pool,
            "member_count": len(pool),
            "weight_each_member_will_carry": 1.0 / len(pool),
            "required_baselines_among_them": baselines,
            "share_of_the_pool_on_the_required_baselines": len(baselines) / len(pool),
            "nothing_downstream_is_read": (
                "no score, no leaderboard, no evaluation. This node runs before "
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
          f"{len(baselines)} of them required baselines -> {out}")


if __name__ == "__main__":
    main()
