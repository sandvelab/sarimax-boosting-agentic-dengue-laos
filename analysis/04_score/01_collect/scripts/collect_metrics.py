"""Score every model that ran, at the platform's finest resolution, into one file.

This node implements no metric. Every value comes from chap-core's own registered
metric, asked for by id; the only things this script chooses are the level of
aggregation -- the finest one available -- and the split label, which is recovered by the
arithmetic batch 2 established:

    split (first predicted period) = time_period - (horizon_distance - 1)

A metric we computed ourselves would be the one we could most easily bend without it
being visible, so the project never implements one.

**Models are discovered, not listed.** The script globs `03_models/**/results/$COMBO/`
for the `model_spec.json` every model node writes, so a model added to the tree is scored
by the fact of having run, and a model that did not run is absent rather than stale. That
is also what makes the scoring node indifferent to which child of a fork produced a
model: exactly one of them has results under any one combination.

**A model that did not run under this combination may be inherited.** When
`COMBO_BASE` is set, a model node with no results under `COMBO` is taken from the base
combination, and `models.csv` carries the combination each row was scored under. This is
what makes a candidate-internal fork cheap: it changed nothing the reference or the
baselines face, so re-running them would only replace an unseeded model's draw with a
different one. `analysis/run.sh` sets no base and therefore inherits nothing.

**Inheritance is per fork, not per node**, which is what keeps the sentence above true.
A combination that moves a baseline fork runs one child of it and not the other, so the
other has no results under `COMBO` and would otherwise be inherited from the base —
putting two persistence baselines on one leaderboard, one of them produced by the very
analysis the row is defined against. A node whose sibling ran under `COMBO` is therefore
the path not taken, and is not inherited. Which child was scored is on the face of
`models.csv`, in its `node` column.

**The unseeded reference is carried as its repeats and as their mean.** Its evaluation is
a draw, not a constant, so each repeat becomes its own row and a further row holds the
per-cell mean over them. Downstream, the mean is the denominator of the skill score --
which is what stops a 2 % wobble in an external model's sampler from being read as an
effect of one of our own choices -- and the individual repeats are what say how large
that wobble was on this dataset.

Writes, under results/$COMBO/:
  metrics_cell.csv   one row per (model, location, time_period, horizon_distance)
  models.csv         one row per scored model: where it came from and what it is
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import pandas as pd
from chap_core.assessment.evaluation import Evaluation
from chap_core.assessment.metrics import get_metric

NODE = Path(__file__).resolve().parents[1]

# The headline metric and the secondaries the plan names beside it.
METRIC_IDS = ("crps", "mae", "coverage_10_90", "coverage_25_75")
CELL_COLUMN = {"crps": "crps", "mae": "abs_error",
               "coverage_10_90": "in_10_90", "coverage_25_75": "in_25_75"}
CELL_KEYS = ["location", "time_period", "horizon_distance"]
SCORE_COLUMNS = ["crps", "abs_error", "in_10_90", "in_25_75"]


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import base  # noqa: E402

BASE = base()
MODELS = ROOT / "analysis/03_models"


def shift_period(period: str, back: int) -> str:
    """The monthly period `back` months before `period` (YYYYMM in, YYYYMM out)."""
    year, month = int(str(period)[:4]), int(str(period)[4:])
    index = year * 12 + (month - 1) - back
    return f"{index // 12:04d}{index % 12 + 1:02d}"


def cell_table(evaluation: Path, model: str) -> pd.DataFrame:
    """The finest-resolution table: every metric for every evaluable cell."""
    flat = Evaluation.from_file(evaluation).to_flat()
    observations = pd.DataFrame(flat.observations)
    forecasts = pd.DataFrame(flat.forecasts)

    table: pd.DataFrame | None = None
    for metric_id in METRIC_IDS:
        # `get_metric` returns the metric *class*; the aggregations are instance methods.
        detailed = get_metric(metric_id)().get_detailed_metric(observations, forecasts)
        detailed = detailed.rename(columns={"metric": CELL_COLUMN[metric_id]})
        table = detailed if table is None else table.merge(detailed, on=CELL_KEYS, how="outer")

    table = table.merge(
        observations.rename(columns={"disease_cases": "observed"}),
        on=["location", "time_period"], how="left")
    table["split_first_period"] = [
        shift_period(period, int(horizon) - 1)
        for period, horizon in zip(table.time_period, table.horizon_distance, strict=True)
    ]
    table["n_samples"] = (
        forecasts.groupby(CELL_KEYS).size()
        .reindex(pd.MultiIndex.from_frame(table[CELL_KEYS])).to_numpy())
    table.insert(0, "model", model)
    return table


def fork_choice(node: Path) -> tuple[str, str] | None:
    """The nearest alternatives fork above `node`, and the child of it `node` sits in.

    `(None, None)` where there is none -- the reference model is not a child of any fork,
    and neither is a model node that sits directly under a sub-analyses parent.
    """
    current = node
    while current != MODELS and MODELS in current.parents:
        parent = current.parent
        claim = parent / "claim.md"
        if claim.exists() and re.search(r"^kind:\s*alternatives\s*$",
                                        claim.read_text(), re.M):
            return str(parent.relative_to(MODELS)), current.name
        current = parent
    return None, None


def specs() -> list[tuple[Path, dict, str]]:
    """Every model scored for this combination, in tree order, with where it came from.

    A model node that produced nothing under this combination is taken from `COMBO_BASE`
    when one is set. That is batch 5's reuse rule -- a combination that moved only a
    candidate-internal fork has not changed what the reference or the baselines face, and
    re-running an unseeded external model would replace its four repeats with a different
    draw and move the denominator of the conclusion for reasons that have nothing to do
    with the fork.

    Which combination each model was scored under is returned here and written into
    `models.csv`, so a leaderboard never hides that some of its rows were computed
    elsewhere. With no base set -- which is how `analysis/run.sh` runs -- nothing is
    inherited and a missing model is simply absent.
    """
    found = [(p.parents[2], p, COMBO)
             for p in sorted(MODELS.glob(f"**/results/{COMBO}/model_spec.json"))]
    seen = {node for node, _, _ in found}
    if BASE:
        taken = {fork: child for fork, child in
                 (fork_choice(node) for node in seen) if fork}
        for p in sorted(MODELS.glob(f"**/results/{BASE}/model_spec.json")):
            node = p.parents[2]
            if node in seen:
                continue
            # Inheritance is per fork, not per node. A node with no results under this
            # combination is normally a model the combination did not need to re-run --
            # but if a *sibling* of it ran, the fork moved, and this node is the path not
            # taken. Inheriting it would put both children of one fork on the leaderboard:
            # two persistence baselines, one of them from an analysis this row is defined
            # against. The docstring above says exactly one child of a fork has results
            # under any one combination, and until batch 22 nothing made that true across
            # the inheritance boundary.
            fork, child = fork_choice(node)
            if fork and taken.get(fork, child) != child:
                continue
            found.append((node, p, BASE))
    if not found:
        raise SystemExit(f"no model has results for combination {COMBO!r}"
                         + (f" or its base {BASE!r}" if BASE else "")
                         + "; run analysis/03_models/run.sh first")
    return [(p.parent, json.loads(p.read_text()), where)
            for _, p, where in sorted(found, key=lambda entry: entry[1])]


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    tables: list[pd.DataFrame] = []
    rows: list[dict] = []
    for results_dir, spec, scored_under in specs():
        names = spec.get("repeat_names") or [spec["model"]]
        members = []
        for name, evaluation in zip(names, spec["evaluations"], strict=True):
            members.append(cell_table(results_dir / evaluation, name))
            rows.append({
                "model": name, "origin": spec["origin"], "kind": spec["kind"],
                "node": spec["node"], "seeded": spec["seeded"],
                "n_samples": spec["n_samples"], "repeat_of": spec["model"]
                if len(names) > 1 else "", "evaluation": evaluation,
                "scored_under_combo": scored_under,
            })
        tables.extend(members)

        if len(members) > 1:
            # The per-cell mean over repeats of an unseeded model. Every repeat scored
            # the same cells, so this is an average over draws of the same quantity --
            # not an average over different evaluations.
            mean = (pd.concat(members).groupby(CELL_KEYS + ["split_first_period"],
                                               as_index=False)
                    .agg({**{c: "mean" for c in SCORE_COLUMNS},
                          "observed": "first", "n_samples": "sum"}))
            mean.insert(0, "model", spec["model"])
            tables.append(mean)
            rows.append({
                "model": spec["model"], "origin": spec["origin"], "kind": "repeat-mean",
                "node": spec["node"], "seeded": spec["seeded"],
                "n_samples": spec["n_samples"] * len(members), "repeat_of": "",
                "evaluation": f"mean of {len(members)} repeats",
                "scored_under_combo": scored_under,
            })

    cells = (pd.concat(tables, ignore_index=True)
             .sort_values(["model", "location", "time_period", "horizon_distance"]))
    cells.to_csv(out / "metrics_cell.csv", index=False)
    pd.DataFrame(rows).to_csv(out / "models.csv", index=False)

    inherited = sorted({r["model"] for r in rows if r["scored_under_combo"] != COMBO})
    print(f"collect[{COMBO}]: {cells.model.nunique()} model rows, {len(cells)} cells, "
          f"{cells.location.nunique()} locations -> {out}"
          + (f"; inherited from {BASE}: {inherited}" if inherited else ""))


if __name__ == "__main__":
    main()
