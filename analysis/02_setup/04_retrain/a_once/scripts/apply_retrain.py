"""Stage 4 of the common setup: how often a model is refitted across the backtest.

chap-core's `n-retrain` decides whether one fit serves the whole backtest or each split
gets its own. Batch 3 fixed `n_periods`, `n_splits` and `stride` and said they do not
move again; `n_retrain` was never part of that triple and was left at the platform's
default as an acknowledged fork.

This child takes the default: **one fit**, on the training period, with the expanding
historic window chap-core hands to `predict` at every split. It is what the platform does
unless told otherwise, and it is the cheaper side of the fork -- refitting at every split
multiplies the cost of every model in the comparison by the number of splits.

It is worth being clear about what `n_retrain 1` does and does not guarantee. It governs
how often chap-core calls `train`; a model that does its fitting inside `predict` refits
at every split regardless, which is what the reference model does. So this stage fixes
the platform's behaviour, not the models', and the difference between the two is a
candidate-internal fork rather than this one.

This stage changes no data. What it contributes is the evaluation flag every model node
reads, so that the flag reaches `chap eval` from a file rather than from each model
script's own constant.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves the setup chain
  setup_spec.json        the chosen retrain policy, as an eval flag
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
SETUP = NODE.parents[1]

N_RETRAIN = 1


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")


def upstream(fork: str, combo: str) -> Path:
    found = sorted((SETUP / fork).glob(f"*/results/{combo}/analysis_dataset.csv"))
    if len(found) != 1:
        raise SystemExit(
            f"{fork}: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(SETUP)) for p in found]}")
    return found[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    source = upstream("03_provinces", COMBO)
    frame = pd.read_csv(source, dtype={"time_period": str})
    frame.to_csv(out / "analysis_dataset.csv", index=False)

    spec = {
        "combo": COMBO,
        "stage": "retrain",
        "order": 4,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_once",
        "description": "chap-core's default: one fit on the training period, expanding "
                       "historic window at predict",
        "dataset_transform": "identity",
        "input": str(source.relative_to(ROOT)),
        "input_sha256": sha256(source),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": int(len(frame)),
        "rows_out": int(len(frame)),
        "eval_flags": {"n_retrain": N_RETRAIN},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"retrain/a_once: n_retrain={N_RETRAIN}, {len(frame)} rows pass through")


if __name__ == "__main__":
    main()
