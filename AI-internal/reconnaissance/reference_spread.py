#!/usr/bin/env python
"""How much can a comparison against the reference model actually distinguish?

Batch-4 reconnaissance. The plan's §2 asks for the comparison to be reported "with its
per-region and per-split spread and a plain statement of what that spread can
distinguish". Before any candidate of ours exists, the reference alone already answers most
of that question, and answering it now — with no candidate in hand to be flattered or
disadvantaged — is the only time it can be answered disinterestedly.

Three sources of spread are separated:

* **Monte Carlo** — the reference is unseeded (`scripts/predict.R` calls
  `inla.posterior.sample` and `rnbinom` and never `set.seed`), so repeating the identical
  command moves its score. This is a floor on what any difference can mean.
* **Across splits** — eight rolling-origin splits, each a different two-quarter window.
* **Across regions** — sixteen provinces spanning four orders of magnitude in burden.

Writes one JSON. Nothing here is a claim about a model; it is a claim about the measurement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def spread_summary(detailed: pd.DataFrame, repeats: pd.DataFrame) -> dict:
    by_split = detailed.groupby("split_first_period")["metric"].mean()
    by_region = detailed.groupby("location")["metric"].mean()
    mean_crps = float(detailed["metric"].mean())

    mc_sd = float(repeats["crps"].std(ddof=1))
    split_se = float(by_split.std(ddof=1) / len(by_split) ** 0.5)

    return {
        "mean_crps": mean_crps,
        "n_cells": int(detailed.shape[0]),
        "n_regions": int(by_region.shape[0]),
        "n_splits": int(by_split.shape[0]),
        "monte_carlo": {
            "n_runs": int(repeats.shape[0]),
            "sd": mc_sd,
            "min": float(repeats["crps"].min()),
            "max": float(repeats["crps"].max()),
            "sd_pct_of_mean": 100 * mc_sd / mean_crps,
        },
        "across_splits": {
            "sd": float(by_split.std(ddof=1)),
            "min": float(by_split.min()),
            "max": float(by_split.max()),
            "se_of_mean": split_se,
            "se_pct_of_mean": 100 * split_se / mean_crps,
        },
        "across_regions": {
            "sd": float(by_region.std(ddof=1)),
            "min": float(by_region.min()),
            "max": float(by_region.max()),
        },
        # The two spreads that bound a comparison, expressed as the smallest difference in
        # mean CRPS that is not obviously inside the noise. Deliberately crude: a paired
        # comparison on the same cells is tighter than this, and phase C should compute
        # that rather than lean on this figure.
        "smallest_distinguishable_difference": {
            "monte_carlo_2sd": 2 * mc_sd,
            "split_2se": 2 * split_se,
            "binding": "split_2se" if 2 * split_se > 2 * mc_sd else "monte_carlo_2sd",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detailed", type=Path, required=True, help="Per-cell CRPS CSV")
    parser.add_argument("--repeats", type=Path, required=True, help="Per-repeat headline metrics CSV")
    parser.add_argument("--out-file", type=Path, required=True)
    args = parser.parse_args()

    summary = spread_summary(pd.read_csv(args.detailed), pd.read_csv(args.repeats))
    args.out_file.write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
