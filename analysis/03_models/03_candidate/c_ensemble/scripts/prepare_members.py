"""Assemble the pool's membership: which models it contains and how to run them.

Candidate 3 is a pool over the models this project already has, and the one thing it must
not do is contain copies of them. So this step does not describe the members — it
**discovers** them, and writes down where they are:

* every Chap contract directory in `03_models` that is not this node's own is a **candidate**
  member, found by globbing for `MLproject`. A model added to the tree joins the pool by
  existing, and a model removed from it leaves by the same route. **One of them is a member
  per model, not per directory**: from batch 22 the glob finds two contracts for the
  persistence baseline and two for climatology, because how uncertainty is wrapped around a
  point baseline is a fork with two published answers. Every alternatives fork above a
  contract is therefore resolved and only the child this combination takes is a member —
  except the family fork, whose children are the candidate families this node exists to
  pool. `member_selection.json` records the resolution; a doubled member name is a hard
  failure rather than a silently doubled weight;
* each member's `train` and `predict` command lines are copied out of its own `MLproject`,
  so the pool talks to its members through the platform's contract rather than through an
  interface invented here;
* each member that takes a configuration gets the one its own node assembles, **under this
  combination**. That is what makes the pool follow a perturbation: under a combination
  that moves candidate 1's observation model, the pool's candidate-1 member moves with it,
  because it is configured by the same fork nodes.

`AGENTS.md` §2 sanctions a node running its siblings' scripts — it is how the stability
node executes the paths not taken — and this node does it for the same reason: its claim is
about the other models, so it cannot be answered without them. What it runs is **the fork
children this combination has not already chosen, and that family's own assembler**, which
write configuration and nothing else; it never runs a sibling's evaluation. And it runs them
only where this combination has no configuration already, so a combination whose configuration
was produced by the family's own step is left exactly as that step left it.

Two things are checked rather than assumed, because both would otherwise fail late and
obscurely:

* **the environment covers every member.** This model's `pyproject.toml` is the union of its
  members', and a member that pinned something it does not carry would fail inside a
  subprocess three layers down. The pins are compared here, at the top;
* **exactly one child of each of a family's forks has a configuration under this
  combination.** That is the family assembler's own invariant, and it is inherited by
  running that assembler rather than by reimplementing it.

Writes, under results/$COMBO/:
  members.json            the pool's membership: nodes, contract directories, entry
                          points, configurations, and the sha256 of every file behind them
  member_selection.json   every contract the glob found, whether it is a member of this
                          combination's pool, and which fork decided that
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

NODE = Path(__file__).resolve().parents[1]


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")
MODELS = ROOT / "analysis" / "03_models"
PYTHON = ROOT / "environment" / "chapenv" / "bin" / "python"
OURS = NODE / "scripts" / "ensemble_model"

# The one alternatives fork whose children are all members. Every other fork above a
# contract directory chooses between constructions of *one* member, and the pool takes
# the child this combination takes; see `on_this_combinations_path`.
FAMILY_FORK = MODELS / "03_candidate"

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import resolve_glob  # noqa: E402

DEPENDENCY = re.compile(r'"\s*([A-Za-z0-9_.-]+)\s*==\s*([^"\s]+)\s*"')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins(model_dir: Path) -> dict[str, str]:
    """The exact pins a model's `pyproject.toml` declares."""
    text = (model_dir / "pyproject.toml").read_text()
    block = text.split("dependencies", 1)[-1]
    return {name: version for name, version in DEPENDENCY.findall(block)}


def contract_files(model_dir: Path) -> dict[str, str]:
    return {
        str(p.relative_to(model_dir)): sha256(p)
        for p in sorted(model_dir.rglob("*"))
        if p.is_file() and not any(part.startswith(".") or part == "__pycache__"
                                   for part in p.relative_to(model_dir).parts)
    }


def short_name(model_dir: Path) -> str:
    """`hier_nb_model` -> `hier_nb`. The name the leaderboard already knows the model by."""
    name = model_dir.name
    return name[:-len("_model")] if name.endswith("_model") else name


def entry_points(contract: dict) -> dict:
    out = {}
    for entry in ("train", "predict"):
        spec = contract["entry_points"][entry]
        out[entry] = {"parameters": sorted(spec.get("parameters") or {}),
                      "command": spec["command"]}
    return out


def run(command: list[str], where: str) -> None:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            env={**os.environ, "COMBO": COMBO})
    if result.returncode != 0:
        raise SystemExit(f"preparing member {where}: failed ({result.returncode})\n"
                         f"$ {' '.join(command)}\n{result.stdout}\n{result.stderr}")
    for line in result.stdout.strip().splitlines():
        print(f"    {line}")


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    value = m.group(1).strip() if m else ""
    return value or None


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
                         f"results under {COMBO!r}; the pool cannot resolve it")
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


def ensure_configuration(owner: Path) -> Path:
    """The member family's assembled configuration for this combination, produced if absent.

    Produced by the family's **own** scripts: the fork children this combination still
    needs, then its assembler. Nothing about how that family is configured is decided
    here, which is the point -- a second place that knew how to configure candidate 1
    would be a second place that could be wrong about it.

    **A fork is only run where this combination cannot already resolve it.** A
    candidate-internal row runs its moved child before the pool, so that fork already has
    a choice under `COMBO`; running the fork's main child as well would give the family's
    assembler two children of one fork and it fails by design -- which is what blocked
    every candidate row until batch 14. And a fork this combination did not move is
    answered by `COMBO_BASE`, so it needs nothing run either. The lookup is
    `resolve_glob`, the same one the assembler itself resolves a fork with, because two
    rules for which child a combination takes are two rules that can disagree.

    What remains -- a fork with no child resolvable under this combination or its base --
    is run at its main path, which is the case a fresh combination with no base starts in.
    """
    configuration = owner / "results" / COMBO / "model_configuration.yaml"
    if configuration.exists():
        print(f"  {owner.name}: configuration already assembled under {COMBO!r}")
        return configuration

    print(f"  {owner.name}: assembling its configuration under {COMBO!r}")
    for fork in sorted(p for p in owner.iterdir()
                       if p.is_dir() and (p / "claim.md").exists()):
        found, where = resolve_glob(fork, "*/results/{combo}/model_option_spec.json")
        if found:
            print(f"    {fork.name}: {sorted(p.parents[2].name for p in found)} "
                  f"already chosen under {where!r}")
            continue
        main = field((fork / "claim.md").read_text(), "main-path")
        if not main:
            raise SystemExit(f"{fork} has no main path; the pool cannot configure "
                             f"{owner.name} from it")
        run(["bash", str(fork / main / "run.sh")], f"{owner.name}/{fork.name}/{main}")
    run([str(PYTHON), str(owner / "scripts" / "assemble_candidate_config.py")],
        f"{owner.name}/assemble_candidate_config.py")

    if not configuration.exists():
        raise SystemExit(f"{owner.name}: its assembler did not write {configuration}")
    return configuration


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    ours = pins(OURS)
    members, covariates = [], []
    selection: list[dict] = []
    for contract_path in sorted(MODELS.glob("**/scripts/*/MLproject")):
        model_dir = contract_path.parent
        if OURS in [model_dir, *model_dir.parents] or model_dir == OURS:
            continue
        contract = yaml.safe_load(contract_path.read_text())
        owner = model_dir.parents[1]

        taken, forks_passed = on_this_combinations_path(owner)
        selection.append({"model_dir": str(model_dir.relative_to(ROOT)),
                          "node": str(owner.relative_to(ROOT)),
                          "is_a_member": taken, "forks": forks_passed})
        if not taken:
            continue

        # The environment check, at the top rather than three subprocesses down.
        theirs = pins(model_dir)
        conflict = {name: (version, ours.get(name))
                    for name, version in theirs.items() if ours.get(name) != version}
        if conflict:
            raise SystemExit(
                f"{short_name(model_dir)} pins {conflict}, which "
                f"{OURS.relative_to(ROOT)}/pyproject.toml does not carry at the same "
                f"version. The pool runs its members in its own interpreter, so its "
                f"environment must be the union of theirs; add the pin there rather "
                f"than loosening it here.")

        needs_configuration = (owner / "scripts" / "assemble_candidate_config.py").exists()
        configuration = ensure_configuration(owner) if needs_configuration else None
        specification = None
        if configuration:
            specification = json.loads(
                (owner / "results" / COMBO / "candidate_spec.json").read_text())
            for name in specification["additional_continuous_covariates"]:
                if name not in covariates:
                    covariates.append(name)

        members.append({
            "name": short_name(model_dir),
            "contract_name": contract["name"],
            "node": str(owner.relative_to(ROOT)),
            "model_dir": str(model_dir.relative_to(ROOT)),
            "model_files_sha256": contract_files(model_dir),
            "entry_points": entry_points(contract),
            "dependencies": theirs,
            "model_config": (str(configuration.relative_to(ROOT)) if configuration
                             else None),
            "model_config_sha256": sha256(configuration) if configuration else None,
            "model_config_contents": (yaml.safe_load(configuration.read_text())
                                      if configuration else None),
            "configured_by": specification["choices"] if specification else None,
        })

    if not members:
        raise SystemExit(f"no member contracts found under {MODELS}; the pool has "
                         f"nothing to pool")

    # Two members under one name is the failure `on_this_combinations_path` exists to
    # prevent, stated as an assertion rather than trusted to it. The pool weights its
    # members equally, so a doubled member is a doubled weight, and the leaderboard would
    # carry one row for two models. Checked here because the names are what every file
    # downstream -- members.json, the fitted object, models.csv -- identifies them by.
    doubled = sorted({m["name"] for m in members
                      if sum(1 for other in members if other["name"] == m["name"]) > 1})
    if doubled:
        raise SystemExit(
            f"the pool would contain {doubled} twice under one name, from "
            f"{[m['model_dir'] for m in members if m['name'] in doubled]}. Two contract "
            f"directories resolved onto this combination's path; a fork above one of "
            f"them is not being taken.")

    # How discovery narrowed, as a file. It is beside `members.json` rather than inside it
    # because the pool's configuration carries `members.json`'s sha256 and the model
    # refuses to run when the two disagree -- so a line of prose added to that file
    # re-hashes the reported model's configuration and forces the headline analysis to be
    # re-run to say it. The account belongs in the record either way; this is where it
    # costs nothing.
    (out / "member_selection.json").write_text(json.dumps({
        "combo": COMBO,
        "resolution": "one member per model, not one per contract directory: every "
                      "alternatives fork above a contract is resolved to the child this "
                      "combination takes. The family fork is the exception -- pooling "
                      "its children is what this node is for.",
        "contracts": selection,
    }, indent=1, sort_keys=True) + "\n")

    document = {
        "combo": COMBO,
        "node": str(NODE.relative_to(ROOT)),
        "discovered_by": "glob analysis/03_models/**/scripts/*/MLproject, excluding "
                         "this node's own contract directory",
        "members": members,
        "additional_continuous_covariates": covariates,
        "pool_environment_pins": ours,
    }
    (out / "members.json").write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")

    listed = ", ".join(m["name"] for m in members)
    off_path = [s["model_dir"] for s in selection if not s["is_a_member"]]
    print(f"ensemble members[{COMBO}]: {len(members)} — {listed}; covariates "
          f"{covariates or 'none'} -> {out / 'members.json'}"
          + (f"; not on this combination's path: {off_path}" if off_path else ""))


if __name__ == "__main__":
    main()
