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
  .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py run --label round2_promoted
  .venv/bin/python .../candidate_fork_sweep.py run --label round2_promoted --only autoregressive_lag3
  .venv/bin/python .../candidate_fork_sweep.py summarise --label round2_promoted

**A sweep is taken around one main path.** Promoting a fork moves the main path, so the
rows of a sweep taken before the promotion and one taken after are not comparable and must
not share a table. `--label` names the sweep; `summarise` refuses to rebuild a table whose
recorded base configuration is not the tree's current one.
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
FAMILIES = ROOT / "analysis/03_models/03_candidate"
OUT_ROOT = ROOT / "AI-generated/candidate-forks"
PYTHON = ROOT / "environment/chapenv/bin/python"

# Which candidate is being swept and which combination its main path was run under. Set
# once by `main` from the command line and read by everything below, because a sweep is a
# statement about one candidate around one base and passing both through every function
# would say so at every line without making it any more true.
#
# Batch 10 made these variables rather than constants. Candidate 2 is a *sibling family*
# under an alternatives node, so it never runs under `main` at all -- its main path runs
# under a combination of its own, and its internal forks are swept around that. A second
# copy of this file with two names changed would have been the obvious alternative and is
# what `chap_eval.py` argues against: a copy per model is a set of copies that will drift.
CANDIDATE = FAMILIES / "a_hierNB"
BASE = "main"
# The combination a swept row inherits from, which is not always the one it is measured
# against. For candidate 1 the two are the same: its main path ran under `main`, which
# also holds the dataset and the other models. Candidate 2's main path ran under a
# combination of its own -- it is a sibling family and never runs under `main` at all --
# so its rows are *measured* against that combination and *inherit* from `main`, where
# the dataset and the other models are. Collapsing the two would make one of them wrong.
INHERIT = "main"


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


def own_scripts() -> list[Path]:
    """The candidate node's own steps, in the order its `run.sh` runs them.

    Read from the generated `run.sh` rather than named here, so that the sweep runs
    whatever the node runs. Naming them would be a second list of the node's steps and
    the one that decides what a swept combination actually contains.
    """
    text = (CANDIDATE / "run.sh").read_text()
    found = [CANDIDATE / m for m in
             re.findall(r'^"\$PYTHON" "(scripts/[^"]+)"$', text, re.M)]
    if not found:
        raise SystemExit(f"{CANDIDATE / 'run.sh'} lists no own scripts; there is nothing "
                         f"for a swept combination to run")
    return found


def run_one(fork: Path, child: Path, out: Path) -> dict:
    """Run one sibling end to end, from its own choice down to the aggregated scores."""
    combo = combination(fork, child)
    out.mkdir(parents=True, exist_ok=True)
    environment = {**os.environ, "COMBO": combo, "COMBO_BASE": INHERIT}
    log_path = out / f"sweep_{combo}.log"

    started = time.time()
    with log_path.open("w") as log:
        log.write(f"# {combo}: {child.relative_to(ROOT)}, measured against {BASE}, "
                  f"inheriting from {INHERIT}\n\n")
        step(["bash", str(child / "run.sh")], environment, log)
        # The forks this combination did not move are answered by `COMBO_BASE` wherever
        # the base combination has them, and run here wherever it does not. Candidate 1
        # is swept around `main`, which holds every choice, so nothing extra runs and the
        # inheritance record is exactly what it was before batch 10. Candidate 2 is swept
        # around its own family combination, which holds its two choices but not the
        # setup or the other models, so its untouched fork is re-run and says so.
        for other, other_main, _ in forks():
            if other == fork:
                continue
            if not (other / other_main / "results" / INHERIT).exists():
                log.write(f"# {other.name}: not present under {INHERIT}, running its "
                          f"main path here\n")
                step(["bash", str(other / other_main / "run.sh")], environment, log)
        for own in own_scripts():
            step([str(PYTHON), str(own)], environment, log)
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


def summarise(out: Path, guard: bool = True) -> None:
    """Collate every combination's scores into one table. Copies; computes one ratio."""
    out.mkdir(parents=True, exist_ok=True)
    previous = out / "fork_sweep.json"
    if guard and previous.exists():
        recorded = json.loads(previous.read_text()).get("base_configuration_sha256")
        current = json.loads(
            (CANDIDATE / "results" / BASE / "candidate_spec.json").read_text()
        )["configuration_sha256"]
        if recorded and recorded != current:
            raise SystemExit(
                "the main path has moved since this sweep was run: it was taken around\n"
                f"  {recorded}\nand the tree now says\n  {current}\n"
                "A one-at-a-time sweep whose rows were measured around different base\n"
                "configurations is not a sweep. Run the sweep again rather than "
                "re-tabulating this one.")
    entries = [{"combo": BASE, "fork": "-", "child": "the main path"}]
    for fork, main, siblings in forks():
        for child in siblings:
            entries.append({"combo": combination(fork, child),
                            "fork": str(fork.relative_to(ROOT)), "child": child.name})

    table = []
    for entry in entries:
        rows = summary_row(entry["combo"])
        cost = json.loads((CANDIDATE / "results" / entry["combo"] / "run_cost.json").read_text())
        spec = json.loads((CANDIDATE / "results" / entry["combo"] / "candidate_spec.json").read_text())
        # Which row of the leaderboard is ours, read from the model's own specification
        # rather than named here: the sweep is told which candidate to sweep and the
        # candidate is what says what it is called.
        ours, reference = rows[cost["model"]], rows["reference"]
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
    board = out / "fork_leaderboard.csv"
    with board.open("w", newline="") as handle:
        # Line endings to match every other CSV in the project, which pandas wrote.
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    best = table[0]
    main_row = next(row for row in table if row["combo"] == BASE)
    (out / "fork_sweep.json").write_text(json.dumps({
        "swept": str(CANDIDATE.relative_to(ROOT)),
        "base_combination": BASE,
        "inherited_from": INHERIT,
        "combinations": len(table),
        "source": ("analysis/04_score/02_aggregate/a_unweighted/results/<combo>/"
                   "metrics_summary.csv, and the candidate node's run_cost.json and "
                   "candidate_spec.json"),
        "main_path_mean_crps": main_row["mean_crps"],
        # The configuration the sweep was taken around. `summarise` refuses to rebuild
        # the table against a different one, because a one-at-a-time sweep whose rows
        # were measured around different base configurations is not a sweep.
        "base_configuration_sha256": main_row["configuration_sha256"],
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


def compare_rounds(before: Path, after: Path, out: Path) -> None:
    """What one sweep says a fork is worth, against what the next sweep says.

    A one-at-a-time sweep answers "what does this fork do to the main path" one fork at a
    time, which is what tier 1 of the phase-D manifest is. Running a second sweep around
    a promoted main path answers the same question from a different place, and the two
    answers need not agree -- if the forks interact, they will not.

    The comparison is between a child's effect **around the earlier base** and the same
    child's effect **around the later one**, both taken as `base CRPS - child CRPS`, so a
    positive number always means "taking this child improves the model from here". For a
    child that was promoted, its effect around the later base is the mirror image: the
    child that was demoted in its place now sits in the table, and reverting to it is the
    cost of the promotion measured from the other side.
    """
    rows_before = {row["combo"]: row for row in
                   csv.DictReader((before / "fork_leaderboard.csv").open())}
    rows_after = {row["combo"]: row for row in
                  csv.DictReader((after / "fork_leaderboard.csv").open())}
    base_before = float(rows_before[BASE]["mean_crps"])
    base_after = float(rows_after[BASE]["mean_crps"])

    # Which child each fork took before and takes now, read from the two tables' own
    # notion of what was not the main path.
    def children(rows):
        return {row["fork"]: row["child"] for row in rows.values() if row["fork"] != "-"}

    table = []
    for fork, _, siblings in forks():
        name = str(fork.relative_to(ROOT))
        for child in siblings + [Path(field((fork / "claim.md").read_text(), "main-path"))]:
            combo_after = combination(fork, fork / child.name)
            combo_before = combo_after
            if combo_after not in rows_after and combo_after not in rows_before:
                continue
            effect_before = (base_before - float(rows_before[combo_before]["mean_crps"])
                             if combo_before in rows_before else None)
            effect_after = (base_after - float(rows_after[combo_after]["mean_crps"])
                            if combo_after in rows_after else None)
            table.append({
                "fork": name, "child": child.name,
                "on_the_main_path_now": child.name not in [s.name for s in siblings],
                "effect_around_earlier_base": effect_before,
                "effect_around_later_base": effect_after,
                "sign_reversed": (effect_before is not None and effect_after is not None
                                  and effect_before * effect_after < 0),
            })

    promoted = [row for row in table if row["on_the_main_path_now"]
                and row["effect_around_earlier_base"] is not None]
    out.mkdir(parents=True, exist_ok=True)
    with (out / "fork_interaction.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    summary = {
        "earlier_sweep": before.name,
        "later_sweep": after.name,
        "earlier_base_mean_crps": base_before,
        "later_base_mean_crps": base_after,
        "actual_gain_from_the_promotion": base_before - base_after,
        # What the one-at-a-time sweep predicted the promotion would gain, if the forks
        # it moved had acted independently.
        "sum_of_the_promoted_forks_one_at_a_time_effects":
            sum(row["effect_around_earlier_base"] for row in promoted),
        "promoted": {row["child"]: row["effect_around_earlier_base"] for row in promoted},
        "children_whose_effect_reversed_sign":
            [row["child"] for row in table if row["sign_reversed"]],
        "source": [str((p / "fork_leaderboard.csv").relative_to(ROOT))
                   for p in (before, after)],
    }
    summary["one_at_a_time_overstates_the_promotion_by"] = (
        summary["sum_of_the_promoted_forks_one_at_a_time_effects"]
        - summary["actual_gain_from_the_promotion"])
    (out / "fork_interaction.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")

    print(f"{'fork child':28s} {'around ' + before.name[:10]:>18} "
          f"{'around ' + after.name[:10]:>18}")
    for row in table:
        def show(value):
            return f"{value:+.3f}" if value is not None else "-"
        mark = "  <- on the main path" if row["on_the_main_path_now"] else ""
        print(f"{row['child']:28s} {show(row['effect_around_earlier_base']):>18} "
              f"{show(row['effect_around_later_base']):>18}{mark}")
    print(f"\npromotion gained {summary['actual_gain_from_the_promotion']:.3f} CRPS; "
          f"one at a time predicted "
          f"{summary['sum_of_the_promoted_forks_one_at_a_time_effects']:.3f}")
    print(f"-> {(out / 'fork_interaction.csv').relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    # Which candidate, and which combination its main path ran under. Defaults are
    # candidate 1 around `main`, so every invocation recorded before batch 10 still means
    # what it meant.
    parser.add_argument("--candidate", default="a_hierNB",
                        help="directory name under 03_models/03_candidate to sweep")
    parser.add_argument("--base", default="main",
                        help="the combination this candidate's main path ran under")
    parser.add_argument("--inherit-from", default=None,
                        help="the combination a swept row inherits its dataset and the "
                             "other models from; defaults to --base")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("run", "run every sibling, then summarise"),
                            ("summarise", "rebuild the table from what is in the tree")):
        step_parser = sub.add_parser(name, help=help_text)
        # A sweep is taken around one main path, and the main path moves when a fork is
        # promoted. The label says which sweep a table is, so a later one does not
        # overwrite the record the promotion was decided from.
        step_parser.add_argument("--label", required=True,
                                 help="subdirectory for this sweep's outputs")
        if name == "run":
            step_parser.add_argument("--only", help="one combination name, to run alone")
    rounds = sub.add_parser("compare-rounds",
                            help="what a fork was worth in one sweep against the next")
    rounds.add_argument("--before", required=True)
    rounds.add_argument("--after", required=True)
    args = parser.parse_args(argv)

    global CANDIDATE, BASE, INHERIT
    CANDIDATE = FAMILIES / args.candidate
    BASE = args.base
    INHERIT = args.inherit_from or args.base
    if not (CANDIDATE / "claim.md").exists():
        raise SystemExit(f"{CANDIDATE} is not a node")
    if not (CANDIDATE / "results" / BASE / "candidate_spec.json").exists():
        raise SystemExit(
            f"{args.candidate} has no assembled configuration under combination "
            f"{BASE!r}. A sweep is taken around a main path that has been run, because "
            f"every row of it is measured as a difference from that row.")

    if args.command == "compare-rounds":
        compare_rounds(OUT_ROOT / args.before, OUT_ROOT / args.after,
                       OUT_ROOT / args.after)
        return 0

    out = OUT_ROOT / args.label

    if args.command == "summarise":
        summarise(out)
        return 0

    ran = []
    for fork, _, siblings in forks():
        for child in siblings:
            if args.only and combination(fork, child) != args.only:
                continue
            print(f"{fork.name}/{child.name}")
            ran.append(run_one(fork, child, out))
    if not ran:
        raise SystemExit(f"nothing to run{f' for {args.only!r}' if args.only else ''}")
    (out / "sweep_runs.json").write_text(json.dumps(ran, indent=1, sort_keys=True) + "\n")
    # No guard here: a `run` has just measured every row around the current main path,
    # so the table it writes is by construction taken around that configuration.
    summarise(out, guard=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
