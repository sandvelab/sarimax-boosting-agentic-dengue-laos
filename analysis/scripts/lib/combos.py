"""Which combination a node is running under, and where it may inherit from.

Every node below `01_data` reads its inputs from and writes its outputs to
`results/$COMBO/`, and `COMBO` defaults to `main`. That much has been true since batch 6
and needs no library. This module exists for the second half of the mechanism, which
batch 5's design named and no batch had yet needed:

> A combination that changes only a candidate-internal fork reuses the reference and
> baseline scores from the setup combination it shares, and `manifest.csv` carries the
> reuse as a column, so which numbers were computed and which were inherited is on the
> face of the file rather than in the driver's control flow.

`COMBO_BASE` names that shared combination. A node running under `COMBO=cov_rich` with
`COMBO_BASE=main` writes its own results under `cov_rich`, and where it needs something
no step of `cov_rich` produced -- the assembled dataset, the choice taken at a fork this
combination did not move, another model's evaluation -- it takes `main`'s.

Three properties, each deliberate.

**Inheritance is per artefact, not per combination.** `resolve` asks whether *this* file
exists under `COMBO` before falling back, so a combination that recomputes one thing and
inherits ten is expressed by running one step, not by declaring anything.

**Inheritance is recorded, never silent.** Every function returns the combination the
artefact came from alongside the path, and the callers write it into the specification
they produce. A number that was inherited is then visibly inherited in the file that
reports it, which is the whole reason the mechanism is allowed at all.

**With `COMBO_BASE` unset there is no fallback.** `bash analysis/run.sh` sets neither
variable, so the main path resolves everything under `main` and a missing input is an
error rather than a quiet substitution. The reported analysis cannot inherit from
anything, because there is nothing for it to inherit from.

Not a step: `scripts/lib/` is a subdirectory, so `node.py` does not put it in any node's
`run.sh`. It is imported by the scripts that need it.
"""

from __future__ import annotations

import os
from pathlib import Path


def combo() -> str:
    """The combination this process is running under."""
    return os.environ.get("COMBO", "main")


def base() -> str | None:
    """The combination this one may inherit from, or None when it may not.

    A combination is never its own base: that would be a fallback to the directory the
    lookup already failed in, which can only hide the failure.
    """
    name = os.environ.get("COMBO_BASE") or None
    return None if name == combo() else name


def candidates() -> list[str]:
    """The combinations to look in, nearest first."""
    return [combo(), *( [base()] if base() else [] )]


def resolve(results_root: Path, artefact: str) -> tuple[Path, str]:
    """Find `artefact` under `results_root`, in this combination or in the base one.

    Returns the path and the combination it was found in. Raises with both places named
    rather than returning something that does not exist, because every caller of this
    is a step whose next line would otherwise fail on a path it cannot explain.
    """
    tried = []
    for name in candidates():
        path = results_root / name / artefact
        tried.append(path)
        if path.exists():
            return path, name
    where = "\n  ".join(str(p) for p in tried)
    raise SystemExit(
        f"no {artefact!r} for combination {combo()!r}"
        + (f" or its base {base()!r}" if base() else "")
        + f"; looked in\n  {where}\nThe step that produces it has not run.")


def resolve_glob(root: Path, pattern: str) -> tuple[list[Path], str]:
    """Expand `pattern` with `{combo}` filled in, in this combination or in the base one.

    Returns the matches and the combination they came from. The first combination with
    any match wins outright: a fork whose children have results under both combinations
    is answered by the nearer one, and matches are never mixed across combinations,
    because a merged answer would describe an analysis that never ran.
    """
    for name in candidates():
        found = sorted(root.glob(pattern.format(combo=name)))
        if found:
            return found, name
    return [], combo()
