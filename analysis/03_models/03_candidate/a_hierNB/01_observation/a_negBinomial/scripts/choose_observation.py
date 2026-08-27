"""Stage 1 of the candidate's configuration: the observation model for the counts.

One negative-binomial distribution per cell, with a single dispersion parameter shared
across provinces. The counts are heavily over-dispersed and a large share of them are
zero, and this child's position is that both features are absorbed by the same variance
function: the negative binomial's variance grows as mu + mu^2/phi, which at small mu puts
most of its mass on zero without a separate process being posited to generate it.

The siblings this node exists to hold -- a zero-inflated mixture and a hurdle model --
take the opposite position, that the zeros come from a reporting process distinct from
the transmission process. Nothing in the data settles which is right: a zero month in a
province reporting four cases in twelve years and a zero month in the capital are the
same value with different meanings, and no column distinguishes them. That is what makes
this a fork rather than a detail.

This script decides nothing beyond its own choice. It writes the option values the
candidate's assembler merges, and the **premise check** the choice rests on: whether the
counts really are over-dispersed relative to a Poisson, computed here rather than
asserted, on the dataset this combination assembled.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import resolve  # noqa: E402


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    dataset, dataset_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})
    counts = frame["disease_cases"].dropna()

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": dataset_combo,
        "stage": "observation",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_negBinomial",
        "description": "one negative binomial per cell, dispersion shared across provinces",
        "user_option_values": {"observation": "negative_binomial"},
        "additional_continuous_covariates": [],
        "premise": {
            "observed_cells": int(len(counts)),
            "zero_share": float((counts == 0).mean()),
            "mean": float(counts.mean()),
            "variance": float(counts.var(ddof=1)),
            # Under a Poisson this ratio is 1. It is reported rather than tested: the
            # counts are not identically distributed across provinces, so a dispersion
            # test on the pooled column would answer a question nobody asked.
            "variance_to_mean_ratio_pooled": float(counts.var(ddof=1) / counts.mean()),
        },
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"observation/a_negBinomial[{COMBO}]: negative_binomial; "
          f"pooled variance/mean {spec['premise']['variance_to_mean_ratio_pooled']:.1f}, "
          f"zeros {spec['premise']['zero_share']:.2f} -> {out}")


if __name__ == "__main__":
    main()
