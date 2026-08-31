"""Gather what each combination concluded into one table, and say what is missing.

The phase-D deliverable is a **distribution of conclusions over reasonable analyses**, not
a headline with a robustness footnote. This is the file that distribution is read from.

It computes almost nothing. Every column is copied out of a combination's own
`analysis/results/<combo>/conclusion.json`, which the root's `conclude.py` wrote from that
combination's stored scores. The exceptions are three subtractions on this table's own
columns, here so that no report has to do them in prose:

* `delta_skill_vs_main` -- how far this analysis's conclusion sits from the reported one;
* `delta_skill_additive` -- for a tier-2 pair, the sum of its two rows' own deltas: what
  the pair would come to if the two forks did not interact;
* `interaction` -- the difference between the two. **This is what tier 2 exists to
  measure.** Batches 9 and 21 each found that one-at-a-time fork effects do not compose,
  which is the argument batch 12 gave for not cutting tier 2 when the budget was drawn; a
  pair whose interaction is small says the one-at-a-time picture can be added up, and one
  whose interaction rivals its main effects says it cannot.

A pair's two rows are recovered from its own `fork` and `child` columns, which the manifest
writes joined by `+`, and matched against the tier-1 row with that fork and that child --
never by splitting the combination's name, which is a label.

**Rows without a conclusion are kept, with the reason.** A stability table that silently
contained only the analyses that happened to have run would be the failure this whole node
exists to prevent, one level up: it would report the distribution over a set nobody chose.
So every row of the manifest appears, and the ones that did not run say whether that is
because the child has no scripts yet, because its batch has not happened, or because it
failed -- read from `run_status.csv` where that file has something to say.

## The holdout half

`--dataset holdout` reads the frozen phase-E manifest and the status file its run wrote,
and produces the same table for the held-out year. It is the same code because it is the
same question asked of the other dataset; what it must not do is put the two in one table,
because a row of each would then be summarised together and the whole point of phase E is
that the two spreads are read side by side rather than pooled. `report_holdout.py` is where
they are joined, row by row, on the pairing batch 15 froze.

Writes, at this node:
  results/conclusions.csv               one row per manifest combination
  results/conclusions_notes.json        how much of the manifest is answered, and by what
  results/holdout_conclusions.csv       the same, for the phase-E set
  results/holdout_conclusions_notes.json
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
RESULTS = ROOT / "analysis/results"

# Copied straight across from conclusion.json. Named here so that a key the root stops
# writing is a visible blank rather than a silently absent column.
CARRIED = ["our_model", "skill_score", "crps_ours", "crps_reference", "mae_ours",
           "coverage_10_90_ours", "coverage_25_75_ours", "n_cells", "n_locations",
           "n_splits", "paired_mean_diff_vs_reference", "paired_se_cluster_split",
           "resolvable_difference_floor", "beats_reference", "beats_all_baselines",
           "candidate_exists"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dataset", choices=("development", "holdout"),
                        default="development",
                        help="which manifest to collect: the development set, or the "
                             "phase-E set frozen in batch 15")
    args = parser.parse_args()
    holdout = args.dataset == "holdout"
    prefix = "holdout_" if holdout else ""

    out = NODE / "results"
    manifest = out / ("manifest_holdout.csv" if holdout else "manifest.csv")
    if not manifest.exists():
        raise SystemExit(f"no {manifest.name}: run "
                         f"{'freeze_holdout_manifest.py' if holdout else 'plan_manifest.py'}"
                         f" first")
    rows = list(csv.DictReader(manifest.open()))

    status_path = out / ("run_status_holdout.csv" if holdout else "run_status.csv")
    status = {}
    if status_path.exists():
        status = {r["combination"]: r for r in csv.DictReader(status_path.open())}

    table, answered = [], 0
    for row in rows:
        combo = row["combination"]
        entry = {"rank": row["rank"], "tier": row["tier"], "combination": combo,
                 "kind": row["kind"], "fork": row["fork"], "child": row["child"],
                 **{key: "" for key in CARRIED},
                 "delta_skill_vs_main": "", "delta_skill_additive": "",
                 "interaction": "", "conclusion_file": "", "why_not": ""}
        conclusion = RESULTS / combo / "conclusion.json" if combo else None
        if conclusion and conclusion.exists():
            data = json.loads(conclusion.read_text())
            entry.update({key: data.get(key, "") for key in CARRIED})
            entry["conclusion_file"] = str(conclusion.relative_to(ROOT))
            answered += 1
        elif not combo:
            entry["why_not"] = "tier-2 slot, unresolved until tier 1 has conclusions"
        elif row["built"] != "True":
            entry["why_not"] = (f"the child has no scripts yet; batch "
                                f"{row.get('assigned_batch', '?')} writes them")
        elif combo in status and status[combo]["status"].startswith("failed"):
            entry["why_not"] = f"{status[combo]['status']}; see {status[combo]['log']}"
        elif combo in status and status[combo]["status"].startswith("not run"):
            # The holdout's unpaired row. Development did not run its twin either, so
            # there is nothing for it to be reported beside; the driver said so and this
            # carries the reason rather than restating it.
            entry["why_not"] = status[combo]["status"]
        elif row.get("assigned_batch", "-").strip() == "-":
            # The held row: a combination that exists and perturbs nothing, which no
            # batch runs and which `conclude.py` was deliberately never pointed at. It is
            # not a row waiting for a batch, and saying so would put a phantom absence
            # into the count this table exists to keep honest.
            entry["why_not"] = row["status"]
        else:
            entry["why_not"] = f"not run yet; assigned to batch {row['assigned_batch']}"
        table.append(entry)

    # The row every delta is measured from: this manifest's own main path, found by
    # its kind. Naming the combination would work on development and silently find
    # nothing on the holdout, where it is called `main__holdout`.
    main_row = next((r for r in table if r["kind"] == "main"), None)
    if main_row and main_row["skill_score"] != "":
        for entry in table:
            if entry["skill_score"] != "":
                entry["delta_skill_vs_main"] = round(
                    float(entry["skill_score"]) - float(main_row["skill_score"]), 6)

    # Whether a pair is the sum of its parts. A tier-1 row is found by the fork it moved
    # and the child it took -- the pair's own `fork` and `child` columns, split on the
    # `+` the manifest joins them with. Matching on those rather than on the combination
    # name means a renamed combination cannot silently break the arithmetic.
    by_move = {(e["fork"], e["child"]): e for e in table
               if e["tier"] == "1" and e["skill_score"] != ""}
    for entry in table:
        if entry["tier"] != "2" or entry["delta_skill_vs_main"] == "":
            continue
        parts = [by_move.get(move) for move in
                 zip(entry["fork"].split("+"), entry["child"].split("+"))]
        if len(parts) != 2 or not all(parts):
            entry["delta_skill_additive"] = ""
            continue
        additive = sum(float(p["delta_skill_vs_main"]) for p in parts)
        entry["delta_skill_additive"] = round(additive, 6)
        entry["interaction"] = round(
            float(entry["delta_skill_vs_main"]) - additive, 6)

    with (out / f"{prefix}conclusions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    scored = [e for e in table if e["skill_score"] != ""]
    paired = [e for e in table if e["interaction"] != ""]
    (out / f"{prefix}conclusions_notes.json").write_text(json.dumps({
        "manifest_rows": len(table),
        "rows_with_a_conclusion": answered,
        "rows_without": len(table) - answered,
        "why_not_counts": {reason: sum(1 for e in table if e["why_not"] == reason)
                           for reason in sorted({e["why_not"] for e in table if e["why_not"]})},
        "skill_score_range": ([min(float(e["skill_score"]) for e in scored),
                               max(float(e["skill_score"]) for e in scored)]
                              if scored else None),
        "source": "analysis/results/<combination>/conclusion.json, one per combination",
        "computed_here": ("delta_skill_vs_main, delta_skill_additive and interaction, "
                          "each a subtraction on this table's own columns"),
        "interaction": ({
            "pairs_measured": len(paired),
            "largest_absolute": max(abs(float(e["interaction"])) for e in paired),
            "range": [min(float(e["interaction"]) for e in paired),
                      max(float(e["interaction"]) for e in paired)],
            "largest_tier1_main_effect_among_the_forks_paired": max(
                abs(float(by_move[move]["delta_skill_vs_main"]))
                for e in paired
                for move in zip(e["fork"].split("+"), e["child"].split("+"))),
            "note": ("interaction = the pair's own delta minus the sum of its two rows' "
                     "deltas. Zero would mean the two forks compose; tier 2 exists "
                     "because batches 9 and 21 each found that they do not."),
        } if paired else None),
        "dataset": args.dataset,
        "manifest": str(manifest.relative_to(ROOT)),
        "note": ("This is not yet the phase-D result. It becomes one when every row it "
                 "names has run; until then it is the record of how much of the frozen "
                 "manifest has been answered."),
    }, indent=1, sort_keys=True) + "\n")

    print(f"{answered} of {len(table)} {args.dataset} manifest rows have a conclusion "
          f"-> {(out / f'{prefix}conclusions.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
