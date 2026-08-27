"""Run the hierarchical negative-binomial candidate through Chap's evaluation.

The model itself is `scripts/hier_nb_model/` -- a Chap model contract directory with its
own `pyproject.toml` and `uv.lock`, so chap-core builds its environment from a lockfile
that travels with the model. What the model does, and why its predictive distribution is
constructed the way it is, is documented there and in this node's claim.

This script chooses nothing. The dataset and the backtest scheme come from
`02_setup/results/$COMBO/`; the configuration comes from the four forks above, assembled
by `assemble_candidate_config.py` into `results/$COMBO/model_configuration.yaml`; and the
call to `chap eval` is the one every model of ours goes through, in
`03_models/scripts/lib/chap_eval.py`.

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
                     f"{configuration} is missing. The four forks above this node and "
                     f"scripts/assemble_candidate_config.py run first.")

seed = json.loads((NODE / "results" / COMBO / "candidate_spec.json").read_text())
seed = seed["seed_derivation"]

run_local_model(
    NODE,
    name="hier_nb",
    model_dir=NODE / "scripts" / "hier_nb_model",
    n_samples=1000,
    seeded=True,
    seed=seed["seed"],
    configuration=configuration,
    note="the forecast is a draw. Two sources: the Laplace posterior of the fitted "
         "coefficients, and the negative-binomial observation model on top of it, plus a "
         "province-year effect drawn from its estimated prior for years the fit never "
         "saw. All three go through one NumPy generator seeded with the component seed "
         f"{seed['seed']}, derived from project seed {seed['project_seed']} as "
         f"{seed['derivation']}. Verified by running the model twice and diffing.",
)
