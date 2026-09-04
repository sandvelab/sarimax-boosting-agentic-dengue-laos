"""Rebuild the pool from its members' own stored evaluations, and test the registered premise.

Two checks, both of the kind batch 10 argued for: written to a file, computed by a script,
and comparing something predicted before the run against something measured after it.

## 1. The pool, reconstructed by a second path

The ensemble scored better than any of its members, and a claim of that shape deserves more
than one route to it. So this script rebuilds the pool **from the members' own stored
`eval.nc` files** — the evaluations produced when each member was run on its own, through
its own node — pools their samples at the weights this run fitted, and scores the result
with chap-core's own CRPS. Nothing of the ensemble's own forecast is used.

The two paths should agree closely and cannot agree exactly. The members inside the pool
are the same code fitted on the same frames from the same seeds, so their draws are the
same draws; but the pool takes a seeded subsample of each member's thousand, and the
reconstruction here takes a different one. What is left is the sampling error of the pool's
own allocation, which is what the difference measures.

**A member's evaluation is matched by configuration, and named by rule.** Each member is
paired with a stored evaluation whose `configuration_sha256`, dataset and backtest flags
are the ones the pool used — so the check never compares the pool against a differently
configured version of one of its own members, which is the mistake a combination-name
lookup would make silently. Several combinations usually carry such a run, all of them the
same model on the same data, and **which one is named is decided by `combos.implies` and
not by which directories exist**: this combination's own run of the member where there is
one, and otherwise the run that moved the fewest forks among the combinations this one
implies. Batch 28 made it so, after the previous tie-break — the first hit of a glob over
sibling directories — was found to record the order in which batches happened to execute.

**A member has no such run at all where the fork that moved is inside that member**, and
then the reconstruction is not done: nothing in the tree evaluated candidate 1 on its own
under, say, the zero-inflated observation model, because the main path pools it. That is a
property of the perturbation manifest and it does not change with time. What does depend on
time is *when* a member's own run appears — the family rows are stability rows, so on a
cold run of `analysis/run.sh` they land long after the main path's pool has been checked.
So the last step of `05_stability/run.sh` runs this script again for every combination
whose members have since been evaluated (`scripts/reconstruct_pools.py`), and the file this
one leaves behind is the same whether the tree was built in one run or in thirty-one
batches.

## 2. The registered premise of the weighting child that ran

Each child of `01_weighting` writes a prediction into its `model_option_spec.json` before
anything is fitted. This script reads it back and evaluates it against the fitted weights,
the members' scores and the pool's, and records which parts of it held.

Writes, under results/$COMBO/:
  pool_check.json   the reconstruction, the members' scores by one path, and the premise
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from chap_core.assessment.evaluation import Evaluation
from chap_core.assessment.metrics import get_metric

NODE = Path(__file__).resolve().parents[1]

#: How a member's evaluation was chosen, written into the file beside the evaluation it
#: names. Two clauses, in order; see `matching_evaluation`.
THIS_COMBINATION = "this combination's own run of the member"
FEWEST_FORKS = ("the fewest forks moved among the combinations this one implies, "
                "ties broken by name")


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")
CELL = ["location", "time_period"]

sys.path.insert(0, str(NODE / "scripts" / "ensemble_model"))
from ensemble import allocate, pool  # noqa: E402

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import implies, tokens  # noqa: E402


def flat(evaluation: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts = Evaluation.from_file(evaluation).to_flat()
    return pd.DataFrame(parts.forecasts), pd.DataFrame(parts.observations)


def sample_block(forecasts: pd.DataFrame) -> pd.DataFrame:
    """(location, time_period) x sample, sorted, so two members can be stacked."""
    wide = forecasts.pivot_table(index=CELL, columns="sample", values="forecast")
    return wide.sort_index(axis=0).sort_index(axis=1)


def stored_evaluations(member: dict, wanted: dict) -> list[str]:
    """Every combination under which this member has been evaluated as the pool has it.

    The configuration's hash, the dataset's hash and the backtest flags, all three, and an
    evaluation file to read. Sorted by name, so the list is the same list whatever order
    the directories were written in. Which of them is *named* is `matching_evaluation`'s
    decision; this is only the set it decides over, and `05_stability` writes the whole set
    into `results/pool_reconstruction.json` once every row has run.
    """
    node = ROOT / member["node"]
    found = []
    for spec_path in sorted(node.glob("results/*/model_spec.json")):
        spec = json.loads(spec_path.read_text())
        if (spec.get("configuration_sha256") == member["model_config_sha256"]
                and spec.get("dataset_sha256") == wanted["dataset_sha256"]
                and spec.get("eval_flags") == wanted["eval_flags"]
                and (spec_path.parent / "eval.nc").exists()):
            found.append(spec_path.parent.name)
    return found


def matching_evaluation(member: dict, wanted: dict,
                        combination: str) -> tuple[Path | None, str, str]:
    """A stored evaluation of this member under the configuration the pool used.

    Matched on the configuration's hash, the dataset's hash and the backtest flags rather
    than on a combination name. A member evaluated under a different configuration is a
    different model, and comparing the pool with it would make this check say nothing
    while looking like it said something.

    Those three fields usually admit more than one run — the same model, on the same data,
    stored under every combination that left it alone — and the one to name is decided
    here, by the combination names alone:

    1. **this combination's own run of the member**, where there is one. A pool row that
       also evaluated its member separately is compared against that;
    2. otherwise the run that **moved the fewest forks among the combinations this one
       implies** (`combos.implies`), ties broken by name. Fewest forks is the member's own
       canonical run: `main` for a baseline the pool did not perturb, `family_hierNB` for
       candidate 1, `provinces_reportingOnly__holdout` for a baseline under a combination
       that moved the province filter and the weighting.

    Both are functions of the two names and the tree, so the answer does not move when an
    unrelated combination is run. Returns the directory, its combination, and the clause
    above that chose it; `(None, "", reason)` when nothing matches, where the reason is
    empty if no run of this member exists under this configuration at all and says so if
    runs exist but this combination implies none of them.
    """
    node = ROOT / member["node"]
    found = stored_evaluations(member, wanted)
    if not found:
        return None, "", ""
    if combination in found:
        return node / "results" / combination, combination, THIS_COMBINATION
    implied = [name for name in found if implies(combination, name)]
    if not implied:
        return None, "", "runs exist, but under combinations this one does not imply"
    chosen = min(implied, key=lambda name: (len(tokens(name)), name))
    return node / "results" / chosen, chosen, FEWEST_FORKS


def why_not(unmatched: list[str], outside: list[str]) -> str | None:
    """Why the reconstruction was skipped, distinguishing its two causes.

    A member with no stored run under this configuration anywhere is the ordinary case and
    a permanent one. A member whose only stored runs are under combinations this one does
    not imply would be the tie-break refusing to reach across the manifest for a number; it
    happens in no combination of this tree, and it is named separately so that it would not
    arrive disguised as the ordinary case.
    """
    if not unmatched:
        return None
    never = [name for name in unmatched if name not in outside]
    parts = []
    if never:
        parts.append(f"no stored evaluation of {never} under the configuration the pool "
                     f"gave them")
    if outside:
        parts.append(f"the only stored evaluations of {outside} are under combinations "
                     f"this one does not imply")
    return "; ".join(parts) + "; the reconstruction needs every member's own run"


def main() -> None:
    out = NODE / "results" / COMBO
    specification = json.loads((out / "candidate_spec.json").read_text())
    fitted = json.loads((out / "fitted_model.json").read_text())
    ours = json.loads((out / "model_spec.json").read_text())
    membership = json.loads((out / "members.json").read_text())["members"]
    weights = np.asarray([m["weight"] for m in fitted["members"]], dtype=float)
    names = [m["name"] for m in fitted["members"]]

    # --- 1. the reconstruction -------------------------------------------------------
    blocks, sources, unmatched, outside = [], {}, [], []
    index = None
    for member in membership:
        directory, combination, chosen_by = matching_evaluation(member, ours, COMBO)
        if directory is None:
            # The member has not been evaluated on its own under the configuration the
            # pool gave it -- which, for a combination that moves a fork inside that
            # member, no run of this tree ever does. It is a fact about the manifest and
            # not a fault in the pool, so it is recorded and the reconstruction is
            # skipped; the premise check below does not depend on it.
            unmatched.append(member["name"])
            if chosen_by:
                outside.append(member["name"])
            continue
        forecasts, observations = flat(directory / "eval.nc")
        wide = sample_block(forecasts)
        blocks.append(wide)
        index = wide.index if index is None else index.intersection(wide.index)
        sources[member["name"]] = {
            "evaluation": str((directory / "eval.nc").relative_to(ROOT)),
            "combination": combination,
            "chosen_by": chosen_by,
            "configuration_sha256": member["model_config_sha256"],
            "cells": int(len(wide)), "draws": int(wide.shape[1])}

    # Only the cells with an observed count are scorable, and the platform's own
    # evaluation drops the rest; the reconstruction has to be over the same cells as the
    # score it is being compared with, or it is a mean over a different denominator.
    own_forecasts, own_observations = flat(out / "eval.nc")
    observed = own_observations.dropna(subset=["disease_cases"]).set_index(CELL)
    if unmatched:
        index = observed.index.sort_values()
        blocks = []
    else:
        index = index.intersection(observed.index).sort_values()

    stack = (np.stack([b.loc[index].to_numpy(float) for b in blocks]) if blocks
             else np.empty((0, len(index), 0)))
    truth = observed.loc[index, "disease_cases"].to_numpy(float)
    horizon = (own_forecasts.drop_duplicates(CELL)
               .set_index(CELL).loc[index, "horizon_distance"].to_numpy(int))

    seed = specification["user_option_values"]["seed"]

    def score(draws: np.ndarray) -> dict:
        long = pd.DataFrame({
            "location": np.repeat([i[0] for i in index], draws.shape[1]),
            "time_period": np.repeat([i[1] for i in index], draws.shape[1]),
            "horizon_distance": np.repeat(horizon, draws.shape[1]),
            "sample": np.tile(np.arange(draws.shape[1]), len(index)),
            "forecast": draws.reshape(-1)})
        observations = pd.DataFrame({
            "location": [i[0] for i in index],
            "time_period": [i[1] for i in index],
            "disease_cases": truth})
        values = {}
        for metric_id in ("crps", "coverage_10_90", "coverage_25_75"):
            detailed = get_metric(metric_id)().get_detailed_metric(observations, long)
            values[metric_id] = float(detailed["metric"].mean())
            values["cells"] = int(len(detailed))
        return values

    def flat_interval_share(draws: np.ndarray) -> dict:
        """How often the model's own quantiles coincide, per nominal interval.

        A count distribution on this dataset carries an atom at zero -- 56 % of observed
        province-months are exactly zero -- and a model that puts more than three
        quarters of its mass there has a 25-75 interval of [0, 0]. Every zero outcome
        then falls inside it, so interval coverage at the 50 % level is bounded below by
        something the model cannot choose, and reading it as calibration would credit or
        blame a model for the shape of the target. The 10-90 level is far less exposed to
        it. This measures the exposure rather than assuming it away.
        """
        shares = {}
        for name, (low, high) in {"25_75": (25, 75), "10_90": (10, 90)}.items():
            lower, upper = np.percentile(draws, [low, high], axis=1)
            shares[name] = float((upper <= lower).mean())
        return shares

    if unmatched:
        rebuilt_score, member_scores, member_coverage = None, {}, {}
    else:
        rebuilt = pool(stack, weights, np.random.default_rng(seed), stack.shape[2])
        rebuilt_score = score(rebuilt)
        # One scoring pass per member: `score` computes all three metrics together and
        # nothing in it is random, so asking twice returned the same numbers twice.
        by_member = {name: score(stack[m]) for m, name in enumerate(names)}
        member_scores = {name: value["crps"] for name, value in by_member.items()}
        member_coverage = {name: value["coverage_10_90"]
                           for name, value in by_member.items()}

    # The pool as it actually ran, scored here from its own stored evaluation over the
    # same cells. Every number in this file therefore comes from one path over one set of
    # cells; `04_score` is the node that reports, and it has not run yet when this does.
    own = sample_block(own_forecasts).loc[index].to_numpy(float)[None, :, :]
    as_run_score = score(own[0])
    as_run = as_run_score["crps"]

    # --- 2. the registered premise ---------------------------------------------------
    stage = specification["stages"][0]
    order = sorted(member_scores, key=member_scores.get)
    baselines = [n for n, m in zip(names, membership) if "01_baselines" in m["node"]]
    candidates = [n for n in names if n not in baselines]
    weight_of = dict(zip(names, weights.tolist()))

    premise = {
        "child": stage["choice"],
        "registered_before_the_run": stage["what_the_premise_implies"],
        "fitted_weights": weight_of,
        "members_ranked_on_the_evaluated_period": order,
        "weight_on_the_candidate_families": sum(weight_of[n] for n in candidates),
        "weight_on_the_required_baselines": sum(weight_of[n] for n in baselines),
        "smallest_weight": min(weight_of.values()),
        "members_below_weight_0.05": [n for n, w in weight_of.items() if w < 0.05],
        "pool_mean_crps": as_run,
        "best_member_mean_crps": member_scores[order[0]] if order else None,
        "mean_of_member_mean_crps": (float(np.mean(list(member_scores.values())))
                                     if member_scores else None),
        "pool_beats_its_best_member_by": (member_scores[order[0]] - as_run
                                          if order else None),
        "pool_coverage_10_90": as_run_score["coverage_10_90"],
        "pool_coverage_25_75": as_run_score["coverage_25_75"],
        "member_coverage_10_90": member_coverage,
        "largest_member_coverage_10_90": (max(member_coverage.values())
                                          if member_coverage else None),
        "nominal_coverage_10_90": 0.80,
        "nominal_coverage_25_75": 0.50,
    }
    # What the weighting *did*, not what the combination asked for. `b_crpsWeighted` fits
    # weights on a block held back inside the training frame, and `run_ensemble.py` falls
    # back to equal weights when the frame is too short to hold one back -- recording
    # `fell_back` and its reason when it does. Keying this on `stage["choice"]` therefore
    # asked for a validation block that was never written, and the row died with a
    # KeyError: batch 25's clean-room run selected `trainingWindow_from2004__
    # weighting_crpsWeighted`, where a window starting in 2004 leaves 36 months to refit
    # members that require 60, and lost the row. It is the fork-blindness batch 14 found
    # four times -- a script keyed on the configuration rather than on the outcome.
    #
    # The fallback is reported rather than passed over in silence, because a combination
    # whose weighting fork could not take effect is a duplicate of its other fork wearing
    # a pair's name, and that is worth seeing in the pool's own check.
    # The two new keys are written only on the fallback path, which no archived
    # combination takes -- so every `pool_check.json` in the repository comes back
    # byte-identical. Batch 26 exists to make `analysis/run.sh` reproduce its own archive;
    # spending that on an extra field in 51 unrelated files would be a poor trade, and the
    # weighting method is already recorded in `fitted_model.json` beside this.
    weighting = fitted["weighting"]
    if weighting.get("fell_back"):
        premise["weighting_fell_back_to_equal"] = weighting.get("fell_back_because")
        premise["validation_gain_over_equal_weights"] = None
    elif "validation" in weighting:
        validation = weighting["validation"]
        premise["validation_gain_over_equal_weights"] = (
            validation["pooled_crps_at_equal_weights"]
            - validation["pooled_crps_at_fitted_weights"])

    document = {
        "combo": COMBO,
        "node": str(NODE.relative_to(ROOT)),
        "weighting": fitted["weighting"]["method"],
        "weights": weight_of,
        "reconstruction": {
            "what_it_is": ("the pool rebuilt from the members' own stored evaluations, "
                           "pooled at the same weights and scored with chap-core's own "
                           "CRPS; independent of the ensemble's own forecast"),
            "member_evaluations": sources,
            "members_without_a_matching_stored_evaluation": unmatched,
            "not_done_because": why_not(unmatched, outside),
            "cells_in_common": int(len(index)),
            "mean_crps_rebuilt": rebuilt_score["crps"] if rebuilt_score else None,
            "mean_crps_as_run": as_run,
            "difference": (rebuilt_score["crps"] - as_run) if rebuilt_score else None,
            "why_they_cannot_be_identical": (
                "the members' draws are the same draws -- same code, same frames, same "
                "seeds -- but the pool takes a seeded subsample of each member's "
                "thousand and this reconstruction takes a different one, so what is "
                "left is the sampling error of the allocation"),
            "allocation": dict(zip(names, allocate(weights, own.shape[2]).tolist())),
        },
        "member_mean_crps_by_this_path": member_scores,
        "share_of_cells_where_the_interval_is_a_point": {
            "what_it_is": ("the share of evaluated cells at which the model's own "
                           "quantiles coincide, so that the interval is [0, 0] and every "
                           "zero outcome falls inside it whatever the model believes. "
                           "56 % of this dataset's observed province-months are exactly "
                           "zero, so the 25-75 coverage figure is bounded below by this "
                           "and is not a clean reading of calibration; the 10-90 figure "
                           "is the one to read"),
            "pool": flat_interval_share(own[0]),
            **({name: flat_interval_share(stack[m]) for m, name in enumerate(names)}
               if not unmatched else {}),
        },
        "premise": premise,
    }
    (out / "pool_check.json").write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")

    print(f"pool check[{COMBO}]: "
          + (f"rebuilt {rebuilt_score['crps']:.3f} against {as_run:.3f} as run "
             f"(difference {rebuilt_score['crps'] - as_run:+.3f}); members "
             + ", ".join(f"{n} {member_scores[n]:.3f}" for n in order)
             if rebuilt_score else
             f"{as_run:.3f} as run; reconstruction not done, no stored evaluation of "
             f"{unmatched} under the configuration the pool gave them")
          + f" -> {out / 'pool_check.json'}")


if __name__ == "__main__":
    main()
