"""Assemble candidate 2's configuration from the two choices above it.

The same mechanism candidate 1 uses, and deliberately the same: the model must not have to
know how many choices there are or which of them are forks. This script reads whichever
child of each fork ran for this combination, merges their option values into one document,
and writes the single configuration file that `chap eval` is then pointed at —
chap-core's own route, `--model-configuration-yaml` → `ModelConfiguration` →
`model_configuration_for_run.yaml` → the `{model_config}` placeholder in the entry points.

**The seed enters here**, derived from the project seed in `readme-at-start.md` by
`analysis/scripts/lib/project_seed.py`, from this node's own path. Candidate 2 therefore
draws from a different component seed than candidate 1, which is what Rule 6's "one seed
derived downward" means: two components of one project, two derivations, one number behind
them both.

**This script is a near-copy of `a_hierNB/scripts/assemble_candidate_config.py`, and the
duplication is a logged decision rather than an oversight.** Lifting the shared part into
`03_models/scripts/lib/` is the right end state — it is the argument `chap_eval.py` makes
about a copy per model being a set of copies that will drift — but doing it in this batch
would rewrite the script that produced the reported main path's configuration, whose hash
is in a provenance record and whose results would have to be regenerated to keep that
record true. Batch 11 adds a third candidate and is where the lift belongs. Until then the
duplication is here, in writing, rather than in nobody's notes.

Writes, under results/$COMBO/:
  model_configuration.yaml   what chap eval is pointed at
  candidate_spec.json        the two choices, the merged options, and the seed derivation
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

    Discovered rather than listed: a script carrying the count would have to be edited to
    notice a fork added later, which is a script that can be wrong about what the model
    is while still running.
    """
    return sorted(p for p in NODE.iterdir() if p.is_dir() and (p / "claim.md").exists())


def chosen_child(fork: Path) -> tuple[Path, str]:
    """The one child of `fork` that ran in this combination, and where it ran.

    Searched for, never named: it is what lets the stability driver swap a child without
    this script or anything downstream of it changing. A fork with no child under `COMBO`
    is answered by `COMBO_BASE`, and the combination that answered is returned so that a
    configuration assembled partly from another combination's choices says so.
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
        # property of the model, which is a design error in the tree rather than a value
        # to resolve here.
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
        "candidate": "boosted",
        "node": str(NODE.relative_to(ROOT)),
        "configuration": "model_configuration.yaml",
        "configuration_sha256": hashlib.sha256(
            (out / "model_configuration.yaml").read_bytes()).hexdigest(),
        "user_option_values": options,
        "additional_continuous_covariates": covariates,
        "choices": {s["stage"]: s["choice"] for s in stages},
        "choice_nodes": {s["stage"]: s["node"] for s in stages},
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
    print(f"boosted[{COMBO}]: {spec['choices']}, covariates {covariates}, "
          f"seed {seed['seed']}"
          + (f"; taken here: {moved}" if COMBO != "main" else "")
          + f" -> {out}")


if __name__ == "__main__":
    main()
