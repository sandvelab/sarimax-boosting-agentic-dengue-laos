"""The one way a combination other than the main path is run.

`AGENTS.md` §2 says the paths not taken are executed by the stability node, which calls its
siblings' main scripts. This module is the machinery that does that: given a manifest row it
builds the ordered list of commands the combination runs -- every one of them a `run.sh` or a
node script the main path also runs -- and executes them with `COMBO` set.

It was `run_manifest.py`'s own code until batch 20, and it moved here for the reason this
project has moved code before: a second caller appeared. `06_external` runs the reported
model, unchanged, on the sibling countries' files, which is the same operation on a different
dataset -- and an external row that ran a second implementation of "the pipeline" would not
be the check it claims to be. So there is one implementation, in a `lib/`, and both callers
import it, exactly as every model in the project reaches `chap eval` through one function.

`scripts/lib/` is a subdirectory, so `node.py` does not put this in any node's `run.sh`. It
is a library, not a step.

The rules it encodes, and why each is not obvious, are in `run_manifest.py`'s docstring,
which remains where the perturbation set's own reasoning lives.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inventory as inv  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
ANALYSIS = ROOT / "analysis"
PYTHON = ROOT / "environment/chapenv/bin/python"


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

    `full_main` is what the holdout's `main` row needs, and every external row: no fork has
    moved, and every stage still has to run, because on that dataset nothing has. Expressed
    by moving nothing and declaring the setup gate open, so the row goes down the same code
    path every other row does and picks up each fork's main child by the ordinary rule --
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


def run_row(row: dict, forks: list[inv.Fork], dry: bool, logs: Path,
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

    logs.mkdir(parents=True, exist_ok=True)
    log_path = logs / f"{combo}.log"
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
