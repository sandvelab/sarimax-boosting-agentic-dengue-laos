"""State the project's conclusion for this combination, as a computed file.

The root of the tree asks whether a model of ours forecasts Lao dengue well enough to beat
the field's own model and the two required baselines. That question has a numeric answer
per analysis, and this script is where it is computed -- once, from the stored scores, so
that nothing anywhere else in the repository states a conclusion that could drift from the
files behind it.

The answer is a **skill score**, `1 − CRPS_ours / CRPS_reference`, with raw CRPS and both
coverage figures beside it. Relative rather than absolute, because the development period
and the held-out year are different years of a real epidemic and their raw CRPS is not
comparable: a raw development-to-holdout gap would confound a model that flattered itself
on development with 2010 simply being harder. A ratio to a reference that faced the same
year controls for that and puts both spreads on one axis.

**Which model is "ours" is resolved from the tree, not chosen here.** Our reported model is
the main path through `03_models/03_candidate` -- the alternatives node whose children are
the model families. Until that node exists, the project has baselines and no candidate, and
this script says so in the file rather than promoting a baseline to a candidate quietly:
`candidate_exists` is false, the headline model is the best-scoring model of ours, and its
role is recorded as a placeholder. Every model's skill score is written out beside the
headline in either case, so the file never depends on that selection to be readable.

Invoked once per combination -- by `analysis/run.sh` for the main path, and by the
stability driver for every other, with COMBO set.

Writes, under results/$COMBO/:
  conclusion.json   the conclusion for this combination
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
COMBO = os.environ.get("COMBO", "main")
REFERENCE = "reference"
CANDIDATE_NODE = NODE / "03_models" / "03_candidate"


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    v = m.group(1).strip() if m else ""
    return v or None if v not in ("", "-", "none", "n/a") else None


def our_reported_model(board: pd.DataFrame) -> tuple[str, str, bool]:
    """The model the project reports, and how it was arrived at."""
    ours = board[board.origin == "ours"]
    if ours.empty:
        raise SystemExit("no model of ours has been scored for this combination")

    if (CANDIDATE_NODE / "claim.md").exists():
        main = field((CANDIDATE_NODE / "claim.md").read_text(), "main-path")
        spec = sorted((CANDIDATE_NODE / main).glob(f"**/results/{COMBO}/model_spec.json"))
        if main and spec:
            name = json.loads(spec[0].read_text())["model"]
            return name, f"the main path through 03_models/03_candidate ({main})", True

    best = ours.sort_values("mean_crps").iloc[0]
    return (best.model,
            "no candidate node exists yet; the best-scoring model of ours stands in",
            False)


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)
    compare = NODE / "04_score" / "03_compare" / "results" / COMBO
    board = pd.read_csv(compare / "leaderboard.csv")
    paired = pd.read_csv(compare / "paired_summary.csv")
    notes = json.loads((compare / "comparison_notes.json").read_text())

    reference = board[board.model == REFERENCE].iloc[0]
    name, basis, candidate_exists = our_reported_model(board)
    ours = board[board.model == name].iloc[0]
    pair = paired[(paired.model == name) & (paired.against == REFERENCE)].iloc[0]

    baselines = sorted(board.loc[board.node.astype(str).str.contains("01_baselines"), "model"])

    conclusion = {
        "combo": COMBO,
        "dataset": "development",
        "our_model": name,
        "our_model_basis": basis,
        "candidate_exists": bool(candidate_exists),
        "skill_score": float(1 - ours.mean_crps / reference.mean_crps),
        "crps_ours": float(ours.mean_crps),
        "crps_reference": float(reference.mean_crps),
        "mae_ours": float(ours.mae),
        "coverage_10_90_ours": float(ours.coverage_10_90),
        "coverage_25_75_ours": float(ours.coverage_25_75),
        "coverage_10_90_reference": float(reference.coverage_10_90),
        "coverage_25_75_reference": float(reference.coverage_25_75),
        "n_cells": int(ours.n_cells),
        "n_locations": int(ours.n_locations),
        "n_splits": int(ours.n_splits),
        "paired_mean_diff_vs_reference": float(pair.mean_diff),
        "paired_se_cluster_split": float(pair.se_cluster_split),
        "paired_win_rate_cells": float(pair.win_rate_cells),
        "resolvable_difference_floor": notes["noise_floor_largest_repeat_pair_mean_diff"],
        "beats_reference": bool(ours.mean_crps < reference.mean_crps),
        "beats_all_baselines": bool(all(
            ours.mean_crps <= float(board.loc[board.model == b, "mean_crps"].iloc[0])
            for b in baselines)),
        "baselines": baselines,
        "skill_by_model": {
            row.model: float(1 - row.mean_crps / reference.mean_crps)
            for row in board.itertuples() if row.origin == "ours"
        },
        "crps_by_model": {row.model: float(row.mean_crps) for row in board.itertuples()},
    }
    (out / "conclusion.json").write_text(json.dumps(conclusion, indent=1, sort_keys=True) + "\n")

    print(f"conclusion[{COMBO}]: {name} CRPS {conclusion['crps_ours']:.3f} vs reference "
          f"{conclusion['crps_reference']:.3f} -> skill {conclusion['skill_score']:+.4f}"
          f"{'' if candidate_exists else '  (placeholder: no candidate node yet)'}")


if __name__ == "__main__":
    main()
