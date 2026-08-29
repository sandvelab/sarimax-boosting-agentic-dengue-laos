"""What the manifest predicted a row would cost, against what it cost.

`plan_manifest.py` re-reads every model's `run_cost.json` each time it runs, so once a row
has actually run the manifest's estimate for it becomes a measurement of that run. The
prediction is therefore only visible in the manifest **as it stood before the rows ran** --
and that version is in git, which is what makes this checkable at all rather than a story
about how good the estimate was.

This script reads the manifest at the commit that froze it, joins it to
`results/run_status.csv`, and writes the comparison. It answers one question the phase-D
budget rests on: is the cost model good enough that the cut order it implies means anything.

Writes, under results/:
  cost_planned_vs_actual.csv   one row per combination that has run
  cost_planned_vs_actual.json  the totals and what they say
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]

# The commit that wrote the manifest, before any tier-1 row had run. Batch 12's own
# commit of the frozen manifest; `git log -- results/manifest.csv` is where it comes from.
FROZEN_AT = "2e186f6"
MANIFEST = "analysis/05_stability/results/manifest.csv"


def manifest_at(commit: str) -> dict[str, dict]:
    text = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{MANIFEST}"],
                          capture_output=True, text=True, check=True).stdout
    return {r["combination"]: r for r in csv.DictReader(io.StringIO(text))
            if r["combination"]}


def main() -> None:
    out = NODE / "results"
    planned = manifest_at(FROZEN_AT)
    status = {r["combination"]: r
              for r in csv.DictReader((out / "run_status.csv").open())}

    rows = []
    for name, run in status.items():
        if run["status"] != "ran" or name not in planned:
            continue
        estimate = planned[name]["est_seconds_dev"]
        if not estimate:
            continue
        estimate, actual = float(estimate), float(run["seconds"])
        rows.append({
            "combination": name,
            "kind": planned[name]["kind"],
            "planned_seconds": estimate,
            "actual_seconds": actual,
            "ratio_actual_over_planned": round(actual / estimate, 3) if estimate else None,
            "error_seconds": round(actual - estimate, 1),
        })
    rows.sort(key=lambda r: -r["actual_seconds"])
    with (out / "cost_planned_vs_actual.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    # The main path is excluded from the totals: its development row is `conclude.py`
    # alone, costed at 0.3 s because the analysis had already run, so including it would
    # flatter the ratio with a row that predicted nothing.
    body = [r for r in rows if r["combination"] != "main"]
    planned_total = sum(r["planned_seconds"] for r in body)
    actual_total = sum(r["actual_seconds"] for r in body)
    worst = max(body, key=lambda r: abs(r["ratio_actual_over_planned"] - 1))
    notes = {
        "manifest_frozen_at_commit": FROZEN_AT,
        "rows_compared": len(body),
        "planned_seconds_total": round(planned_total, 1),
        "actual_seconds_total": round(actual_total, 1),
        "ratio_total": round(actual_total / planned_total, 3),
        "worst_row": worst["combination"],
        "worst_row_ratio": worst["ratio_actual_over_planned"],
        "spread_of_actual_seconds": [min(r["actual_seconds"] for r in body),
                                     max(r["actual_seconds"] for r in body)],
        "distinct_planned_values": sorted({r["planned_seconds"] for r in body}),
        "what_this_says":
            "The total is close and the individual rows are not. The frozen manifest gave "
            "every `setup` row the same figure, because it costed a row as the sum of its "
            "parts measured under `main`, and nothing in that model knew that a row can "
            "change how much work a part does. `retrain_everySplit` sets n_retrain to the "
            "split count, so the reference model runs sixteen jobs per repeat instead of "
            "two; it was the most expensive row in tier 1 and the cost model could not see "
            "why. A cut order ranked on these estimates would have been ranked on a "
            "constant.",
    }
    (out / "cost_planned_vs_actual.json").write_text(
        json.dumps(notes, indent=1, sort_keys=True) + "\n")

    print(f"planned {planned_total:.0f} s vs actual {actual_total:.0f} s over "
          f"{len(body)} rows (ratio {notes['ratio_total']}); worst row "
          f"{worst['combination']} at {worst['ratio_actual_over_planned']}x")


if __name__ == "__main__":
    main()
