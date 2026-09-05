"""Which models the pool contains — decided once, for everything that has to know.

Candidate 3 is a linear pool over the models this project already has, and two steps of
its node need to know which models those are. `prepare_members.py` needs it because it
runs them; `01_weighting/a_equal/scripts/choose_weighting.py` needs it because an equally
weighted pool's whole specification is *how many members there are and which of them are
the plan's required baselines*, and that has to be registered before the pool runs.

Until this module they were two rules. `prepare_members.py` resolved every alternatives
fork above a contract directory to the child this combination takes; `choose_weighting.py`
globbed for contract directories and counted them. The two agreed until batch 22 gave the
persistence baseline and the climatology baseline a second published construction each,
and from that point the specification said **six members at 1/6 each, two-thirds of the
mass on required baselines** while **four at 1/4** ran. Both statements were printed by
the same run, three lines apart, in every clean-room log the project has.

So: **one rule, in one file, imported by both.** The shape of the pool is a property of the
tree —

* every Chap contract directory under `03_models`, found by globbing for `MLproject`,
  except the pool's own. A model added to the tree joins the pool by existing;
* **one member per model, not one per contract directory.** Every alternatives fork above a
  contract is resolved and only the child this combination takes is a member. The one
  exception is the family fork, `03_candidate`, whose children are the candidate families
  that pooling them is the point of.

**Why a fork is resolved from what ran rather than from the tree alone.** A fork could be
read off `claim.md`'s main path and never touch a result, which would make this a pure
function of the checkout. It is not done that way, because the pool must contain the model
the combination actually scored: under `persistence_negBinomialFloor` the member is
`b_negBinomialFloor`, and no property of the tree says so — the combination does. The
lookup is `combos.resolve_glob`, the same one `04_score` and the family assemblers use, so
a fork is resolved here exactly as it is resolved everywhere else; where no child has
results the fork's own main path answers, which is the case a cold checkout starts in.

That the lookup reads directories is worth being careful about, because a rule that
depends on which combinations happen to have been run is the defect batch 28 removed one
node over. It does not here, and that is checked rather than asserted: the answer this
module gives is identical for all 47 combinations to the membership
`prepare_members.py` recorded when each of them ran, and identical whether or not
`COMBO_BASE` is set. What `COMBO_BASE` moves is the *sentence explaining* how a fork was
resolved, which is why no such sentence is registered in the weighting premise.

Not a step: `scripts/lib/` is a subdirectory, so `node.py` puts it in no node's `run.sh`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MODELS = Path(__file__).resolve().parents[2]
ANALYSIS = MODELS.parent
ROOT = ANALYSIS.parent

sys.path.insert(0, str(ANALYSIS / "scripts" / "lib"))
from combos import resolve_glob  # noqa: E402

#: The pool itself. Its own contract directory is not a member of it.
POOL = MODELS / "03_candidate" / "c_ensemble"

#: The one alternatives fork whose children are all members. Every other fork above a
#: contract chooses between constructions of *one* member, and the pool takes the child
#: this combination takes; see `on_this_combinations_path`.
FAMILY_FORK = MODELS / "03_candidate"

#: chap-core's model contract requires this filename, and it has no suffix to recognise
#: it by, so the glob names it.
CONTRACT_GLOB = "**/scripts/*/MLproject"


def field(text: str, key: str) -> str | None:
    """A `key: value` line of a `claim.md` front matter, or None when it is blank."""
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    value = m.group(1).strip() if m else ""
    return value or None


def contracts() -> list[Path]:
    """Every Chap contract directory the pool could contain, in path order.

    Discovered, not listed: a list here would be a second statement of what models this
    project has, and it would be the statement that goes stale.
    """
    return [p.parent for p in sorted(MODELS.glob(CONTRACT_GLOB))
            if POOL not in [p.parent, *p.parent.parents]]


def alternatives_above(node: Path) -> list[tuple[Path, str]]:
    """Every alternatives fork between `03_models` and `node`, with the child node sits in."""
    out: list[tuple[Path, str]] = []
    current = node
    while current != MODELS and MODELS in current.parents:
        parent = current.parent
        claim = parent / "claim.md"
        if claim.exists() and field(claim.read_text(), "kind") == "alternatives":
            out.append((parent, current.name))
        current = parent
    return out


def taken_child(fork: Path) -> tuple[str, str]:
    """The child of `fork` this combination scores, and how that was resolved.

    Whichever child has a `model_spec.json` under this combination, else under the base
    one, else the child the fork's `claim.md` names as its main path. The first two
    answers come from `resolve_glob`, which is the same lookup every other combination-
    aware step in the project uses, so a fork is resolved here exactly as `04_score`
    resolves it -- one rule, not two that can disagree about which model ran.
    """
    found, where = resolve_glob(fork, "*/results/{combo}/model_spec.json")
    children = sorted({p.parents[2].name for p in found})
    if len(children) > 1:
        raise SystemExit(
            f"{fork.relative_to(ROOT)}: {children} all have results under "
            f"{where!r}. Exactly one child of a fork is on any one combination's path, "
            f"and the pool cannot decide which of two constructions of one member it "
            f"contains.")
    if children:
        return children[0], f"has results under {where!r}"
    main = field((fork / "claim.md").read_text(), "main-path")
    if not main:
        raise SystemExit(f"{fork.relative_to(ROOT)} has no main path and no child with "
                         f"results under this combination; the pool cannot resolve it")
    return main, "the fork's main path; no child has results under this combination"


def on_this_combinations_path(owner: Path) -> tuple[bool, list[dict]]:
    """Whether this contract is the member the combination takes, and the forks it passed.

    **The pool contains one model per member, not one per contract directory.** Discovery
    globs for `MLproject`, and from batch 22 that glob finds two contracts for the
    persistence baseline and two for climatology -- the two published constructions of
    each, which are the children of a fork. Taking both would put two persistence models
    in a pool whose claim is that it pools *the* persistence baseline, and would do it
    silently, under every combination including `main`.

    So every alternatives fork above a contract is resolved and only the child this
    combination takes is a member. The one exception is the family fork itself, whose
    children are the candidate families: pooling those is what this node is for, and they
    are members precisely because they are siblings under it.
    """
    passed = []
    for fork, child in alternatives_above(owner):
        if fork == FAMILY_FORK:
            passed.append({"fork": str(fork.relative_to(ROOT)), "child": child,
                           "resolved_by": "the family fork: every child of it is a member"})
            continue
        taken, how = taken_child(fork)
        passed.append({"fork": str(fork.relative_to(ROOT)), "child": child,
                       "taken": taken, "resolved_by": how})
        if taken != child:
            return False, passed
    return True, passed


def selection() -> list[dict]:
    """Every contract the glob found, whether it is a member, and which fork decided that.

    This is the document `prepare_members.py` writes as `member_selection.json` and the
    list `choose_weighting.py` counts. Both read it from here, so the specification a
    weighting child registers before the run and the membership the pool is built from
    cannot be two different answers.
    """
    rows: list[dict] = []
    for model_dir in contracts():
        owner = model_dir.parents[1]
        taken, forks = on_this_combinations_path(owner)
        rows.append({"model_dir": str(model_dir.relative_to(ROOT)),
                     "node": str(owner.relative_to(ROOT)),
                     "is_a_member": taken, "forks": forks})
    return rows


def members(rows: list[dict] | None = None) -> list[str]:
    """The member nodes, as paths relative to the repository root, in path order."""
    return [r["node"] for r in (selection() if rows is None else rows) if r["is_a_member"]]


def not_members(rows: list[dict] | None = None) -> list[str]:
    """The contracts the glob found that this combination's pool does not contain."""
    return [r["model_dir"] for r in (selection() if rows is None else rows)
            if not r["is_a_member"]]


#: A member under this path is one of the two baselines the plan requires every model to
#: be compared against. It is a location in the tree, not a name, because the plan names
#: the comparison and the tree names the models.
REQUIRED_BASELINES = "01_baselines"


def required_baselines(member_nodes: list[str]) -> list[str]:
    return [n for n in member_nodes if REQUIRED_BASELINES in n]
