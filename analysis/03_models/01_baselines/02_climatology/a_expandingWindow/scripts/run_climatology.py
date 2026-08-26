"""Run the seasonal climatology baseline through Chap's evaluation.

The model itself is `scripts/climatology_model/` -- a Chap model contract directory with
its own `pyproject.toml` and `uv.lock`, the same shape as the persistence baseline's, so
that the two required baselines reach the evaluation by the identical route.

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
    name="climatology",
    model_dir=NODE / "scripts" / "climatology_model",
    n_samples=1000,
    seeded=False,
    note="none. The draws are the empirical quantile function evaluated at the fixed "
         "levels (i + 0.5)/N, not sampled from it, so the model contains no randomness "
         "and Rule 6 is satisfied by there being nothing to seed.",
)
