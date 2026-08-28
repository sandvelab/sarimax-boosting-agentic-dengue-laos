#!/usr/bin/env python3
"""What each candidate family scores at its own main path, in one table.

`candidate_fork_sweep.py` answers "which child of each fork should this candidate take".
This answers the question one level up and the last one phase C has to settle: **which
family should the project's model be**. The two are separate scripts because they are
separate questions, and because a sweep is taken around one candidate while this is taken
across all of them.

## Why the table cannot simply be one combination's leaderboard

An alternatives node runs exactly one child, so no single combination ever contains all
three families. Candidate 1 ran under `main`, candidate 2 under `family_boosted` and
candidate 3 under `family_ensemble`, each inheriting the dataset, the setup choices and the
reference from `main`. Every row here is therefore read from **the combination in which
that family ran at its own main path**, and which combination that was is a column of the
table rather than something the reader has to know.

**The combination is found, not named.** For each family, this looks for a combination
whose stored `candidate_spec.json` records exactly the choices its forks currently declare
as their main paths — so a family whose forks were promoted since it last ran has no row
rather than a stale one, and the table cannot quietly describe a configuration that is no
longer the family's.

**Every number is copied from a file inside the tree.** The scores come from
`04_score/02_aggregate/a_unweighted/results/<combo>/metrics_summary.csv`, which the tree's
own scripts wrote from chap-core's own metrics; the cost from the node's `run_cost.json`;
the configuration hash from its `candidate_spec.json`. The one computed value is the skill
score, a ratio of two numbers on the same row.

Run from the repository root:
  .venv/bin/python AI-internal/useful-scripts/family_leaderboard.py --label families
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ROOT / "analysis/03_models/03_candidate"
AGGREGATE = ROOT / "analysis/04_score/02_aggregate/a_unweighted/results"
OUT_ROOT = ROOT / "AI-generated/candidate-forks"
REFERENCE = "reference"


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    value = m.group(1).strip() if m else ""
    return value or None


def main_path_children(family: Path) -> set[str]:
    """The child nodes the family's forks currently declare as their main paths.

    Compared as **node paths** rather than as a stage-to-choice mapping: a fork's
    directory name and the stage name its children write into their specifications are
    two different strings by design -- `06_yearVariance` and `year_variance` -- and a
    comparison that assumed they matched would silently find no family at all.
    """
    children = set()
    for fork in sorted(p for p in family.iterdir()
                       if p.is_dir() and (p / "claim.md").exists()):
        main = field((fork / "claim.md").read_text(), "main-path")
        if not main:
            raise SystemExit(f"{fork} declares no main path")
        children.add(str((fork / main).relative_to(ROOT)))
    return children


def combination_of(family: Path) -> tuple[str, dict] | None:
    """The combination in which this family ran at its own main path, if any."""
    wanted = main_path_children(family)
    for spec_path in sorted(family.glob("results/*/candidate_spec.json")):
        spec = json.loads(spec_path.read_text())
        if (set(spec["choice_nodes"].values()) == wanted
                and (spec_path.parent / "model_spec.json").exists()):
            return spec_path.parent.name, spec
    return None


def rows_for(combination: str) -> dict[str, dict]:
    path = AGGREGATE / combination / "metrics_summary.csv"
    if not path.exists():
        raise SystemExit(f"no aggregated scores for {combination!r}: {path} is missing")
    with path.open() as handle:
        return {row["model"]: row for row in csv.DictReader(handle)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--label", default="families",
                        help="subdirectory of AI-generated/candidate-forks to write to")
    args = parser.parse_args(argv)
    out = OUT_ROOT / args.label
    out.mkdir(parents=True, exist_ok=True)

    on_the_main_path = field((FAMILIES / "claim.md").read_text(), "main-path")
    table, missing = [], []
    for family in sorted(p for p in FAMILIES.iterdir()
                         if p.is_dir() and (p / "claim.md").exists()):
        found = combination_of(family)
        if not found:
            missing.append(family.name)
            continue
        combination, spec = found
        rows = rows_for(combination)
        cost = json.loads(
            (family / "results" / combination / "run_cost.json").read_text())
        ours, reference = rows[cost["model"]], rows[REFERENCE]
        table.append({
            "family": family.name,
            "model": cost["model"],
            "on_the_main_path": family.name == on_the_main_path,
            "combination": combination,
            "mean_crps": float(ours["mean_crps"]),
            "mae": float(ours["mae"]),
            "coverage_10_90": float(ours["coverage_10_90"]),
            "coverage_25_75": float(ours["coverage_25_75"]),
            "n_cells": int(ours["n_cells"]),
            "crps_reference": float(reference["mean_crps"]),
            "skill_vs_reference": 1 - float(ours["mean_crps"]) / float(reference["mean_crps"]),
            "backtest_seconds": cost["wall_clock_seconds"],
            "choices": ";".join(f"{k}={v}" for k, v in spec["choices"].items()),
            "configuration_sha256": spec["configuration_sha256"],
        })

    if not table:
        raise SystemExit("no family has run at its own main path; nothing to tabulate")
    table.sort(key=lambda row: row["mean_crps"])

    board = out / "family_leaderboard.csv"
    with board.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    best = table[0]
    current = next((r for r in table if r["on_the_main_path"]), None)
    (out / "families.json").write_text(json.dumps({
        "node": "analysis/03_models/03_candidate",
        "families": len(table),
        "families_without_a_current_run": missing,
        "source": ("analysis/04_score/02_aggregate/a_unweighted/results/<combo>/"
                   "metrics_summary.csv, and each family's run_cost.json and "
                   "candidate_spec.json under the combination it ran at its main path"),
        "on_the_main_path": on_the_main_path,
        "main_path_mean_crps": current["mean_crps"] if current else None,
        "best_family": best["family"],
        "best_mean_crps": best["mean_crps"],
        "best_moves_the_main_path_by": (current["mean_crps"] - best["mean_crps"]
                                        if current else None),
        "reference_mean_crps": best["crps_reference"],
        "ranking": [row["family"] for row in table],
    }, indent=1, sort_keys=True) + "\n")

    width = max(len(row["family"]) for row in table)
    print(f"{'family':<{width}}  {'combination':<16} {'CRPS':>7} {'MAE':>7} {'10-90':>6} "
          f"{'25-75':>6} {'skill':>8} {'s':>5}")
    for row in table:
        mark = "  <- on the main path" if row["on_the_main_path"] else ""
        print(f"{row['family']:<{width}}  {row['combination']:<16} "
              f"{row['mean_crps']:7.3f} {row['mae']:7.3f} {row['coverage_10_90']:6.3f} "
              f"{row['coverage_25_75']:6.3f} {row['skill_vs_reference']:+8.4f} "
              f"{row['backtest_seconds']:5.0f}{mark}")
    if missing:
        print(f"\nno current run at their own main path: {missing}")
    print(f"\n-> {board.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
