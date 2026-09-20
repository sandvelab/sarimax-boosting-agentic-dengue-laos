#!/usr/bin/env python3
"""How much does this project's backtest resolve? Stage 1 vs. the two required baselines,
on the identical set of scored cells, each read from its own node's file-grounded result
(no number here is computed except by reading those files -- AGENTS.md §1).

"Resolves" is read as: how much of a naive forecaster's error does stage 1 actually remove.
Reported as stage 1's mean CRPS and each baseline's, plus stage 1's percentage CRPS reduction
relative to each baseline, on the exact matching (province, split, month) cell set -- checked
explicitly, not assumed from equal counts.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
STAGE1 = NODE.parent / "02_stage1"
PERSISTENCE = NODE / "01_persistence"
CLIMATOLOGY = NODE / "02_climatology"
RESULTS = NODE / "results"


def read_cells(node: Path) -> dict[tuple[str, str, str], float]:
    with (node / "results" / "per_cell_scores.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    return {
        (r["province"], r["split"], r["month"]): float(r["crps"])
        for r in rows if r["crps"] not in ("", None)
    }


def main() -> None:
    stage1_cells = read_cells(STAGE1)
    persistence_cells = read_cells(PERSISTENCE)
    climatology_cells = read_cells(CLIMATOLOGY)

    keys = set(stage1_cells) & set(persistence_cells) & set(climatology_cells)
    all_keys = set(stage1_cells) | set(persistence_cells) | set(climatology_cells)
    if keys != all_keys:
        missing = sorted(all_keys - keys)
        raise SystemExit(
            f"cell sets do not match across stage 1 and both baselines "
            f"({len(missing)} mismatched cells, e.g. {missing[:5]}) -- "
            f"comparison would not be apples-to-apples"
        )

    ordered = sorted(keys)
    mean_stage1 = sum(stage1_cells[k] for k in ordered) / len(ordered)
    mean_persistence = sum(persistence_cells[k] for k in ordered) / len(ordered)
    mean_climatology = sum(climatology_cells[k] for k in ordered) / len(ordered)

    summary = {
        "n_cells_compared": len(ordered),
        "mean_crps": {
            "stage1_sarimax": mean_stage1,
            "persistence": mean_persistence,
            "seasonal_climatology": mean_climatology,
        },
        "stage1_pct_reduction_vs_persistence": 100 * (mean_persistence - mean_stage1) / mean_persistence,
        "stage1_pct_reduction_vs_climatology": 100 * (mean_climatology - mean_stage1) / mean_climatology,
        "stage1_beats_persistence": mean_stage1 < mean_persistence,
        "stage1_beats_climatology": mean_stage1 < mean_climatology,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
