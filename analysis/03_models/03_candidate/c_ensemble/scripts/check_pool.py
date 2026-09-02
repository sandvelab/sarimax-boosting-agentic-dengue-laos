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

**A member's evaluation is matched by configuration, not by combination.** Each member is
paired with a stored evaluation whose `configuration_sha256`, dataset and backtest flags
are the ones the pool used — so the check fails loudly if it is about to compare the pool
against a differently configured version of one of its own members, which is exactly the
mistake a combination-name lookup would make silently.

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


def flat(evaluation: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts = Evaluation.from_file(evaluation).to_flat()
    return pd.DataFrame(parts.forecasts), pd.DataFrame(parts.observations)


def sample_block(forecasts: pd.DataFrame) -> pd.DataFrame:
    """(location, time_period) x sample, sorted, so two members can be stacked."""
    wide = forecasts.pivot_table(index=CELL, columns="sample", values="forecast")
    return wide.sort_index(axis=0).sort_index(axis=1)


def matching_evaluation(member: dict, wanted: dict) -> tuple[Path, str]:
    """A stored evaluation of this member under the configuration the pool used.

    Matched on the configuration's hash, the dataset's hash and the backtest flags rather
    than on a combination name. A member evaluated under a different configuration is a
    different model, and comparing the pool with it would make this check say nothing
    while looking like it said something.
    """
    node = ROOT / member["node"]
    found = []
    for spec_path in sorted(node.glob("results/*/model_spec.json")):
        spec = json.loads(spec_path.read_text())
        if (spec.get("configuration_sha256") == member["model_config_sha256"]
                and spec.get("dataset_sha256") == wanted["dataset_sha256"]
                and spec.get("eval_flags") == wanted["eval_flags"]
                and (spec_path.parent / "eval.nc").exists()):
            found.append(spec_path.parent)
    if not found:
        return None, ""
    # KNOWN DEFECT, assigned to batch 28 and deliberately not repaired here.
    #
    # What this returns depends on *which combinations happen to exist on disk*, because
    # `found` is a glob over sibling result directories and the tie is broken by taking the
    # first. Worse, whether it finds anything at all does too: the archived
    # `main__holdout/pool_check.json` records the reconstruction as impossible -- "no stored
    # evaluation of ['hier_nb', 'boosted']" -- because batch 16 ran `main__holdout` before
    # those directories existed, and re-running it today reconstructs the pool and gets
    # 76.646 against the reported 76.731. Eighteen of the 51 `pool_check.json` files change
    # when re-run, with no number in them moving; what moves is which evaluation each names
    # and whether the reconstruction happened.
    #
    # Batch 26 found this while fixing the KeyError below and left it alone: repairing the
    # tie-break alone would rewrite those eighteen archived files while leaving the larger
    # time-dependence in place, and deciding what the headline holdout row's reconstruction
    # should say is not something to do in passing.
    return found[0], found[0].name


def main() -> None:
    out = NODE / "results" / COMBO
    specification = json.loads((out / "candidate_spec.json").read_text())
    fitted = json.loads((out / "fitted_model.json").read_text())
    ours = json.loads((out / "model_spec.json").read_text())
    membership = json.loads((out / "members.json").read_text())["members"]
    weights = np.asarray([m["weight"] for m in fitted["members"]], dtype=float)
    names = [m["name"] for m in fitted["members"]]

    # --- 1. the reconstruction -------------------------------------------------------
    blocks, sources, unmatched = [], {}, []
    index = None
    for member in membership:
        directory, combination = matching_evaluation(member, ours)
        if directory is None:
            # The member has not been evaluated on its own under the configuration the
            # pool gave it. That is a fact about which combinations have been run, not a
            # fault in the pool, so it is recorded and the reconstruction is skipped --
            # the premise check below does not depend on it.
            unmatched.append(member["name"])
            continue
        forecasts, observations = flat(directory / "eval.nc")
        wide = sample_block(forecasts)
        blocks.append(wide)
        index = wide.index if index is None else index.intersection(wide.index)
        sources[member["name"]] = {
            "evaluation": str((directory / "eval.nc").relative_to(ROOT)),
            "combination": combination,
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
        member_scores = {name: score(stack[m])["crps"] for m, name in enumerate(names)}
        member_coverage = {name: score(stack[m])["coverage_10_90"]
                           for m, name in enumerate(names)}

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
            "not_done_because": (
                f"no stored evaluation of {unmatched} under the configuration the pool "
                f"gave them; the reconstruction needs every member's own run"
                if unmatched else None),
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
