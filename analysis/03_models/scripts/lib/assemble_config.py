"""The one way a candidate family's configuration is assembled from the forks above it.

Every family under `03_candidate` decides what it is at a set of fork nodes, and every one
of them then has to do the same four things: find whichever child of each fork ran for this
combination, merge their option values into one document without letting two forks own the
same option, derive this component's seed from the project seed, and write the single
`model_configuration.yaml` that `chap eval` is pointed at with a `candidate_spec.json`
saying where every part of it came from.

Until batch 14 each family did that in its own near-copy of one script. Batch 10 logged the
duplication, batch 11 logged it again and scheduled the lift here, because rewriting those
scripts changes their sha256 and that hash is in the provenance record of every combination
they configured -- so the lift belongs in the batch that re-runs those combinations anyway.
This is that lift, and the argument for it is `chap_eval.py`'s one node up: a copy per model
is a set of copies that will drift, and the drift is invisible because each copy runs.

**It is a library, not a step.** `scripts/lib/` is a subdirectory, so `node.py` puts it in
no node's `run.sh`. The steps are the one-screen runners at the family nodes, which say
which candidate they are and what, if anything, is particular about it -- the shape
`04_score/scripts/lib/aggregate.py` gave the weighting fork's three children one node over.

**This is the route model configuration takes into an `MLproject` model.** It is
chap-core's own: `chap eval --model-configuration-yaml <file>` parses the file into a
`ModelConfiguration` (`user_option_values` and `additional_continuous_covariates`, extra
fields forbidden), writes it back out as `model_configuration_for_run.yaml` in the run
directory, and substitutes that filename for the `{model_config}` placeholder in the
model's entry points. The model reads its own configuration from a file, so the
configuration a run used is a stored artifact of that run rather than a command line nobody
kept.

**The seed enters here.** Rule 6 asks for one project seed derived downward, so each family
derives its own component seed from `readme-at-start.md`'s project seed by
`analysis/scripts/lib/project_seed.py`, **from that family's own node path**. Three
candidates therefore draw from three seeds with one number behind them all, and the number a
model used is in a file beside its results.

Writes, under the calling node's results/$COMBO/:
  model_configuration.yaml   what chap eval is pointed at
  candidate_spec.json        the choices, the merged options and the seed derivation
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import yaml

ANALYSIS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ANALYSIS / "scripts" / "lib"))
from combos import resolve_glob  # noqa: E402
from project_seed import component_seed  # noqa: E402

ROUTE = ("chap eval --model-configuration-yaml -> ModelConfiguration -> "
         "model_configuration_for_run.yaml -> {model_config} in the MLproject "
         "entry points")


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


def forks(node: Path) -> list[Path]:
    """The fork nodes under `node`, in the order the node runs them.

    Discovered rather than listed, for the same reason the child of each fork is: batch 9
    added a fifth and a sixth fork to candidate 1, and a script carrying the count would
    have had to be edited to notice them -- which is a script that can be wrong about
    what the model is while still running.
    """
    return sorted(p for p in node.iterdir() if p.is_dir() and (p / "claim.md").exists())


def chosen_child(fork: Path, combo: str) -> tuple[Path, str]:
    """The one child of `fork` that ran in this combination, and where it ran.

    Searched for, never named: it is what lets the stability driver swap a child without
    this code or anything downstream of it changing.

    A combination that moved one fork leaves the others untouched, so a fork with no
    child under `COMBO` is answered by `COMBO_BASE` -- the choice this combination did
    not change. The combination that answered is returned and recorded, because a
    configuration assembled partly from another combination's choices must say so.
    """
    found, from_combo = resolve_glob(fork, "*/results/{combo}/model_option_spec.json")
    if len(found) != 1:
        raise SystemExit(
            f"{fork.name}: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(fork.parent)) for p in found]}")
    return found[0], from_combo


def assemble(node: Path, *, candidate: str,
             options_first: dict | None = None,
             covariates_first: list[str] | None = None,
             spec_extra: dict | None = None) -> tuple[dict, Path]:
    """Merge this family's fork choices into one configuration and write both files.

    `options_first` and `covariates_first` are what the family brings to the merge before
    any fork speaks -- candidate 3's pool carries the path and hash of its membership
    document and the union of its members' covariates, and neither is an option value any
    fork owns. `spec_extra` is what its `candidate_spec.json` records beyond the common
    fields. The other two families pass none of the three, which is the whole of what
    distinguishes them from each other.
    """
    root = repo_root(node)
    combo = os.environ.get("COMBO", "main")
    out = node / "results" / combo
    out.mkdir(parents=True, exist_ok=True)

    stages: list[dict] = []
    options: dict = dict(options_first or {})
    covariates: list[str] = list(covariates_first or [])
    for fork in forks(node):
        child, from_combo = chosen_child(fork, combo)
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

    seed = component_seed(root, str(node.relative_to(root)))
    options["seed"] = seed["seed"]

    configuration = {
        "user_option_values": options,
        "additional_continuous_covariates": covariates,
    }
    (out / "model_configuration.yaml").write_text(
        yaml.safe_dump(configuration, sort_keys=True, default_flow_style=False))

    spec = {
        "combo": combo,
        "candidate": candidate,
        "node": str(node.relative_to(root)),
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
        **(spec_extra or {}),
        "seed_derivation": seed,
        "route": ROUTE,
        "stages": stages,
    }
    (out / "candidate_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")
    return spec, out


def moved_here(spec: dict) -> list[str]:
    """The choices this combination took itself, as `stage=child`; the rest are inherited."""
    return [f"{stage}={spec['choices'][stage]}"
            for stage, where in spec["choice_combos"].items() if where == spec["combo"]]
