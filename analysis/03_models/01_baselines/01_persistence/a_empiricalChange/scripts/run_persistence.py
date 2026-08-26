"""Run the persistence baseline through Chap's evaluation.

The model itself is `scripts/persistence_model/` -- a Chap model contract directory with
its own `pyproject.toml` and `uv.lock`, so chap-core builds its environment from a
lockfile that travels with the model. What the model does, and why its predictive
distribution is constructed the way it is, is documented there and in the node's claim.

This script chooses nothing. The dataset and the backtest scheme come from
`02_setup/results/$COMBO/`; the call to `chap eval` is the one every model of ours goes
through, in `03_models/scripts/lib/chap_eval.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[2] / "scripts" / "lib"))

from chap_eval import run_local_model  # noqa: E402

run_local_model(
    NODE,
    name="persistence",
    model_dir=NODE / "scripts" / "persistence_model",
    n_samples=1000,
    seeded=False,
    note="none. The draws are the empirical quantile function evaluated at the fixed "
         "levels (i + 0.5)/N, not sampled from it, so the model contains no randomness "
         "and Rule 6 is satisfied by there being nothing to seed.",
)
