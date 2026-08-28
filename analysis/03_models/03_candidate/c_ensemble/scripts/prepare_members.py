"""Assemble the pool's membership: which models it contains and how to run them.

Candidate 3 is a pool over the models this project already has, and the one thing it must
not do is contain copies of them. So this step does not describe the members — it
**discovers** them, and writes down where they are:

* every Chap contract directory in `03_models` that is not this node's own is a member,
  found by globbing for `MLproject`. A model added to the tree joins the pool by existing,
  and a model removed from it leaves by the same route;
* each member's `train` and `predict` command lines are copied out of its own `MLproject`,
  so the pool talks to its members through the platform's contract rather than through an
  interface invented here;
* each member that takes a configuration gets the one its own node assembles, **under this
  combination**. That is what makes the pool follow a perturbation: under a combination
  that moves candidate 1's observation model, the pool's candidate-1 member moves with it,
  because it is configured by the same fork nodes.

`AGENTS.md` §2 sanctions a node running its siblings' scripts — it is how the stability
node executes the paths not taken — and this node does it for the same reason: its claim is
about the other models, so it cannot be answered without them. What it runs is each family's
**fork children on the main path and that family's own assembler**, which write configuration
and nothing else; it never runs a sibling's evaluation. And it runs them only where this
combination has no configuration already, so a combination whose configuration was produced
by the family's own step is left exactly as that step left it.

Two things are checked rather than assumed, because both would otherwise fail late and
obscurely:

* **the environment covers every member.** This model's `pyproject.toml` is the union of its
  members', and a member that pinned something it does not carry would fail inside a
  subprocess three layers down. The pins are compared here, at the top;
* **exactly one child of each of a family's forks has a configuration under this
  combination.** That is the family assembler's own invariant, and it is inherited by
  running that assembler rather than by reimplementing it.

Writes, under results/$COMBO/:
  members.json   the pool's membership: nodes, contract directories, entry points,
                 configurations, and the sha256 of every file behind them
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


def ensure_configuration(owner: Path) -> Path:
    """The member family's assembled configuration for this combination, produced if absent.

    Produced by the family's **own** scripts: each of its forks' main-path children, then
    its assembler. Nothing about how that family is configured is decided here, which is
    the point -- a second place that knew how to configure candidate 1 would be a second
    place that could be wrong about it.
    """
    configuration = owner / "results" / COMBO / "model_configuration.yaml"
    if configuration.exists():
        print(f"  {owner.name}: configuration already assembled under {COMBO!r}")
        return configuration

    print(f"  {owner.name}: assembling its configuration under {COMBO!r} "
          f"from its forks' main paths")
    for fork in sorted(p for p in owner.iterdir()
                       if p.is_dir() and (p / "claim.md").exists()):
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
    for contract_path in sorted(MODELS.glob("**/scripts/*/MLproject")):
        model_dir = contract_path.parent
        if OURS in [model_dir, *model_dir.parents] or model_dir == OURS:
            continue
        contract = yaml.safe_load(contract_path.read_text())
        owner = model_dir.parents[1]

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
    print(f"ensemble members[{COMBO}]: {len(members)} — {listed}; covariates "
          f"{covariates or 'none'} -> {out / 'members.json'}")


if __name__ == "__main__":
    main()
