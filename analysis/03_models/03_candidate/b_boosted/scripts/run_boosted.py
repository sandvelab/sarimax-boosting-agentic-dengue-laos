"""Run the gradient-boosted candidate through Chap's evaluation.

The model itself is `scripts/boosted_model/` -- a Chap model contract directory with its
own `pyproject.toml` and `uv.lock`, so chap-core builds its environment from a lockfile
that travels with the model. What the model does, and why its predictive distribution is
constructed the way it is, is documented there and in this node's claim.

This script chooses nothing. The dataset and the backtest scheme come from
`02_setup/results/$COMBO/`; the configuration comes from the two forks above, assembled by
`assemble_candidate_config.py` into `results/$COMBO/model_configuration.yaml`; and the call
to `chap eval` is the one every model of ours goes through, in
`03_models/scripts/lib/chap_eval.py`. Using the same one is what makes candidate 2's score
comparable with candidate 1's rather than merely similar to it.

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
                     f"{configuration} is missing. The two forks above this node and "
                     f"scripts/assemble_candidate_config.py run first.")

spec = json.loads((NODE / "results" / COMBO / "candidate_spec.json").read_text())
seed = spec["seed_derivation"]
head = spec["user_option_values"]["head"]

run_local_model(
    NODE,
    name="boosted",
    model_dir=NODE / "scripts" / "boosted_model",
    n_samples=1000,
    seeded=True,
    seed=seed["seed"],
    configuration=configuration,
    note="the forecast is a draw, and this family has only one source of it: the "
         "observation model the head puts around what the trees return. A boosted "
         "ensemble has no posterior, so unlike candidate 1 there is no draw over the "
         "fitted parameters -- the spread is the spread of the outcome around a model "
         "taken as known. Under the negative-binomial head the draw is from that "
         "distribution at the fitted dispersion; under the quantile-ensemble head it is "
         "a uniform draw inverted through the fitted ladder. The fit itself draws "
         "nothing: early stopping is disabled and the boosters are refitted at a fixed "
         "round count, so two fits on the same frame are identical. All of it goes "
         f"through one NumPy generator seeded with the component seed {seed['seed']}, "
         f"derived from project seed {seed['project_seed']} as {seed['derivation']}. "
         f"Head in this combination: {head}. Verified by running the model twice and "
         "diffing.",
)
