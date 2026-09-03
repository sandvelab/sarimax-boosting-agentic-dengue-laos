"""Put the two datasets on one axis: what the frozen set concluded on 2010, beside 2009.

This is what phase E exists to produce. The development half is a distribution over 32
analyses that all looked reasonable; the holdout half is the same 32 analyses, fixed before
the year was opened, run against a year none of them had seen. The question is not which
number is bigger. It is **how far the development picture transfers** -- the reported
conclusion, the spread around it, the ranking of the analyses within that spread, and which
judgment calls matter.

The plan says it plainly: if the holdout numbers are much worse than the development
numbers, that gap is the most interesting result the project has, because it is the direct
measurement of how much a system optimising freely against a development set inflated its
own performance. It is reported here and not explained away.

## The pairing is read, not made

`manifest_holdout.csv` carries each row's development conclusion beside it, frozen in batch
15 before the year was opened. This script joins on that column rather than on the names,
and the frozen figure is the one it compares against -- never a figure recomputed today.

It still checks the frozen figures against what `conclusions.csv` says, and what it does
with a difference follows what the difference means:

  a frozen row whose development twin    **fatal**. The pairing itself is gone: the frozen
  the tree no longer concludes           row is paired with an analysis this repository can
                                         no longer produce a development figure for, so
                                         there is nothing to compare against.

  a frozen row whose development         reported, not fatal. The development skill score
  *figure* has drifted                   divides by the reference model, which is unseeded,
                                         so any re-run of the development half re-draws it.
                                         The frozen figure is a record of what was paired
                                         and it stands; the drift is measured against the
                                         band that dataset's own repeats of the reference
                                         define, and written into the output.

The distinction is the whole of it. A number that moved by the width of the reference's own
noise is the reference being unseeded; a pairing that moved is the comparison being about
something else than it says. Only the second can make the reported answer wrong, and a
check a correct clean-room run cannot pass is a check that gets weakened the first time it
fires. `holdout_freeze_check.json`, written by `freeze_holdout_manifest.py` earlier in the
same run, reports the same drift on the same rows under `drift_under_an_unchanged_set` and
reaches the same verdict.

## What is comparable across the two, and what is not

The skill score is a ratio to a reference that faced the same year, so it is comparable --
that is why the project reports one (`readme-at-start.md`). Raw CRPS is not: 2010 is a
different year of a real epidemic, evaluated over four splits rather than eight and 192
cells rather than 371. The reference's own CRPS on each dataset is reported here for
exactly that reason: it is the measure of how hard the year was, computed by a model nobody
here tuned.

Writes, at this node:
  results/holdout_vs_development.csv    one row per paired analysis
  results/holdout_vs_development.json   the phase-E answer, and the counts behind it
  results/fork_sensitivity_both.csv     one row per fork, on both datasets

Seeds: none. Every number is an arithmetic summary of stored scores.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import median

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
RESULTS = NODE / "results"

# Below this, a frozen development figure and today's are the same number: it is float
# formatting through a CSV. Above it, the figure has drifted, which is reported and is not
# an error -- the score divides by the unseeded reference. What is fatal is a frozen row
# the development table no longer concludes at all, which is a moved pairing rather than a
# moved number.
FROZEN_TOLERANCE = 1e-9


def rows_of(path: Path) -> list[dict]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def number(value) -> float | None:
    return float(value) if value not in ("", None) else None


def spread(values: list[float]) -> dict:
    values = sorted(values)
    return {"n": len(values), "min": round(values[0], 6),
            "median": round(median(values), 6), "max": round(values[-1], 6),
            "range": round(values[-1] - values[0], 6)}


def spearman(a: list[float], b: list[float]) -> float:
    """Rank correlation, computed here rather than imported.

    The question it answers is whether the *ordering* of the analyses survives the change
    of year -- whether an analysis that looked better on development looks better on 2010.
    Ties are averaged. scipy is not in the pinned analysis environment and one function is
    not a reason to add a dependency to it.
    """
    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            average = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = average
            i = j + 1
        return out

    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return round(cov / (va * vb), 6) if va and vb else float("nan")


def main() -> None:
    manifest = rows_of(RESULTS / "manifest_holdout.csv")
    development = {r["combination"]: r for r in rows_of(RESULTS / "conclusions.csv")}
    holdout = {r["combination"]: r for r in rows_of(RESULTS / "holdout_conclusions.csv")}
    dev_dist = json.loads((RESULTS / "distribution.json").read_text())
    hold_dist = json.loads((RESULTS / "holdout_distribution.json").read_text())
    dev_forks = {r["fork"]: r for r in rows_of(RESULTS / "sensitivity_by_fork.csv")}
    hold_forks = {r["fork"]: r
                  for r in rows_of(RESULTS / "holdout_sensitivity_by_fork.csv")}

    # ---- one row per paired analysis -------------------------------------------------
    table, unpaired, drifted, moved, unconcluded = [], [], [], [], []
    compared = 0
    for row in manifest:
        name, twin = row["combination"], row["development_combination"]
        frozen = number(row["development_skill_score"])
        here = holdout.get(name, {})
        there = development.get(twin, {})

        if frozen is not None and twin not in development:
            moved.append({"combination": name, "development_combination": twin})
            continue

        if frozen is not None and there.get("skill_score", "") == "":
            unconcluded.append({"combination": name, "development_combination": twin,
                                "why_not": there.get("why_not", "")})
        elif frozen is not None:
            compared += 1
            today = float(there["skill_score"])
            if abs(frozen - today) > FROZEN_TOLERANCE:
                drifted.append({"combination": twin, "frozen": frozen, "today": today,
                                "moved_by": round(today - frozen, 6)})

        if frozen is None or here.get("skill_score", "") == "":
            unpaired.append({
                "combination": name,
                "development": there.get("why_not", "") or "has a conclusion",
                "holdout": here.get("why_not", "") or "has a conclusion"})
            continue

        dev_skill, hold_skill = frozen, float(here["skill_score"])
        table.append({
            "combination": name,
            "development_combination": twin,
            "tier": row["tier"],
            "kind": row["kind"],
            "fork": row["fork"],
            "child": row["child"],
            "our_model": here["our_model"],
            "development_skill_score": dev_skill,
            "holdout_skill_score": hold_skill,
            "skill_holdout_minus_development": round(hold_skill - dev_skill, 6),
            "development_crps_ours": number(row["development_crps_ours"]),
            "holdout_crps_ours": number(here["crps_ours"]),
            "development_crps_reference": number(row["development_crps_reference"]),
            "holdout_crps_reference": number(here["crps_reference"]),
            "development_coverage_10_90": number(row["development_coverage_10_90"]),
            "holdout_coverage_10_90": number(here["coverage_10_90_ours"]),
            # Derived from the two frozen CRPS columns rather than read from the
            # development table, for the same reason the skill score is: `conclude.py`
            # defines it as `ours.mean_crps < reference.mean_crps` and both sides of that
            # comparison are frozen beside the row. Reading today's value instead would
            # put a re-derived figure into a reported phase-E count -- on batch 27's
            # clean-room conclusions one row flips and the count reads 28 rather than 27.
            "development_beats_reference": str(
                number(row["development_crps_ours"])
                < number(row["development_crps_reference"])),
            "holdout_beats_reference": here["beats_reference"],
            # Not derivable from the freeze: it compares against the baselines' own CRPS,
            # which `manifest_holdout.csv` does not carry, and the frozen manifest is not
            # rewritten (plan §3). So this one figure is still read from the development
            # table as it stands today, and `holdout_vs_development.json` says so.
            "development_beats_all_baselines": development[twin]["beats_all_baselines"],
            "holdout_beats_all_baselines": here["beats_all_baselines"],
        })

    if moved:
        raise SystemExit(
            "the pairing this compares on is no longer the pairing that was frozen:\n  "
            + "\n  ".join(f"{m['combination']}: frozen against "
                          f"{m['development_combination']}, which the development table "
                          f"no longer carries" for m in moved)
            + "\nThe frozen set names a development analysis this tree can no longer "
              "produce a figure for. Fix the tree, or open a batch for the change; this "
              "script does not re-pair the frozen set.")

    if drifted:
        largest = max(drifted, key=lambda d: abs(d["moved_by"]))
        print(f"{len(drifted)} frozen development figure(s) have drifted, largest "
              f"{largest['moved_by']:+.6f} on {largest['combination']}. The frozen "
              f"figures stand and are what this comparison uses.")

    table.sort(key=lambda r: -r["holdout_skill_score"])
    with (RESULTS / "holdout_vs_development.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    # ---- one row per fork, on both ---------------------------------------------------
    both = []
    for fork, dev in dev_forks.items():
        hold = hold_forks.get(fork, {})
        both.append({
            "fork": fork,
            "stage": dev["stage"],
            "kind": dev["kind"],
            "owner": dev["owner"],
            "development_largest_abs_delta_skill": number(dev["largest_abs_delta_skill"]),
            "holdout_largest_abs_delta_skill": number(
                hold.get("largest_abs_delta_skill", "")),
            "development_signed_delta_skill": number(dev["signed_delta_skill"]),
            "holdout_signed_delta_skill": number(hold.get("signed_delta_skill", "")),
            "development_moves_more_than_noise": dev["moves_more_than_reference_noise"],
            "holdout_moves_more_than_noise": hold.get(
                "moves_more_than_reference_noise", ""),
            "development_sensitivity_rank": number(dev["sensitivity_rank"]),
            "holdout_sensitivity_rank": number(hold.get("sensitivity_rank", "")),
            "agrees_on_whether_it_matters": (
                dev["moves_more_than_reference_noise"]
                == hold.get("moves_more_than_reference_noise", "")),
        })
    both.sort(key=lambda f: -(f["development_largest_abs_delta_skill"] or 0))
    with (RESULTS / "fork_sensitivity_both.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(both[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(both)

    # ---- the answer ------------------------------------------------------------------
    dev_skills = [r["development_skill_score"] for r in table]
    hold_skills = [r["holdout_skill_score"] for r in table]
    main_row = next(r for r in table if r["kind"] == "main")
    ranked_dev = sorted(dev_skills, reverse=True)
    ranked_hold = sorted(hold_skills, reverse=True)

    scored_forks = [f for f in both
                    if f["holdout_largest_abs_delta_skill"] is not None]
    (RESULTS / "holdout_vs_development.json").write_text(json.dumps({
        "what_this_is": (
            "The phase-E answer: the frozen set of 32 analyses, run on the development "
            "period and again on the held-out year, reported side by side. The pairing "
            "was fixed in batch 15 before the year was opened."),
        "the_reported_analysis": {
            "combination": main_row["combination"],
            "our_model": main_row["our_model"],
            "development_skill_score": main_row["development_skill_score"],
            "holdout_skill_score": main_row["holdout_skill_score"],
            "gap": main_row["skill_holdout_minus_development"],
            "development_crps_ours": main_row["development_crps_ours"],
            "holdout_crps_ours": main_row["holdout_crps_ours"],
            "development_crps_reference": main_row["development_crps_reference"],
            "holdout_crps_reference": main_row["holdout_crps_reference"],
            "development_coverage_10_90": main_row["development_coverage_10_90"],
            "holdout_coverage_10_90": main_row["holdout_coverage_10_90"],
            "holdout_beats_reference": main_row["holdout_beats_reference"],
            "holdout_beats_all_baselines": main_row["holdout_beats_all_baselines"],
            "rank_within_development": ranked_dev.index(
                main_row["development_skill_score"]) + 1,
            "rank_within_holdout": ranked_hold.index(
                main_row["holdout_skill_score"]) + 1,
            "of": len(table),
        },
        "how_hard_the_year_was": {
            "reference_crps_development": main_row["development_crps_reference"],
            "reference_crps_holdout": main_row["holdout_crps_reference"],
            "note": ("The denominator of every skill score, on a model nobody here "
                     "tuned. Raw CRPS is not comparable across the two datasets -- "
                     "different year, four splits rather than eight, 192 cells rather "
                     "than 371 -- and this is the figure that says so."),
        },
        "the_two_spreads": {
            "development": {**spread(dev_skills),
                            "noise_band": dev_dist["reference_noise_band"]["skill_band"]},
            "holdout": {**spread(hold_skills),
                        "noise_band": hold_dist["reference_noise_band"]["skill_band"]},
            "note": ("Each dataset's noise band is measured on that dataset, from its "
                     "own four repeats of the unseeded reference."),
        },
        "does_the_conclusion_hold_on_2010": {
            "beats_the_reference": sum(1 for r in table
                                       if r["holdout_beats_reference"] == "True"),
            "beats_both_required_baselines": sum(
                1 for r in table if r["holdout_beats_all_baselines"] == "True"),
            "of": len(table),
            "on_development_it_was": {
                "beats_the_reference": sum(
                    1 for r in table if r["development_beats_reference"] == "True"),
                "beats_both_required_baselines": sum(
                    1 for r in table if r["development_beats_all_baselines"] == "True"),
                "beats_the_reference_is_from": (
                    "the frozen CRPS columns of results/manifest_holdout.csv"),
                "beats_both_required_baselines_is_from": (
                    "results/conclusions.csv as it stands today, because the baselines' "
                    "own CRPS is not frozen beside the row and the frozen manifest is "
                    "not rewritten. It is the one development figure in this file that "
                    "is re-derived rather than read from the freeze, and a re-run of the "
                    "development half can therefore move it."),
            },
            "rows_that_beat_the_reference_on_development_and_not_on_the_holdout": sorted(
                r["combination"] for r in table
                if r["development_beats_reference"] == "True"
                and r["holdout_beats_reference"] != "True"),
            "rows_that_beat_it_on_the_holdout_and_not_on_development": sorted(
                r["combination"] for r in table
                if r["development_beats_reference"] != "True"
                and r["holdout_beats_reference"] == "True"),
        },
        "does_the_ordering_transfer": {
            "spearman_rank_correlation": spearman(dev_skills, hold_skills),
            "rows": len(table),
            "note": ("Whether an analysis that scored better on development scores "
                     "better on 2010. This is the question a development-set ranking "
                     "is used for, and it is answered here rather than assumed."),
        },
        "the_gap": {
            **spread([r["skill_holdout_minus_development"] for r in table]),
            "rows_worse_on_the_holdout": sum(
                1 for r in table if r["skill_holdout_minus_development"] < 0),
            "rows_better_on_the_holdout": sum(
                1 for r in table if r["skill_holdout_minus_development"] > 0),
            "note": ("Holdout skill minus development skill, per analysis. A negative "
                     "value is an analysis that did better on the data it was developed "
                     "against than on the year it had never seen."),
        },
        "which_forks_matter_on_both": {
            "forks": len(both),
            "agreeing_on_whether_the_fork_matters": sum(
                1 for f in scored_forks if f["agrees_on_whether_it_matters"]),
            "of_forks_scored_on_both": len(scored_forks),
            "matter_on_development_only": sorted(
                f["stage"] for f in scored_forks
                if f["development_moves_more_than_noise"] == "True"
                and f["holdout_moves_more_than_noise"] != "True"),
            "matter_on_the_holdout_only": sorted(
                f["stage"] for f in scored_forks
                if f["development_moves_more_than_noise"] != "True"
                and f["holdout_moves_more_than_noise"] == "True"),
            "matter_on_both": sorted(
                f["stage"] for f in scored_forks
                if f["development_moves_more_than_noise"] == "True"
                and f["holdout_moves_more_than_noise"] == "True"),
            "sensitivity_rank_correlation": spearman(
                [f["development_largest_abs_delta_skill"] for f in scored_forks],
                [f["holdout_largest_abs_delta_skill"] for f in scored_forks]),
        },
        "rows_not_paired": unpaired,
        "frozen_pairing_verified": {
            "checked": len(table),
            "against": "results/conclusions.csv, as it stands today",
            "tolerance": FROZEN_TOLERANCE,
            "verdict": ("the frozen pairing stands" if not moved
                        else f"{len(moved)} pairing(s) moved"),
            "pairings_that_moved": {
                "rows": moved,
                "note": ("Fatal, and the run stops before anything is written: a frozen "
                         "row whose development twin the table no longer concludes is "
                         "paired with an analysis this tree can no longer produce a "
                         "figure for. This file exists, so there were none."),
            },
            "development_twins_without_a_conclusion_today": {
                "rows": unconcluded,
                "note": ("The twin is still in the development table but has no skill "
                         "score in it. Reported, not fatal: the frozen figure is a "
                         "record of what was paired and does not need re-deriving."),
            },
            "frozen_figures_that_drifted": {
                "rows": len(drifted),
                "of": compared,
                "largest_absolute_move": (
                    round(max(abs(d["moved_by"]) for d in drifted), 6)
                    if drifted else 0.0),
                "development_noise_band": dev_dist[
                    "reference_noise_band"]["skill_band"],
                "largest_move_is_inside_the_band": (
                    max(abs(d["moved_by"]) for d in drifted)
                    <= dev_dist["reference_noise_band"]["skill_band"]
                    if drifted else True),
                "detail": drifted,
                "note": ("Reported, never absorbed: the frozen figures stand and are "
                         "what the comparison above uses. The development skill score "
                         "divides by the reference model, which is unseeded, so a re-run "
                         "of the development half re-draws it and moves every figure "
                         "with it. The band is this dataset's own four repeats of that "
                         "reference, so it says whether a move is larger than the "
                         "reference's own. freeze_holdout_manifest.py reports the same "
                         "drift on the same rows under drift_under_an_unchanged_set."),
            },
        },
        "sources": {
            "the frozen pairing": "results/manifest_holdout.csv",
            "one row per paired analysis": "results/holdout_vs_development.csv",
            "one row per fork, both datasets": "results/fork_sensitivity_both.csv",
            "each dataset's own distribution": ["results/distribution.json",
                                                "results/holdout_distribution.json"],
        },
    }, indent=1, sort_keys=False) + "\n")

    print(f"{len(table)} paired analyses. Reported: development "
          f"{main_row['development_skill_score']:+.4f} -> holdout "
          f"{main_row['holdout_skill_score']:+.4f} "
          f"({main_row['skill_holdout_minus_development']:+.4f})")
    print(f"development spread {min(dev_skills):+.4f}..{max(dev_skills):+.4f}; "
          f"holdout spread {min(hold_skills):+.4f}..{max(hold_skills):+.4f}; "
          f"rank correlation {spearman(dev_skills, hold_skills):+.3f}")
    print(f"-> {(RESULTS / 'holdout_vs_development.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
