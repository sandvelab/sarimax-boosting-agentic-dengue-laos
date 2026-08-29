"""Run the frozen-window seasonal climatology baseline through Chap's evaluation.

The model itself is `scripts/climatology_model/` -- a Chap model contract directory whose
`MLproject` is the sibling construction's but for its name, and whose `uv.lock` resolves to
the same six packages at the same versions, so the two children of this fork reach `chap
eval` by the identical route and the fork moves the estimation window and nothing else.
What the model does, and what freezing the table costs on this dataset, is documented there
and in the node's claim.

**It scores under the name `climatology`**, which is the sibling's name too. That is
deliberate: this is the seasonal climatology baseline, estimated over a different window,
and the leaderboard row it produces is the row `main`'s climatology produces. A second name
would put two climatology baselines on the board where the plan's §4 requires one, and would
make every cross-combination comparison of that row a comparison of two differently-named
things. Which construction produced it is in `models.csv`'s `node` column and in this run's
`model_spec.json`.

This script chooses nothing. The dataset and the backtest scheme come from
`02_setup/results/$COMBO/`; the call to `chap eval` is the one every model of ours goes
through, in `03_models/scripts/lib/chap_eval.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[3] / "scripts" / "lib"))

from chap_eval import run_local_model  # noqa: E402

run_local_model(
    NODE,
    name="climatology",
    model_dir=NODE / "scripts" / "climatology_model",
    n_samples=1000,
    seeded=False,
    note="none. The draws are the empirical quantile function of the frozen table "
         "evaluated at the fixed levels (i + 0.5)/N, not sampled from it, so the model "
         "contains no randomness and Rule 6 is satisfied by there being nothing to seed.",
)
