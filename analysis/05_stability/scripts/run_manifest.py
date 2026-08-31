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

**A fork of the family that is running is the case that rule does not cover**, and batch 14
found it by running into it. `c_ensemble/run.sh` runs `01_weighting/run.sh` at the main
path, as an alternatives parent must, so a row moving the pool's own weighting fork had the
moved child and the main one under one combination and the assembler failed by design. Such
a row therefore takes that family's forks itself and then runs the family's **own scripts**,
read out of its `run.sh` under the `# Own scripts` marker `node.py` writes -- which is what
`02_setup` already gets, one kind up, where the driver names `assemble_setup.py` rather than
calling `02_setup/run.sh`. It is the same fork-blindness this project has now found four
times, in the last place that had it.

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

## The holdout half

`--dataset holdout` runs the frozen phase-E set, `results/manifest_holdout.csv`, whose rows
are the same analyses under `__holdout` names. Nothing about the step lists changes: the
combination name carries the dataset, `analysis/scripts/lib/combos.py` turns the suffix into
the file the setup chain starts from and the backtest scheme it is evaluated under, and
every command issued is the same command the development twin issued. That is the point --
a holdout row that ran different code would not measure what phase E is for.

**One row differs, and it is the `main` row.** On development it runs `conclude.py` and
nothing else, because the main path is the analysis that already ran. On the holdout it has
never run, so it runs the whole pipeline: every setup fork at its main child, the
assembler, both baselines, the reference, the reported family, and the scoring chain. That
is `analysis/run.sh` minus `01_data`, which is not combination-scoped, and minus this node.
It runs first, and every other holdout row inherits from it.

Usage, from the repository root:
  environment/chapenv/bin/python analysis/05_stability/scripts/run_manifest.py --dry-run
  ... --batch 13            only the rows the manifest assigns to that batch
  ... --only trainingWindow_from2004
  ... --dataset holdout     the frozen phase-E set, on the held-out year
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


OWN_SCRIPT = re.compile(r'^"\$PYTHON"\s+"(scripts/[^"]+)"\s*$')


def own_scripts(node: Path) -> list[tuple[str, list[str]]]:
    """A node's own scripts, in the order its own `run.sh` runs them.

    Read out of that file rather than listed here. The driver's rule is that every command
    it issues is one the main path also issues, and a list of a node's scripts kept in the
    driver would be a second copy of its `run.sh` free to fall out of step with it -- the
    same objection this project has made four times now to a step that carries what it
    could read. The block is the one `node.py` generates under `# Own scripts`, and the
    child calls above it are exactly what this function exists to leave out.
    """
    lines = (node / "run.sh").read_text().splitlines()
    if "# Own scripts" not in lines:
        raise SystemExit(f"{node}/run.sh has no '# Own scripts' marker; the driver "
                         f"cannot run this node without also re-running the fork child "
                         f"this row moves")
    steps = [(Path(m.group(1)).stem, python(node / m.group(1)))
             for m in (OWN_SCRIPT.match(line.strip())
                       for line in lines[lines.index("# Own scripts") + 1:]) if m]
    if not steps:
        raise SystemExit(f"{node}/run.sh lists no own scripts under its marker")
    return steps


def steps_for(row: dict, forks: list[inv.Fork],
              full_main: bool = False) -> list[tuple[str, list[str]]]:
    """The ordered commands one combination runs. Named steps, so a log can be read.

    `full_main` is what the holdout's `main` row needs: no fork has moved, and every
    stage still has to run, because on that dataset nothing has. Expressed by moving
    nothing and declaring the setup gate open, so the row goes down the same code path
    every other row does and picks up each fork's main child by the ordinary rule --
    rather than by a second list of the pipeline kept here, which is the failure this
    driver has already had to correct four times.
    """
    if row["kind"] == "main" and not full_main:
        return [("conclude", python(ANALYSIS / "scripts/conclude.py"))]

    if row["kind"] == "main":
        moved: list[tuple[inv.Fork, str]] = []
        kinds = {"setup"}
    else:
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
        internal = [(fork, child) for fork, child in moved if fork.kind == "candidate"]
        for fork, child in internal:
            if fork.owner != family:
                out.append((f"{fork.stage}/{child}", bash(fork.node / child / "run.sh")))

        # A fork of the family that is *running* cannot be taken that way. Its own
        # `run.sh` runs every fork below it at the main path -- that is what an
        # alternatives parent does -- so calling it after the moved child would put both
        # children of one fork under this combination and the family's assembler fails by
        # design. So the family's forks are taken here, the moved child where one moved,
        # and then the family's own scripts, which is what its `run.sh` does minus the
        # child calls. It is the treatment `02_setup` already gets one kind up.
        own = [f for f, _ in internal if f.owner == family]
        node = family_fork.node / family
        if own:
            chosen = {fork.rel: child for fork, child in internal}
            for fork in [f for f in forks if f.owner == family]:
                child = chosen.get(fork.rel, fork.main)
                out.append((f"{fork.stage}/{child}", bash(fork.node / child / "run.sh")))
            out.extend(own_scripts(node))
        else:
            out.append((f"family/{family}", bash(node / "run.sh")))

    out.append(("collect", bash(ANALYSIS / "04_score/01_collect/run.sh")))
    take("scoring")
    out.append(("compare", bash(ANALYSIS / "04_score/03_compare/run.sh")))
    out.append(("conclude", python(ANALYSIS / "scripts/conclude.py")))
    return out


def run_row(row: dict, forks: list[inv.Fork], dry: bool,
            full_main: bool = False) -> dict:
    combo = row["combination"]
    steps = steps_for(row, forks, full_main=full_main)
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
    parser.add_argument("--dataset", choices=("development", "holdout"),
                        default="development",
                        help="which manifest to run: the development set, or the "
                             "phase-E set frozen in batch 15")
    args = parser.parse_args()

    # The two manifests, and the two status files that record what each one did. Kept
    # apart rather than merged on a column: a holdout row is a different analysis facing
    # a different year, and one file holding both would invite a summary over the union.
    holdout = args.dataset == "holdout"
    manifest = NODE / "results" / ("manifest_holdout.csv" if holdout else "manifest.csv")
    status_file = NODE / "results" / (
        "run_status_holdout.csv" if holdout else "run_status.csv")
    if not manifest.exists():
        raise SystemExit(f"no {manifest.name}: run "
                         f"{'freeze_holdout_manifest.py' if holdout else 'plan_manifest.py'}"
                         f" first")
    forks = inv.forks()
    rows = list(csv.DictReader(manifest.open()))

    outcomes = []
    for row in rows:
        if args.only and row["combination"] != args.only:
            continue
        # `assigned_batch` is "-" for the held row, which no batch runs. Selecting by
        # batch has to skip it rather than fail on it: a filter that crashes on the one
        # row it is meant to exclude would have stopped every `--batch` invocation the
        # driver exists to be used with.
        if args.batch and row.get("assigned_batch", "").strip() != str(args.batch):
            continue
        if args.tier and int(row["tier"]) != args.tier:
            continue
        if not row["combination"]:
            outcomes.append({"combination": f"tier2 slot (rank {row['rank']})",
                             "status": "pending-selection", "seconds": "", "steps": "",
                             "log": "", "at": ""})
            continue
        # A holdout row whose development twin was never run has nothing to be
        # reported beside, and phase E's whole shape is the two spreads on one axis.
        # The held row is the only one: it is the main path under a second name, and
        # development did not run it either. Skipping it here keeps the two halves
        # paired at 32 rows rather than adding a thirty-third that exists on one side.
        # Read off the frozen manifest's own column, not off the row's kind.
        if holdout and not row.get("development_skill_score", "").strip():
            outcomes.append({
                "combination": row["combination"],
                "status": "not run: its development twin has no conclusion "
                          f"({row['status']})",
                "seconds": "", "steps": "", "log": "", "at": ""})
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
        outcomes.append(run_row(row, forks, args.dry_run, full_main=holdout))

    if args.dry_run:
        skipped = [o for o in outcomes if o["status"] != "dry-run"]
        print(f"\n{len(outcomes) - len(skipped)} row(s) would run; "
              f"{len(skipped)} would not:")
        for o in skipped:
            print(f"    {o['combination']:34s} {o['status']}")
        return

    # Merged into the existing record rather than replacing it: batches 13, 14, 22 and 15
    # each run part of the manifest, and the file has to end up describing all of them.
    path = status_file
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
