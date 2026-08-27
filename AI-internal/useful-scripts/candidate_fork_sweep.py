#!/usr/bin/env python3
"""Run every non-main child of candidate 1's forks on the development data, and tabulate.

Phase C has to choose which child of each fork the main path takes, and a choice made on
anything other than what the children score is a choice made on taste. So each sibling is
run: one combination per sibling, everything else held at the main path's choice.

## Why this lives here and not in the tree

`AGENTS.md` §2 says the paths not taken are executed by the stability node, and the
stability node is batch 12's. This script is not that node and does not replace it. The
difference is what the numbers are *for*:

* **here, phase C**: a selection aid. Which child does the main path take? The answer is
  read off the leaderboard quantities -- mean CRPS, calibration, cost -- and then the tree
  is promoted and the decision recorded.
* **there, phase D**: the reported result. The frozen manifest is run through the whole
  scoring chain, every combination gets its own `conclusion.json`, and what is reported is
  the *distribution* of conclusions over the reasonable analyses -- including the cost of
  the selection this script informs.

So the sweep stops at `04_score/02_aggregate`. It does not run `03_compare` or
`conclude.py`, because a conclusion per sibling is exactly the phase-D deliverable and
producing nine of them here would report the stability answer before the manifest that
makes it honest has been frozen.

**Every number the sweep produces is written inside the tree**, by the tree's own scripts,
under `results/<combination>/`. Only the cross-combination table is written here, and it
is copied from those files by `summarise()` rather than computed a second time.

## What a combination is

One non-main child of one fork, with every other fork left at its main path. That is
`COMBO=<stage>_<child>` with `COMBO_BASE=main`: the sibling's own step runs and writes
under the new combination, and every input it does not itself produce -- the assembled
dataset, the five choices this combination did not move, the reference and baseline scores
-- is resolved from `main` by `analysis/scripts/lib/combos.py` and recorded as inherited.
The reference is therefore not re-run, which matters because it is unseeded: re-running it
would replace its four repeats with a different draw and move the denominator of every
comparison for reasons that have nothing to do with the fork.

Run from the repository root:
  .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py run
  .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py run --only autoregressive_lag3
  .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py summarise
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "analysis/03_models/03_candidate/a_hierNB"
OUT = ROOT / "AI-generated/candidate-forks"
PYTHON = ROOT / "environment/chapenv/bin/python"
BASE = "main"


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    value = m.group(1).strip() if m else ""
    return value or None


def forks() -> list[tuple[Path, str, list[Path]]]:
    """Each fork under the candidate: its node, its main-path child, its siblings."""
    out = []
    for fork in sorted(p for p in CANDIDATE.iterdir()
                       if p.is_dir() and (p / "claim.md").exists()):
        main = field((fork / "claim.md").read_text(), "main-path")
        children = sorted(p for p in fork.iterdir()
                          if p.is_dir() and (p / "claim.md").exists())
        out.append((fork, main, [c for c in children if c.name != main]))
    return out


def stage(fork: Path) -> str:
    """The fork's name without its ordering prefix -- `01_observation` -> `observation`."""
    return fork.name.split("_", 1)[1]


def combination(fork: Path, child: Path) -> str:
    """The combination name for taking `child` at `fork`, everything else at the main path."""
    return f"{stage(fork)}_{child.name.split('_', 1)[1]}"


def step(command: list[str], environment: dict, log) -> None:
    log.write("$ " + " ".join(command) + "\n")
    log.flush()
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=environment)
    if result.returncode != 0:
        raise SystemExit(f"failed ({result.returncode}): {' '.join(command)}; see {log.name}")


def run_one(fork: Path, child: Path) -> dict:
    """Run one sibling end to end, from its own choice down to the aggregated scores."""
    combo = combination(fork, child)
    OUT.mkdir(parents=True, exist_ok=True)
    environment = {**os.environ, "COMBO": combo, "COMBO_BASE": BASE}
    log_path = OUT / f"sweep_{combo}.log"

    started = time.time()
    with log_path.open("w") as log:
        log.write(f"# {combo}: {child.relative_to(ROOT)}, everything else at {BASE}\n\n")
        step(["bash", str(child / "run.sh")], environment, log)
        step([str(PYTHON), str(CANDIDATE / "scripts/assemble_candidate_config.py")],
             environment, log)
        step([str(PYTHON), str(CANDIDATE / "scripts/run_hier_nb.py")], environment, log)
        step(["bash", str(ROOT / "analysis/04_score/01_collect/run.sh")], environment, log)
        step(["bash", str(ROOT / "analysis/04_score/02_aggregate/run.sh")], environment, log)
    seconds = time.time() - started

    print(f"  {combo}: {seconds:.0f} s -> {log_path.relative_to(ROOT)}")
    return {"combo": combo, "fork": str(fork.relative_to(ROOT)), "child": child.name,
            "sweep_seconds": round(seconds, 1)}


def summary_row(combo: str) -> dict:
    """The scored rows for one combination, read from the file the tree wrote."""
    path = (ROOT / "analysis/04_score/02_aggregate/a_unweighted/results" / combo
            / "metrics_summary.csv")
    if not path.exists():
        raise SystemExit(f"no aggregated scores for {combo!r}: {path} is missing")
    with path.open() as handle:
        rows = {row["model"]: row for row in csv.DictReader(handle)}
    return rows


def summarise() -> None:
    """Collate every combination's scores into one table. Copies; computes one ratio."""
    OUT.mkdir(parents=True, exist_ok=True)
    entries = [{"combo": BASE, "fork": "-", "child": "the main path"}]
    for fork, main, siblings in forks():
        for child in siblings:
            entries.append({"combo": combination(fork, child),
                            "fork": str(fork.relative_to(ROOT)), "child": child.name})

    table = []
    for entry in entries:
        rows = summary_row(entry["combo"])
        ours, reference = rows["hier_nb"], rows["reference"]
        cost = json.loads((CANDIDATE / "results" / entry["combo"] / "run_cost.json").read_text())
        spec = json.loads((CANDIDATE / "results" / entry["combo"] / "candidate_spec.json").read_text())
        table.append({
            **entry,
            "mean_crps": float(ours["mean_crps"]),
            "mae": float(ours["mae"]),
            "coverage_10_90": float(ours["coverage_10_90"]),
            "coverage_25_75": float(ours["coverage_25_75"]),
            "n_cells": int(ours["n_cells"]),
            "crps_reference": float(reference["mean_crps"]),
            # The one computed value here, and it is a ratio of two numbers on the row.
            "skill_vs_reference": 1 - float(ours["mean_crps"]) / float(reference["mean_crps"]),
            "backtest_seconds": cost["wall_clock_seconds"],
            "inherited_choices": sum(1 for where in spec["choice_combos"].values()
                                     if where != entry["combo"]),
            "configuration_sha256": spec["configuration_sha256"],
        })

    table.sort(key=lambda row: row["mean_crps"])
    board = OUT / "fork_leaderboard.csv"
    with board.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)

    best = table[0]
    main_row = next(row for row in table if row["combo"] == BASE)
    (OUT / "fork_sweep.json").write_text(json.dumps({
        "swept": "analysis/03_models/03_candidate/a_hierNB",
        "base_combination": BASE,
        "combinations": len(table),
        "source": ("analysis/04_score/02_aggregate/a_unweighted/results/<combo>/"
                   "metrics_summary.csv, and the candidate node's run_cost.json and "
                   "candidate_spec.json"),
        "main_path_mean_crps": main_row["mean_crps"],
        "best_combination": best["combo"],
        "best_mean_crps": best["mean_crps"],
        "best_moves_the_main_path_by": main_row["mean_crps"] - best["mean_crps"],
        "reference_mean_crps": main_row["crps_reference"],
        "ranking": [row["combo"] for row in table],
    }, indent=1, sort_keys=True) + "\n")

    width = max(len(row["combo"]) for row in table)
    print(f"\n{'combination':<{width}}  {'CRPS':>7} {'MAE':>7} {'10-90':>6} {'25-75':>6} "
          f"{'skill':>7} {'s':>5}")
    for row in table:
        print(f"{row['combo']:<{width}}  {row['mean_crps']:7.3f} {row['mae']:7.3f} "
              f"{row['coverage_10_90']:6.3f} {row['coverage_25_75']:6.3f} "
              f"{row['skill_vs_reference']:+7.4f} {row['backtest_seconds']:5.0f}")
    print(f"\n-> {board.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run", help="run every sibling, then summarise")
    runner.add_argument("--only", help="one combination name, to re-run it alone")
    sub.add_parser("summarise", help="rebuild the table from what is already in the tree")
    args = parser.parse_args(argv)

    if args.command == "summarise":
        summarise()
        return 0

    ran = []
    for fork, _, siblings in forks():
        for child in siblings:
            if args.only and combination(fork, child) != args.only:
                continue
            print(f"{fork.name}/{child.name}")
            ran.append(run_one(fork, child))
    if not ran:
        raise SystemExit(f"nothing to run{f' for {args.only!r}' if args.only else ''}")
    (OUT / "sweep_runs.json").write_text(json.dumps(ran, indent=1, sort_keys=True) + "\n")
    summarise()
    return 0


if __name__ == "__main__":
    sys.exit(main())
