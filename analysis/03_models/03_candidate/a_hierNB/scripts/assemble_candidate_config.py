"""Assemble the candidate's configuration from the four choices above it.

The four forks under this node each take one decision about what the model is. This
script closes that chain the way `02_setup/scripts/assemble_setup.py` closes the setup
chain, and for the same reason: the model must not have to know how many choices there
are or which of them are forks. It reads whichever child of each fork ran for this
combination, merges their option values into one document, and writes the single
configuration file that `chap eval` is then pointed at.

**This is the route model configuration takes into an `MLproject` model**, which batches 2,
4 and 7 all left open because no model had needed it. It is chap-core's own: `chap eval
--model-configuration-yaml <file>` parses the file into a `ModelConfiguration`
(`user_option_values` and `additional_continuous_covariates`, extra fields forbidden),
writes it back out as `model_configuration_for_run.yaml` in the run directory, and
substitutes that filename for the `{model_config}` placeholder in the `MLproject` entry
points. The model reads its own configuration from a file, so the configuration a run used
is a stored artifact of that run rather than a command line nobody kept.

**The seed enters here.** The model draws from a posterior and is therefore the first
component in this project with anything to seed. Rule 6 asks for one project seed derived
downward, so the seed is derived from `readme-at-start.md`'s project seed by
`analysis/scripts/lib/project_seed.py` and written into the configuration -- which means
the number the model used is in a file beside its results, and re-deriving it needs only
the project seed and this node's path.

Writes, under results/$COMBO/:
  model_configuration.yaml   what chap eval is pointed at
  candidate_spec.json        the four choices, the merged options, and the seed derivation
"""

from __future__ import annotations

import hashlib
import json
import os
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

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import resolve_glob  # noqa: E402
from project_seed import component_seed  # noqa: E402


def forks() -> list[Path]:
    """The fork nodes under this one, in the order the node runs them.

    Discovered rather than listed, for the same reason the child of each fork is: batch 9
    added a fifth and a sixth fork to this node, and a script carrying the count would
    have had to be edited to notice them -- which is a script that can be wrong about
    what the model is while still running.
    """
    return sorted(p for p in NODE.iterdir() if p.is_dir() and (p / "claim.md").exists())


def chosen_child(fork: Path) -> tuple[Path, str]:
    """The one child of `fork` that ran in this combination, and where it ran.

    Searched for, never named: it is what lets the stability driver swap a child without
    this script or anything downstream of it changing.

    A combination that moved one fork leaves the others untouched, so a fork with no
    child under `COMBO` is answered by `COMBO_BASE` -- the choice this combination did
    not change. The combination that answered is returned and recorded, because a
    configuration assembled partly from another combination's choices must say so.
    """
    found, from_combo = resolve_glob(fork, "*/results/{combo}/model_option_spec.json")
    if len(found) != 1:
        raise SystemExit(
            f"{fork.name}: expected exactly one child with results for combination "
            f"{COMBO!r}, found {[str(p.relative_to(NODE)) for p in found]}")
    return found[0], from_combo


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    stages = []
    options: dict = {}
    covariates: list[str] = []
    for fork in forks():
        child, from_combo = chosen_child(fork)
        spec = json.loads(child.read_text())
        spec["chosen_under_combo"] = from_combo
        stages.append(spec)
        # A key set by two stages would mean two forks disagreeing about the same
        # property of the model, which is a design error in the tree rather than a
        # value to resolve here.
        clash = sorted(set(spec["user_option_values"]) & set(options))
        if clash:
            raise SystemExit(f"{fork} sets option(s) {clash} that an earlier stage "
                             f"already set; two forks cannot own the same option")
        options.update(spec["user_option_values"])
        for name in spec["additional_continuous_covariates"]:
            if name not in covariates:
                covariates.append(name)

    seed = component_seed(ROOT, str(NODE.relative_to(ROOT)))
    options["seed"] = seed["seed"]

    configuration = {
        "user_option_values": options,
        "additional_continuous_covariates": covariates,
    }
    (out / "model_configuration.yaml").write_text(
        yaml.safe_dump(configuration, sort_keys=True, default_flow_style=False))

    spec = {
        "combo": COMBO,
        "candidate": "hier_nb",
        "node": str(NODE.relative_to(ROOT)),
        "configuration": "model_configuration.yaml",
        "configuration_sha256": hashlib.sha256(
            (out / "model_configuration.yaml").read_bytes()).hexdigest(),
        "user_option_values": options,
        "additional_continuous_covariates": covariates,
        "choices": {s["stage"]: s["choice"] for s in stages},
        "choice_nodes": {s["stage"]: s["node"] for s in stages},
        # Which combination each choice was taken under. All `combo` on the main path;
        # a combination that moved one fork shows that one fork as its own and the rest
        # inherited, which is the whole description of what the combination is.
        "choice_combos": {s["stage"]: s["chosen_under_combo"] for s in stages},
        "seed_derivation": seed,
        "route": ("chap eval --model-configuration-yaml -> ModelConfiguration -> "
                  "model_configuration_for_run.yaml -> {model_config} in the MLproject "
                  "entry points"),
        "stages": stages,
    }
    (out / "candidate_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    moved = [f"{stage}={spec['choices'][stage]}"
             for stage, where in spec["choice_combos"].items() if where == COMBO]
    print(f"candidate[{COMBO}]: {spec['choices']}, covariates {covariates}, "
          f"seed {seed['seed']}"
          + (f"; taken here: {moved}" if COMBO != "main" else "")
          + f" -> {out}")


if __name__ == "__main__":
    main()
