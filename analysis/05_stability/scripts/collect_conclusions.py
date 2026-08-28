"""Gather what each combination concluded into one table, and say what is missing.

The phase-D deliverable is a **distribution of conclusions over reasonable analyses**, not
a headline with a robustness footnote. This is the file that distribution is read from.

It computes nothing. Every column is copied out of a combination's own
`analysis/results/<combo>/conclusion.json`, which the root's `conclude.py` wrote from that
combination's stored scores -- the one exception being `delta_skill_vs_main`, which is a
subtraction of two columns on the table and is here so that no report has to do it in
prose.

**Rows without a conclusion are kept, with the reason.** A stability table that silently
contained only the analyses that happened to have run would be the failure this whole node
exists to prevent, one level up: it would report the distribution over a set nobody chose.
So every row of the manifest appears, and the ones that did not run say whether that is
because the child has no scripts yet, because its batch has not happened, or because it
failed -- read from `run_status.csv` where that file has something to say.

Writes, at this node:
  results/conclusions.csv       one row per manifest combination
  results/conclusions_notes.json  how much of the manifest is answered, and by what
"""

from __future__ import annotations

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
    out = NODE / "results"
    manifest = out / "manifest.csv"
    if not manifest.exists():
        raise SystemExit("no manifest: run plan_manifest.py first")
    rows = list(csv.DictReader(manifest.open()))

    status_path = out / "run_status.csv"
    status = {}
    if status_path.exists():
        status = {r["combination"]: r for r in csv.DictReader(status_path.open())}

    table, answered = [], 0
    for row in rows:
        combo = row["combination"]
        entry = {"rank": row["rank"], "tier": row["tier"], "combination": combo,
                 "kind": row["kind"], "fork": row["fork"], "child": row["child"],
                 **{key: "" for key in CARRIED},
                 "delta_skill_vs_main": "", "conclusion_file": "", "why_not": ""}
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
                                f"{row['assigned_batch']} writes them")
        elif combo in status and status[combo]["status"].startswith("failed"):
            entry["why_not"] = f"{status[combo]['status']}; see {status[combo]['log']}"
        else:
            entry["why_not"] = f"not run yet; assigned to batch {row['assigned_batch']}"
        table.append(entry)

    main_row = next((r for r in table if r["combination"] == "main"), None)
    if main_row and main_row["skill_score"] != "":
        for entry in table:
            if entry["skill_score"] != "":
                entry["delta_skill_vs_main"] = round(
                    float(entry["skill_score"]) - float(main_row["skill_score"]), 6)

    with (out / "conclusions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    scored = [e for e in table if e["skill_score"] != ""]
    (out / "conclusions_notes.json").write_text(json.dumps({
        "manifest_rows": len(table),
        "rows_with_a_conclusion": answered,
        "rows_without": len(table) - answered,
        "why_not_counts": {reason: sum(1 for e in table if e["why_not"] == reason)
                           for reason in sorted({e["why_not"] for e in table if e["why_not"]})},
        "skill_score_range": ([min(float(e["skill_score"]) for e in scored),
                               max(float(e["skill_score"]) for e in scored)]
                              if scored else None),
        "source": "analysis/results/<combination>/conclusion.json, one per combination",
        "computed_here": ("delta_skill_vs_main only, which is a subtraction of two "
                          "columns on this table"),
        "note": ("This is not yet the phase-D result. It becomes one when every row it "
                 "names has run; until then it is the record of how much of the frozen "
                 "manifest has been answered."),
    }, indent=1, sort_keys=True) + "\n")

    print(f"{answered} of {len(table)} manifest rows have a conclusion "
          f"-> {(out / 'conclusions.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
