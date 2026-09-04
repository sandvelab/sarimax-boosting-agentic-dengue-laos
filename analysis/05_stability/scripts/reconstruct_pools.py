"""Every pool row's independent reconstruction, settled once the whole set has run.

`c_ensemble/scripts/check_pool.py` rebuilds the pool from its members' **own** stored
evaluations — the runs each member produced when it was evaluated on its own, through its
own node — and compares that with what the pool scored. It is the second path behind the
claim that the pool holds no model code of its own, and it needs its members' separate
runs to exist.

They exist late. A candidate family runs on its own only under the family fork's own
combination, which is a stability row, so on a run of `analysis/run.sh` from nothing the
main path's pool is checked hours before candidate 1 and candidate 2 have been evaluated
separately. The check then records that the reconstruction could not be done — truthfully,
at that moment — and nothing afterwards revisits it. In this repository the record was
worse than late: the archived `main__holdout` said the reconstruction was *impossible*,
which recorded only that batch 16 ran the holdout's main row before the holdout's family
rows, and re-running the same script years' worth of batches later reconstructed it
without difficulty. Batch 26 found it; batch 28 is this.

So this step runs at the end of `05_stability/run.sh`, where every combination has been
run, and gives every pool row the same answer it would have had if the tree had been built
in any other order:

* for each combination with a pool, it asks `check_pool`'s own rule which stored
  evaluation each member should be compared against — never a second copy of that rule;
* where the file on disk names those evaluations already, nothing is re-run;
* where it does not, `check_pool.py` is invoked exactly as `c_ensemble/run.sh` invokes it,
  with `COMBO` set, and it rewrites its own file.

**A combination whose reconstruction is still not done after this is one no order of
execution could have helped**: it moves a fork *inside* one of the members, and nothing in
the tree ever evaluated that member on its own under that configuration. That is a
property of the perturbation manifest, and this file says which rows it applies to.

Writes, at this node:
  results/pool_reconstruction.json   every pool row, the evaluations available for each
                                     member, the one the rule names, and the residual
                                     between the rebuilt pool and the pool that ran
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
ENSEMBLE = ROOT / "analysis/03_models/03_candidate/c_ensemble"
PYTHON = ROOT / "environment" / "chapenv" / "bin" / "python"

sys.path.insert(0, str(ENSEMBLE / "scripts"))
import check_pool  # noqa: E402


def wanted_sources(combination: str) -> dict[str, dict]:
    """What `check_pool`'s rule says this combination's members should be compared with."""
    out = ENSEMBLE / "results" / combination
    ours = json.loads((out / "model_spec.json").read_text())
    membership = json.loads((out / "members.json").read_text())["members"]
    sources = {}
    for member in membership:
        found = check_pool.stored_evaluations(member, ours)
        directory, chosen, why = check_pool.matching_evaluation(member, ours, combination)
        sources[member["name"]] = {
            "evaluations_available": found,
            "chosen": chosen or None,
            "chosen_by": why if directory is not None else None,
            "not_chosen_because": (None if directory is not None else
                                   (why or "no run of this member under the configuration "
                                           "the pool gave it")),
        }
    return sources


def recorded_sources(combination: str) -> tuple[dict[str, str], dict[str, str]] | None:
    """What the file on disk names, as {member: combination} and {member: clause}."""
    path = ENSEMBLE / "results" / combination / "pool_check.json"
    if not path.exists():
        return None
    used = json.loads(path.read_text())["reconstruction"]["member_evaluations"]
    return ({name: value["combination"] for name, value in used.items()},
            {name: value.get("chosen_by") for name, value in used.items()})


def main() -> None:
    rows, rerun = [], []
    for directory in sorted((ENSEMBLE / "results").iterdir()):
        if not (directory / "members.json").exists():
            continue
        if not (directory / "eval.nc").exists():
            continue
        combination = directory.name
        wanted = wanted_sources(combination)
        expected = {name: value["chosen"] for name, value in wanted.items()
                    if value["chosen"]}
        clauses = {name: value["chosen_by"] for name, value in wanted.items()
                   if value["chosen"]}
        found = recorded_sources(combination)
        if found is None or found[0] != expected or found[1] != clauses:
            print(f"reconstruct_pools: re-running check_pool for {combination}"
                  f" (names {found[0] if found else 'nothing'}, rule says {expected})",
                  flush=True)
            subprocess.run([str(PYTHON), str(ENSEMBLE / "scripts" / "check_pool.py")],
                           cwd=ROOT, check=True,
                           env={**os.environ, "COMBO": combination})
            rerun.append(combination)
        document = json.loads((directory / "pool_check.json").read_text())
        reconstruction = document["reconstruction"]
        rows.append({
            "combination": combination,
            "members": wanted,
            "reconstructed": reconstruction["mean_crps_rebuilt"] is not None,
            "not_done_because": reconstruction["not_done_because"],
            "cells": reconstruction["cells_in_common"],
            "mean_crps_as_run": reconstruction["mean_crps_as_run"],
            "mean_crps_rebuilt": reconstruction["mean_crps_rebuilt"],
            "difference": reconstruction["difference"],
        })

    done = [r for r in rows if r["reconstructed"]]
    residuals = sorted(abs(r["difference"]) for r in done)
    summary = {
        "what_this_is": (
            "every combination with a pool, the stored evaluations each of its members "
            "has, and the one check_pool's rule compares the pool against. Written after "
            "the whole manifest has run, so it does not depend on the order the rows were "
            "executed in; the rows re-run to get there are named in the run log, not here, "
            "because which files were already correct is a fact about this invocation and "
            "not about the analysis"),
        "combinations": len(rows),
        "reconstructed": len(done),
        "not_reconstructed": len(rows) - len(done),
        "why_the_rest_cannot_be": (
            "the combination moves a fork inside one of the pool's members, and the tree "
            "evaluates a member on its own only under the family fork's own combination, "
            "so no run of this analysis produces that member's separate evaluation under "
            "that configuration"),
        "residual_between_the_rebuilt_pool_and_the_pool_that_ran": {
            "what_it_is": ("the members' draws are the same draws; the pool takes a seeded "
                           "subsample of each member's thousand and the reconstruction "
                           "takes a different one, so the residual is the sampling error "
                           "of the pool's own allocation"),
            "smallest": residuals[0] if residuals else None,
            "largest": residuals[-1] if residuals else None,
        },
        "rows": rows,
    }
    out = NODE / "results" / "pool_reconstruction.json"
    out.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    message = (f"pool reconstruction: {len(done)} of {len(rows)} combinations rebuilt "
               f"from their members' own evaluations, {len(rerun)} file(s) rewritten")
    if rerun:
        message += " (" + ", ".join(rerun) + ")"
    if residuals:
        message += f"; residuals {residuals[0]:.3f} to {residuals[-1]:.3f}"
    print(message + f" -> {out}")


if __name__ == "__main__":
    main()
