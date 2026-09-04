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

Batch 16 added a third thing a combination decides: **which of the two datasets it is
evaluated on**. Phase E re-runs the frozen set on the held-out year under `__holdout`
names, and the functions at the foot of this file are the one place that suffix is read.

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


# ---------------------------------------------------------------------------
# Which dataset a combination is evaluated on.
#
# Phase E re-runs the frozen perturbation set on the held-out year, and every one of
# its rows is a development combination with `__holdout` appended
# (`05_stability/results/manifest_holdout.csv`). Three things differ on that side and
# nothing else does: the file the setup chain starts from, the backtest scheme, and the
# span the province and training-window forks call "evaluated".
#
# All three are answered here rather than in the six setup scripts that need them. That
# is the shape this project has had to learn four times: a step that discovers something
# and carries its own copy of the rule is a step that goes out of date alone. A holdout
# row must run *the same analysis* as its development twin, differing only in the data it
# faces, and the way to make that checkable is for there to be one place where the
# difference lives.
#
# The suffix is the signal because it is what the frozen manifest already names the rows.
# Deriving the phase from the combination name means the driver sets one variable, COMBO,
# exactly as it does for every other row, and no second switch can be set inconsistently
# with it.
#
# Batch 20 added four more datasets on that same mechanism: the external check runs the
# reported model, unchanged, on the Thai and Vietnamese sibling files, in the two
# arrangements that mirror Laos's development backtest and its held-out year. They are
# datasets and not forks -- the analysis does not move, the country does -- so they are
# suffixes here rather than children anywhere, and `tokens` strips them exactly as it
# strips `__holdout`. Because their spans are properties of those files rather than of
# the Lao one, the **scheme file** became a property of the dataset too; it had been a
# constant repeated in six setup scripts.
# ---------------------------------------------------------------------------

HOLDOUT_SUFFIX = "__holdout"

#: Every dataset a combination can face, and the suffix that names it. The empty suffix
#: is development, which is what a combination with no dataset suffix at all faces.
#: Matched longest-first, so `__thaFinal` is not read as `__tha`.
DATASET_BY_SUFFIX = {
    "": "development",
    HOLDOUT_SUFFIX: "holdout",
    "__tha": "tha",
    "__thaFinal": "thaFinal",
    "__vnm": "vnm",
    "__vnmFinal": "vnmFinal",
}

#: The dataset each combination's setup chain starts from, relative to the repository
#: root. The two Lao files are written by `01_data/01_partition`, the four sibling files
#: by `01_data/03_siblings`; between them those two nodes are the only ones that read
#: anything under `Archive/`.
SOURCE_BY_DATASET = {
    "development": "analysis/01_data/01_partition/results/development_1998-01_2009-12.csv",
    "holdout": "analysis/01_data/01_partition/results/phase_e_1998-01_2010-12.csv",
    "tha": "analysis/01_data/03_siblings/results/THA_development_1998-01_2009-12.csv",
    "thaFinal": "analysis/01_data/03_siblings/results/THA_full_1998-01_2010-12.csv",
    "vnm": "analysis/01_data/03_siblings/results/VNM_development_1998-01_2009-12.csv",
    "vnmFinal": "analysis/01_data/03_siblings/results/VNM_full_1998-01_2010-12.csv",
}

LAO_SCHEME = "analysis/01_data/02_characterise/results/backtest_scheme_chosen.json"
EXTERNAL_SCHEME = "analysis/01_data/03_siblings/results/backtest_scheme_external.json"

#: Which stored scheme file answers for this dataset. Batch 3 fixed the Lao schemes and
#: said neither moves again; the sibling file records the same two arrangements checked
#: against the sibling calendars, because a span is a fact about the file it was read off.
SCHEME_FILE_BY_DATASET = {
    "development": LAO_SCHEME,
    "holdout": LAO_SCHEME,
    "tha": EXTERNAL_SCHEME,
    "thaFinal": EXTERNAL_SCHEME,
    "vnm": EXTERNAL_SCHEME,
    "vnmFinal": EXTERNAL_SCHEME,
}

#: Keys into whichever scheme file answers for the dataset.
SCHEME_KEY_BY_DATASET = {
    "development": "development_scheme",
    "holdout": "phase_e_scheme",
    "tha": "tha_scheme",
    "thaFinal": "thaFinal_scheme",
    "vnm": "vnm_scheme",
    "vnmFinal": "vnmFinal_scheme",
}

SPAN_KEY_BY_DATASET = {
    "development": "development_evaluated_span",
    "holdout": "phase_e_evaluated_span",
    "tha": "tha_evaluated_span",
    "thaFinal": "thaFinal_evaluated_span",
    "vnm": "vnm_evaluated_span",
    "vnmFinal": "vnmFinal_evaluated_span",
}

#: The datasets that are not Laos. Named here so that a step which has to say whether it
#: is looking at the project's own data can ask rather than match on a string.
EXTERNAL_DATASETS = ("tha", "thaFinal", "vnm", "vnmFinal")


def dataset_suffix(name: str | None = None) -> str:
    """The dataset suffix on this combination's name, or `""` for development.

    Longest match wins, so a suffix that is a prefix of another one cannot shadow it.
    """
    name = combo() if name is None else name
    matches = [s for s in DATASET_BY_SUFFIX if s and name.endswith(s)]
    return max(matches, key=len) if matches else ""


def is_holdout(name: str | None = None) -> bool:
    """Is this combination evaluated on the held-out year?

    Specifically the Lao 2010 that plan §3 seals -- not "on some other dataset". The
    driver's seal reads this, and sealing the external check would be sealing a thing the
    plan does not seal.
    """
    return dataset_suffix(name) == HOLDOUT_SUFFIX


def is_external(name: str | None = None) -> bool:
    """Is this combination the external check, on a sibling country's file?"""
    return dataset(name) in EXTERNAL_DATASETS


def dataset(name: str | None = None) -> str:
    """Which of the datasets this combination faces."""
    return DATASET_BY_SUFFIX[dataset_suffix(name)]


def source_dataset(root: Path, name: str | None = None) -> Path:
    """The file the setup chain's first stage reads for this combination."""
    return root / SOURCE_BY_DATASET[dataset(name)]


def scheme_path(name: str | None = None) -> str:
    """The stored backtest-scheme file this combination reads, relative to the root.

    Returned as the repository-relative string rather than as a path, because every
    caller writes it into the specification it produces as the source of the flags it
    used, and a specification naming an absolute path on the machine that ran it is not
    a specification anybody else can read.
    """
    return SCHEME_FILE_BY_DATASET[dataset(name)]


def scheme_file(root: Path, name: str | None = None) -> Path:
    """The same file, resolved."""
    return root / scheme_path(name)


def scheme_key(name: str | None = None) -> str:
    """Which backtest scheme in the stored scheme file this combination is evaluated under."""
    return SCHEME_KEY_BY_DATASET[dataset(name)]


def span_key(name: str | None = None) -> str:
    """Which evaluated span in the stored scheme file this combination's forks read."""
    return SPAN_KEY_BY_DATASET[dataset(name)]


# ---------------------------------------------------------------------------
# What a combination's name says was moved.
#
# A combination is named by the fork children it takes that the main path does not,
# joined by `__`, with `__holdout` appended on the phase-E side: `main`,
# `provinces_reportingOnly__weighting_crpsWeighted__holdout`. Batch 28 needed to ask
# whether one combination is a run of the *same* model another combination configured,
# which is a question about those tokens, so the splitting lives here beside the suffix
# rather than in the one node that first needed it.
# ---------------------------------------------------------------------------

#: A child of the family fork -- the alternatives fork whose children are the model
#: families themselves. It is the one fork a member's own standalone run always moves:
#: candidate 1 is evaluated on its own only under `family_hierNB`, because the main path
#: runs the pool. So a member's evaluation carries this token where the pool's own
#: combination does not, and comparing the two has to allow for it.
FAMILY_TOKEN_PREFIX = "family_"


def tokens(name: str | None = None) -> list[str]:
    """The fork children this combination takes that the main path does not.

    `main` takes none and gives `[]`; a dataset suffix is not one of them, because it
    names the dataset rather than a fork.
    """
    name = combo() if name is None else name
    suffix = dataset_suffix(name)
    stem = name[: -len(suffix)] if suffix else name
    return [] if stem == "main" else stem.split("__")


def implies(combination: str, candidate: str) -> bool:
    """Does `combination` imply `candidate` as a run of one of its own members?

    True when every fork `candidate` moves is one `combination` moves too, family tokens
    aside, and both face the same dataset. The subset is what makes the member the one
    this combination configured; the exception for the family fork is what lets a member
    that runs on its own only under `family_x` be found from a combination that pools it.

    A candidate outside that set may still carry an identically configured run of the
    member -- a fork that moves a different model entirely leaves this one alone -- but it
    is a different analysis, and naming it would put another combination's directory into
    this one's record for no reason beyond which directories happened to exist.
    """
    if dataset(candidate) != dataset(combination):
        return False
    moved = {t for t in tokens(candidate) if not t.startswith(FAMILY_TOKEN_PREFIX)}
    return moved <= set(tokens(combination))
