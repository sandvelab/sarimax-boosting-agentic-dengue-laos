"""Run the parametric persistence baseline through Chap's evaluation.

The model itself is `scripts/persistence_model/` -- a Chap model contract directory with
its own `pyproject.toml` and `uv.lock`, resolving to the same six packages at the same
versions as the sibling construction's, so chap-core builds both from lockfiles that
travel with the models and the fork moves the construction and nothing else. What the
model does, and whose published construction it is, is documented there and in the node's
claim.

**It scores under the name `persistence`**, which is the sibling's name too. That is
deliberate: this is the persistence baseline, wrapped a second way, and the leaderboard row
it produces is the row `main`'s persistence produces. A second name would put two baselines
on the board where the plan's §4 requires one, and would make every cross-combination
comparison of that row a comparison of two differently-named things. Which construction
produced it is in `models.csv`'s `node` column and in this run's `model_spec.json`.

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
    note="none. The dispersion is fitted by a deterministic search on a fixed grid and "
         "the draws are the fitted negative binomial's quantile function evaluated at "
         "the fixed levels (i + 0.5)/N, not sampled from it, so the model contains no "
         "randomness and Rule 6 is satisfied by there being nothing to seed -- the same "
         "property the sibling construction has.",
)
