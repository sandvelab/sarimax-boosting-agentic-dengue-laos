"""Assemble candidate 3's configuration from the choice above it and the pool's members.

The same mechanism the other two candidates use, and for the same reason: the model must
not have to know how many choices there are or which of them are forks. This script reads
whichever child of each fork ran for this combination, merges their option values into one
document, and writes the single configuration file that `chap eval` is then pointed at —
chap-core's own route, `--model-configuration-yaml` → `ModelConfiguration` →
`model_configuration_for_run.yaml` → the `{model_config}` placeholder in the entry points.

What is particular to this candidate is the second input. The pool's membership is not an
option value — it is a document, listing four contract directories, their entry points,
their configurations and the sha256 of every file behind them — so the configuration
carries **the path to that document and its hash** rather than its contents. The model
refuses to run if the two disagree, which is what stops a members file edited after
assembly from producing a run whose record names a pool it did not contain.

**The seed enters here**, derived from the project seed in `readme-at-start.md` by
`analysis/scripts/lib/project_seed.py`, from this node's own path. Candidate 3 therefore
draws from a different component seed than either of the models it pools, which is what
Rule 6's "one seed derived downward" means: three components of one project, three
derivations, one number behind them all. The seed here governs only the pool's own draw —
which member each of the thousand samples comes from. The members draw from their own
seeds, through their own entry points.

**The covariates are the union of the members'.** The pool needs every column any member
needs, and no member can be handed a frame missing one; asking for the union is the only
setting that is correct whatever the members turn out to be.

**On the duplication with the other two assemblers.** Batch 10 logged that the shared part
belongs in `03_models/scripts/lib/` and named this batch as where the lift belongs. It is
not done here, and the reason is batch 9's own rule rather than reluctance: rewriting
`a_hierNB/scripts/assemble_candidate_config.py` changes its sha256, and that hash is in the
provenance record of every combination those assemblers configured — thirteen of them,
whose results would then name a script that never produced them. The lift is therefore
**scheduled rather than skipped**: batches 13 and 14 re-run every combination in the frozen
manifest, which is the moment when regenerating those records costs nothing extra. Logged
here, in the node's claim and in the plan's §4b, rather than in nobody's notes.

Writes, under results/$COMBO/:
  model_configuration.yaml   what chap eval is pointed at
  candidate_spec.json        the choices, the merged options, the members and the seed
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

    Discovered rather than listed, as in the sibling families: a script carrying the count
    would have to be edited to notice a fork added later, which is a script that can be
    wrong about what the model is while still running.
    """
    return sorted(p for p in NODE.iterdir() if p.is_dir() and (p / "claim.md").exists())


def chosen_child(fork: Path) -> tuple[Path, str]:
    """The one child of `fork` that ran in this combination, and where it ran."""
    found, from_combo = resolve_glob(fork, "*/results/{combo}/model_option_spec.json")
    if len(found) != 1:
        raise SystemExit(
            f"{fork.name}: expected exactly one child with results for combination "
            f"{COMBO!r}, found {[str(p.relative_to(NODE)) for p in found]}")
    return found[0], from_combo


def main() -> None:
    out = NODE / "results" / COMBO
    members_file = out / "members.json"
    if not members_file.exists():
        raise SystemExit(f"no membership for combination {COMBO!r}: {members_file} is "
                         f"missing. scripts/prepare_members.py runs first.")
    membership = json.loads(members_file.read_text())

    stages = []
    options: dict = {}
    covariates: list[str] = list(membership["additional_continuous_covariates"])
    for fork in forks():
        child, from_combo = chosen_child(fork)
        spec = json.loads(child.read_text())
        spec["chosen_under_combo"] = from_combo
        stages.append(spec)
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
    options["members_file"] = str(members_file.relative_to(ROOT))
    options["members_sha256"] = hashlib.sha256(members_file.read_bytes()).hexdigest()

    configuration = {
        "user_option_values": options,
        "additional_continuous_covariates": covariates,
    }
    (out / "model_configuration.yaml").write_text(
        yaml.safe_dump(configuration, sort_keys=True, default_flow_style=False))

    spec = {
        "combo": COMBO,
        "candidate": "ensemble",
        "node": str(NODE.relative_to(ROOT)),
        "configuration": "model_configuration.yaml",
        "configuration_sha256": hashlib.sha256(
            (out / "model_configuration.yaml").read_bytes()).hexdigest(),
        "user_option_values": options,
        "additional_continuous_covariates": covariates,
        "choices": {s["stage"]: s["choice"] for s in stages},
        "choice_nodes": {s["stage"]: s["node"] for s in stages},
        "choice_combos": {s["stage"]: s["chosen_under_combo"] for s in stages},
        "members": [
            {"name": m["name"], "node": m["node"], "model_dir": m["model_dir"],
             "model_config": m["model_config"], "configured_by": m["configured_by"]}
            for m in membership["members"]],
        "members_file": options["members_file"],
        "members_sha256": options["members_sha256"],
        "seed_derivation": seed,
        "route": ("chap eval --model-configuration-yaml -> ModelConfiguration -> "
                  "model_configuration_for_run.yaml -> {model_config} in the MLproject "
                  "entry points"),
        "stages": stages,
    }
    (out / "candidate_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    moved = [f"{stage}={spec['choices'][stage]}"
             for stage, where in spec["choice_combos"].items() if where == COMBO]
    print(f"ensemble[{COMBO}]: {spec['choices']}, "
          f"{len(spec['members'])} members, covariates {covariates or 'none'}, "
          f"seed {seed['seed']}"
          + (f"; taken here: {moved}" if COMBO != "main" else "")
          + f" -> {out}")


if __name__ == "__main__":
    main()
