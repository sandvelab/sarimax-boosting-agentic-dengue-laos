#!/usr/bin/env python3
"""Run the external check's rows, through the same driver the perturbation set runs through.

Every command issued here is a `run.sh` or a node script that the main path also runs, with
`COMBO` set to one of the four external names. The step lists are built by
`05_stability/scripts/lib/driver.py`, which is where they were built for the thirty-two
perturbation rows and the held-out year before this batch existed. There is no second
implementation of the pipeline and there must never be one: a check that ran different code
would measure the code and not the model.

**Every row runs the whole pipeline.** On development the `main` row runs `conclude.py`
alone, because the main path is the analysis that already ran. Here nothing has run: each
row faces a file no model in this project has seen, so each takes every setup fork at its
main child, the assembler, both required baselines, the reference model's four unseeded
repeats, the reported pool and the scoring chain. That is `driver.steps_for`'s `full_main`,
the same argument the holdout's `main` row takes, and it is expressed by moving nothing
rather than by a second list of the pipeline kept here.

**Nothing is sealed and nothing is skipped.** Plan §3's seal protects the Lao 2010, because
the model was developed against Lao 1998–2009. No model is developed on these files, so a
row that has already run is run again on the next invocation, which is what keeps
`analysis/run.sh` a reproduction of the external check rather than a description of it —
the failure batch 18's clean-room check found in the phase-E half. The cost of that is
that the reference model is unseeded, so a re-run redraws the denominator; the run status
records the draw's date and `report_external.py` reports the reference's own spread beside
every figure that divides by it.

Writes:
  results/run_status_external.csv         what each row did, how long, and where its log is
  results/external_cost_planned_vs_actual.json   the estimate against the clock
  results/logs/<combination>.log          the full output of every step of every row

Seeds: the project seed reaches the models through their own component seeds, unchanged;
nothing about the derivation is the dataset. The reference is unseeded and is run four
times, as it is on both Lao arrangements.

Usage, from the repository root:
  environment/chapenv/bin/python analysis/06_external/scripts/run_external.py --dry-run
  ... --only main__vnm
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
RESULTS = NODE / "results"
LOGS = RESULTS / "logs"
MANIFEST = RESULTS / "manifest_external.csv"
STATUS = RESULTS / "run_status_external.csv"

sys.path.insert(0, str(ROOT / "analysis/05_stability/scripts/lib"))
import inventory as inv  # noqa: E402
from driver import run_row  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="print each row's step list and run nothing")
    parser.add_argument("--only", help="one combination name")
    args = parser.parse_args()

    if not MANIFEST.exists():
        raise SystemExit(f"no {MANIFEST.name}: run plan_external.py first")
    rows = list(csv.DictReader(MANIFEST.open()))
    forks = inv.forks()

    outcomes = []
    for row in rows:
        if args.only and row["combination"] != args.only:
            continue
        if row["status"] != "planned":
            outcomes.append({"combination": row["combination"],
                             "status": f"not run: {row['status']}",
                             "seconds": "", "steps": "", "log": "", "at": ""})
            continue
        outcomes.append(run_row(row, forks, args.dry_run, logs=LOGS, full_main=True))

    if args.dry_run:
        return 0

    fields = ["combination", "status", "seconds", "steps", "log", "at"]
    known = {r["combination"]: r for r in csv.DictReader(STATUS.open())} \
        if STATUS.exists() else {}
    known.update({o["combination"]: o for o in outcomes})
    order = {r["combination"]: int(r["rank"]) for r in rows}
    with STATUS.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for name in sorted(known, key=lambda n: order.get(n, 999)):
            writer.writerow(known[name])

    # The estimate against the clock, in the terms batches 13 and 15 compared them: the
    # total and the per-row ratios, because those two have disagreed every time.
    planned = {r["combination"]: float(r["planned_seconds"]) for r in rows}
    actual = {name: float(r["seconds"]) for name, r in known.items() if r["seconds"]}
    paired = {name: {"planned_seconds": planned[name], "actual_seconds": actual[name],
                     "ratio": round(actual[name] / planned[name], 3)}
              for name in sorted(actual) if name in planned}
    totals = (sum(v["planned_seconds"] for v in paired.values()),
              sum(v["actual_seconds"] for v in paired.values()))
    (RESULTS / "external_cost_planned_vs_actual.json").write_text(json.dumps({
        "what_this_is": (
            "what plan_external.py estimated each row would take, against what it took. "
            "The estimate was committed before any of these rows ran"),
        "rows": paired,
        "planned_seconds_total": round(totals[0], 1),
        "actual_seconds_total": round(totals[1], 1),
        "total_ratio": round(totals[1] / totals[0], 3) if totals[0] else None,
        "worst_row": max(paired, key=lambda n: paired[n]["ratio"]) if paired else None,
        "best_row": min(paired, key=lambda n: paired[n]["ratio"]) if paired else None,
    }, indent=2) + "\n")

    ran = sum(1 for o in outcomes if o["status"] == "ran")
    print(f"\n{ran} of {len(outcomes)} row(s) ran -> {STATUS.relative_to(ROOT)}")
    if paired:
        print(f"planned {totals[0] / 3600:.2f} h, actual {totals[1] / 3600:.2f} h, "
              f"ratio {totals[1] / totals[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
