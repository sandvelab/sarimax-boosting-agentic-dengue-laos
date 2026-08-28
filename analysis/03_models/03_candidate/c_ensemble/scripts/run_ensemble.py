"""Run the ensemble candidate through Chap's evaluation.

The model itself is `scripts/ensemble_model/` -- a Chap model contract directory with its
own `pyproject.toml` and `uv.lock`, so chap-core builds its environment from a lockfile
that travels with the model. What the model does, and why the pool is a pool of
distributions rather than of point forecasts, is documented there and in this node's claim.

This script chooses nothing. The dataset and the backtest scheme come from
`02_setup/results/$COMBO/`; the membership comes from `prepare_members.py` and the
configuration from `assemble_candidate_config.py`; and the call to `chap eval` is the one
every model of ours goes through, in `03_models/scripts/lib/chap_eval.py`. Using the same
one is what makes candidate 3's score comparable with its own members' rather than merely
similar to them -- which matters more here than anywhere else in the project, because the
thing being asked is whether pooling those members beats choosing between them.

The seed is not set here either. It is derived from the project seed by the assembler and
travels inside the configuration file, which is what puts it in the model's own record.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[1] / "scripts" / "lib"))

from chap_eval import run_local_model  # noqa: E402

COMBO = os.environ.get("COMBO", "main")
configuration = NODE / "results" / COMBO / "model_configuration.yaml"
if not configuration.exists():
    raise SystemExit(f"no assembled configuration for combination {COMBO!r}: "
                     f"{configuration} is missing. The fork above this node, "
                     f"scripts/prepare_members.py and "
                     f"scripts/assemble_candidate_config.py run first.")

spec = json.loads((NODE / "results" / COMBO / "candidate_spec.json").read_text())
seed = spec["seed_derivation"]
weighting = spec["user_option_values"]["weighting"]
members = ", ".join(m["name"] for m in spec["members"])

run_local_model(
    NODE,
    name="ensemble",
    model_dir=NODE / "scripts" / "ensemble_model",
    n_samples=1000,
    seeded=True,
    seed=seed["seed"],
    configuration=configuration,
    note="every draw in this model's forecast was drawn by one of its members, through "
         "the member's own predict entry point and from the member's own seed. What "
         "this model's seed governs is the pool: how many of the thousand draws each "
         "member contributes is fixed by the weights and the largest-remainder rule, "
         "and which of that member's draws are taken, and in what order they are "
         "written, come from one NumPy generator seeded with the component seed "
         f"{seed['seed']}, derived from project seed {seed['project_seed']} as "
         f"{seed['derivation']}. Under weighting=min_crps the weights themselves are "
         "fitted in train, by a deterministic solve over the members' validation "
         "forecasts, which are in turn drawn from the members' own seeds. Nothing in "
         "the pool is drawn twice from one stream. "
         f"Weighting in this combination: {weighting}; members: {members}. Verified by "
         "running the model twice and diffing.",
)
