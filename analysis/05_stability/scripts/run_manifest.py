"""Run the combinations the manifest names, by calling the tree's own scripts.

`/perturb run`. `AGENTS.md` §2 says the paths not taken are executed by the stability node,
which calls its siblings' main scripts; this is that. There is no second implementation of
the analysis here and there must never be one -- every command below is a `run.sh` or a
node script that the main path also runs, with `COMBO` set to something other than `main`.

## What a combination has to run, and why it is not just "the pipeline"

A combination takes one child at one fork and leaves every other fork where it is. Both
assemblers in this project -- `02_setup/scripts/assemble_setup.py` and each candidate
family's `assemble_candidate_config.py` -- resolve a fork by finding **the one child of it
with results under this combination**, and fail if they find two. So the driver may not run
a parent's `run.sh` after running a moved sibling: the parent would run the main child as
well and the assembler would see both.

It therefore builds the step list per row, substituting the moved child for the main one:

| kind | steps |
|---|---|
| `main` | `conclude.py`, and nothing else -- the main path is the analysis that already ran |
| `setup` | the moved setup child · the other three setup forks' main children · `assemble_setup.py` · every model · the scoring chain · `conclude.py` |
| `scoring` | `01_collect` · the moved aggregation child · `03_compare` · `conclude.py` |
| `baseline` | the moved baseline child · the other baseline fork's main child · our reported family · the scoring chain · `conclude.py` |
| `family` | the named family, in place of the reported one · the scoring chain · `conclude.py` |
| `candidate` | the moved fork child · our reported family · the scoring chain · `conclude.py` |
| `pair` | the union of its two rows' steps, in tree order, each fork's child taken once |

Everything a combination does not run is inherited from `COMBO_BASE` by
`analysis/scripts/lib/combos.py`, per artefact and on the face of the file that reports it.
The reference model is inherited wherever a fork cannot have moved it, which is not an
optimisation: it is unseeded, and re-running it would replace its four repeats with a
different draw and move the denominator of every comparison for reasons that have nothing
to do with the fork.

## What it does when a row cannot run

Rows whose child has no scripts are **recorded as not run, with the reason**, and the
driver carries on. An absence has to be a visible decision (`AGENTS.md` §4), and a driver
that failed on the first unbuilt row would leave that record in nobody's notes. Every
outcome lands in `results/run_status.csv`, which says for each row what happened, how long
it took, and where its log is.

Usage, from the repository root:
  environment/chapenv/bin/python analysis/05_stability/scripts/run_manifest.py --dry-run
  ... --batch 13            only the rows the manifest assigns to that batch
  ... --only trainingWindow_from2004
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import inventory as inv  # noqa: E402

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
ANALYSIS = ROOT / "analysis"
PYTHON = ROOT / "environment/chapenv/bin/python"
LOGS = NODE / "results" / "logs"


def bash(path: Path) -> list[str]:
    return ["bash", str(path)]


def python(path: Path) -> list[str]:
    return [str(PYTHON), str(path)]


def fork_by_rel(forks: list[inv.Fork], rel: str) -> inv.Fork:
    return next(f for f in forks if f.rel == rel)


def steps_for(row: dict, forks: list[inv.Fork]) -> list[tuple[str, list[str]]]:
    """The ordered commands one combination runs. Named steps, so a log can be read."""
    if row["kind"] == "main":
        return [("conclude", python(ANALYSIS / "scripts/conclude.py"))]

    moved = [(fork_by_rel(forks, rel), child) for rel, child
             in zip(row["fork"].split("+"), row["child"].split("+"))]
    kinds = {fork.kind for fork, _ in moved}
    out: list[tuple[str, list[str]]] = []

    def take(kind: str) -> None:
        """Every fork of this kind: the moved child where one moved, else the main one."""
        chosen = {fork.rel: child for fork, child in moved if fork.kind == kind}
        for fork in [f for f in forks if f.kind == kind]:
            child = chosen.get(fork.rel, fork.main)
            out.append((f"{fork.stage}/{child}", bash(fork.node / child / "run.sh")))

    if "setup" in kinds:
        take("setup")
        out.append(("assemble_setup", python(ANALYSIS / "02_setup/scripts/assemble_setup.py")))

    # Which of our models runs. A family row swaps the reported family for a sibling;
    # everything else runs the family the tree's main path names.
    family_fork = next(f for f in forks if f.kind == "family")
    family = next((child for fork, child in moved if fork.kind == "family"),
                  family_fork.main)

    if "setup" in kinds or "baseline" in kinds:
        take("baseline")
    if "setup" in kinds:
        out.append(("reference", bash(ANALYSIS / "03_models/02_reference/run.sh")))
    if kinds != {"scoring"}:
        # A candidate-internal fork's child writes the option spec the family's assembler
        # then picks up, so it runs before the family and never after it.
        for fork, child in moved:
            if fork.kind == "candidate":
                out.append((f"{fork.stage}/{child}", bash(fork.node / child / "run.sh")))
        out.append((f"family/{family}", bash(family_fork.node / family / "run.sh")))

    out.append(("collect", bash(ANALYSIS / "04_score/01_collect/run.sh")))
    take("scoring")
    out.append(("compare", bash(ANALYSIS / "04_score/03_compare/run.sh")))
    out.append(("conclude", python(ANALYSIS / "scripts/conclude.py")))
    return out


def run_row(row: dict, forks: list[inv.Fork], dry: bool) -> dict:
    combo = row["combination"]
    steps = steps_for(row, forks)
    if dry:
        mark = "" if row["built"] == "True" else "   (not built: this is its specification)"
        print(f"\n{combo}  [{row['kind']}]  base={row['combo_base']}{mark}")
        for name, command in steps:
            shown = " ".join(str(Path(c).relative_to(ROOT)) if str(c).startswith(str(ROOT))
                             else c for c in command)
            print(f"    {name:34s} {shown}")
        return {"combination": combo, "status": "dry-run", "seconds": "",
                "steps": len(steps), "log": "", "at": ""}

    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"{combo}.log"
    environment = {**os.environ, "COMBO": combo}
    if row["combo_base"] not in ("-", "", combo):
        environment["COMBO_BASE"] = row["combo_base"]
    else:
        environment.pop("COMBO_BASE", None)

    started = time.time()
    with log_path.open("w") as log:
        log.write(f"# {combo} [{row['kind']}] base={row['combo_base']}\n")
        for name, command in steps:
            log.write(f"\n$ {name}: {' '.join(command)}\n")
            log.flush()
            result = subprocess.run(command, cwd=ROOT, env=environment,
                                    stdout=log, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                seconds = round(time.time() - started, 1)
                print(f"  {combo}: FAILED at {name} after {seconds:.0f} s -> {log_path}")
                return {"combination": combo, "status": f"failed at {name}",
                        "seconds": seconds, "steps": len(steps),
                        "log": str(log_path.relative_to(ROOT)),
                        "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    seconds = round(time.time() - started, 1)
    print(f"  {combo}: {seconds:.0f} s")
    return {"combination": combo, "status": "ran", "seconds": seconds,
            "steps": len(steps), "log": str(log_path.relative_to(ROOT)),
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="print each row's step list and run nothing")
    parser.add_argument("--batch", type=int, help="only rows this batch is assigned")
    parser.add_argument("--tier", type=int)
    parser.add_argument("--only", help="one combination name")
    args = parser.parse_args()

    manifest = NODE / "results" / "manifest.csv"
    if not manifest.exists():
        raise SystemExit("no manifest: run plan_manifest.py first")
    forks = inv.forks()
    rows = list(csv.DictReader(manifest.open()))

    outcomes = []
    for row in rows:
        if args.only and row["combination"] != args.only:
            continue
        if args.batch and int(row["assigned_batch"]) != args.batch:
            continue
        if args.tier and int(row["tier"]) != args.tier:
            continue
        if not row["combination"]:
            outcomes.append({"combination": f"tier2 slot (rank {row['rank']})",
                             "status": "pending-selection", "seconds": "", "steps": "",
                             "log": "", "at": ""})
            continue
        if row["built"] != "True":
            # In a dry run the step list of a child nobody has written yet is the most
            # useful thing this script produces: it is the specification the batch that
            # writes it works to.
            if args.dry_run:
                run_row(row, forks, dry=True)
            outcomes.append({"combination": row["combination"],
                             "status": "not-built: the child has no scripts yet",
                             "seconds": "", "steps": "", "log": "", "at": ""})
            continue
        outcomes.append(run_row(row, forks, args.dry_run))

    if args.dry_run:
        skipped = [o for o in outcomes if o["status"] != "dry-run"]
        print(f"\n{len(outcomes) - len(skipped)} row(s) would run; "
              f"{len(skipped)} would not:")
        for o in skipped:
            print(f"    {o['combination']:34s} {o['status']}")
        return

    # Merged into the existing record rather than replacing it: batches 13, 14, 22 and 15
    # each run part of the manifest, and the file has to end up describing all of them.
    path = NODE / "results" / "run_status.csv"
    fields = ["combination", "status", "seconds", "steps", "log", "at"]
    known = {}
    if path.exists():
        known = {r["combination"]: r for r in csv.DictReader(path.open())}
    known.update({o["combination"]: o for o in outcomes})
    order = {r["combination"]: int(r["rank"]) for r in rows if r["combination"]}
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for name in sorted(known, key=lambda n: order.get(n, 999)):
            writer.writerow(known[name])
    ran = sum(1 for o in outcomes if o["status"] == "ran")
    print(f"\n{ran} of {len(outcomes)} row(s) ran -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
