"""The fork inventory, read out of the tree rather than listed anywhere.

A perturbation manifest is a list of analyses that all looked reasonable, and the list of
things that could reasonably have been done differently is exactly the set of alternatives
nodes in `analysis/`. So this module does not carry an inventory: it walks the tree and
finds one. A fork added by a later batch is in the manifest the next time the planner runs,
and a fork someone forgot to add is visibly absent from the tree rather than invisibly
absent from a list.

Batch 5 wrote the inventory out by hand and counted ten forks. The tree now has sixteen --
five that batches 9 to 11 added while building the candidates, and two baseline forks that
the hand-written list omitted although the plan's phase D names one of them. That gap is the
argument for computing it.

## What a fork's *kind* is, and why the manifest needs it

The plan (§ phase D) distinguishes forks by which models they move, because "a comparison
where one side moved and the other did not is not a comparison". The tree encodes the
distinction in its shape, so the kind is read off the fork's position:

| Kind | Where | What re-runs |
|---|---|---|
| `setup` | under `02_setup` | every model, the reference four times |
| `scoring` | under `04_score` | nothing; the stored per-cell scores are re-aggregated |
| `baseline` | under `03_models/01_baselines` | that baseline, **and our reported model** |
| `family` | `03_models/03_candidate` itself | our model only |
| `candidate` | under a family | our model only |

**The `baseline` row is not what batch 5 designed.** It listed the persistence fork as
moving one leaderboard row. Batch 11 put the two required baselines inside the reported
model -- the linear opinion pool takes them as members -- so a fork on how uncertainty is
wrapped around the persistence point now moves the pool as well as the persistence row, and
its reach doubled the moment the family fork was promoted. Nothing about the fork changed;
what changed is what depends on it.

## Naming

A combination is named `<stage>_<child>`, where the stage is the fork's directory name
without its ordering prefix and the child is the child's name without its letter prefix --
`01_observation/a_negBinomial` is `observation_negBinomial`. Thirteen combinations already
exist under that scheme and keep their names, because a combination that is renamed between
batches is a different analysis as far as every file that points at it is concerned.

Two forks need the stage name to be stated rather than derived, and both are recorded in
`STAGE_OVERRIDE` with the reason. `assert_unique_names` is what actually protects the
scheme: any future collision fails the planner instead of quietly merging two analyses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dc_field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ANALYSIS = ROOT / "analysis"

# The stage name a fork's combinations carry, where it is not the fork's own directory name
# with the ordering prefix removed. Both entries are about identity, not taste.
STAGE_OVERRIDE = {
    # Named `family` since batch 9's sweeps: `family_hierNB`, `family_boosted` and
    # `family_ensemble` are on disk and are pointed at from the family leaderboard, the
    # provenance records and three batch reports. `candidate_hierNB` would be the same
    # analysis under a name nothing refers to.
    "03_models/03_candidate": "family",
    # `population` is taken by `a_hierNB/03_population`, which ran two combinations under
    # it in batch 9. Batch 5 warned that population appears twice and asks different
    # questions in the two places: this fork is what the *column* contains, the other is
    # how our model uses it. The column keeps the qualified name because the model fork
    # holds the short one already.
    "02_setup/01_population": "popColumn",
}

# Which models are on the leaderboard, as the names they score under. Read from the
# collected scores rather than declared, so a model added later is counted.
def leaderboard_models(combo: str = "main") -> list[str]:
    path = ANALYSIS / "04_score/01_collect/results" / combo / "models.csv"
    if not path.exists():
        return []
    import csv
    with path.open() as handle:
        return sorted({row["model"] for row in csv.DictReader(handle)})


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    value = m.group(1).strip() if m else ""
    return None if value in ("", "-", "none", "n/a") else value


def suffix(name: str) -> str:
    """`a_negBinomial` -> `negBinomial`; `01_observation` -> `observation`."""
    return name.split("_", 1)[1] if "_" in name else name


@dataclass
class Fork:
    node: Path                      # the alternatives node itself
    stage: str                      # the name its combinations carry
    kind: str                       # setup | scoring | baseline | family | candidate
    main: str                       # directory name of the main-path child
    children: list[str]             # every child, in directory order
    owner: str                      # the model family a candidate fork configures, else "-"
    built: dict[str, bool] = dc_field(default_factory=dict)

    @property
    def rel(self) -> str:
        return str(self.node.relative_to(ROOT))

    @property
    def siblings(self) -> list[str]:
        """The children the main path does not take -- one manifest row each."""
        return [c for c in self.children if c != self.main]

    def combination(self, child: str) -> str:
        return f"{self.stage}_{suffix(child)}"


def _kind(node: Path) -> str:
    rel = node.relative_to(ANALYSIS).as_posix()
    if rel == "03_models/03_candidate":
        return "family"
    if rel.startswith("02_setup/"):
        return "setup"
    if rel.startswith("04_score/"):
        return "scoring"
    if rel.startswith("03_models/01_baselines/"):
        return "baseline"
    if rel.startswith("03_models/03_candidate/"):
        return "candidate"
    raise SystemExit(
        f"{rel} is an alternatives node in a part of the tree the manifest has no rule "
        f"for. Which models a fork moves is a property of where it sits (AGENTS.md §2, "
        f"and batch 5 §2); a fork somewhere new needs that decided before it can be "
        f"perturbed, not defaulted.")


def _built(child: Path) -> bool:
    """Whether this child has anything that could be run.

    A child directory with nothing but the scaffold `/node new` writes is a fork the tree
    declares and does not yet carry. The manifest lists it -- it is a reasonable
    alternative whether or not anyone has coded it -- and says it is not built, which is
    what turns 'we did not run this' into a visible decision rather than a gap.
    """
    scripts = child / "scripts"
    if not scripts.is_dir():
        return False
    return any(p.name != ".gitkeep" for p in scripts.rglob("*") if p.is_file())


def forks() -> list[Fork]:
    """Every alternatives node in the tree, in tree order."""
    out: list[Fork] = []
    for claim in sorted(ANALYSIS.rglob("claim.md")):
        node = claim.parent
        text = claim.read_text()
        if field(text, "kind") != "alternatives":
            continue
        main = field(text, "main-path")
        children = sorted(p.name for p in node.iterdir()
                          if p.is_dir() and (p / "claim.md").exists())
        if main not in children:
            raise SystemExit(f"{node}: main-path {main!r} is not among {children}")
        rel = node.relative_to(ANALYSIS).as_posix()
        kind = _kind(node)
        owner = "-"
        if kind == "candidate":
            owner = node.parent.name
        out.append(Fork(
            node=node,
            stage=STAGE_OVERRIDE.get(rel, suffix(node.name)),
            kind=kind,
            main=main,
            children=children,
            owner=owner,
            built={c: _built(node / c) for c in children},
        ))
    return out


def assert_unique_names(forks_: list[Fork]) -> None:
    """No two forks may produce the same combination name.

    Two analyses sharing a directory under `results/` is the one failure this whole
    mechanism cannot survive: the second would overwrite the first and the manifest would
    report a number the row it names never produced.
    """
    seen: dict[str, str] = {}
    for fork in forks_:
        for child in fork.children:
            name = fork.combination(child)
            if name in seen:
                raise SystemExit(
                    f"combination name {name!r} is claimed by both {seen[name]} and "
                    f"{fork.rel}. Add an entry to STAGE_OVERRIDE with the reason; do not "
                    f"let two analyses share a results directory.")
            seen[name] = fork.rel
