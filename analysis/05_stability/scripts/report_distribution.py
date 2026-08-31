"""State what the perturbation set concluded: the distribution, and what moves it.

`/perturb report`. `collect_conclusions.py` gathers one row per analysis; this script is
where that table becomes the phase-D answer. The plan (§8, phase D) asks for two things
and this file is both of them:

* **a distribution of conclusions over reasonable analyses**, not a headline with a
  robustness footnote; and
* **a stated answer to whether the conclusion moves when a reasonable alternative is taken
  at each fork, and which forks it is most sensitive to** -- which the plan calls the most
  valuable single output of the project.

## The yardstick, and why it is not a threshold anybody chose

"Does the conclusion move" needs a scale to be answered on, and picking one would be a
judgment call of exactly the kind this node exists to expose. So it is measured instead.
The reference model is unseeded and was scored four times; our model's skill score against
each of those four repeats is in `03_compare`'s `paired_summary.csv`, and the spread of
those four is **how far the reported skill score moves when nothing changes but the
reference's own sampler**. A fork whose largest move is inside that band has not been shown
to move the conclusion at all.

That is the skill-space twin of the CRPS noise floor the project has quoted since batch 7,
and it comes from the same four repeats. Both are read from files here; neither is typed.

## Comparability, which the weighting fork breaks

A skill score is a ratio and is dimensionless, so all thirty-two are on one axis -- which
is the reason the project reports a ratio rather than a CRPS (`readme-at-start.md`). Mean
CRPS is not: under case weighting the mean is over a re-weighted set of cells and comes out
near 88 rather than near 19, and putting those in one range would report a spread that is
an artefact of the unit. So every CRPS statistic here is computed **within a weighting
group**, and which group a row is in is read from its own fork and child columns rather
than guessed from the size of the number.

## The holdout half

`--dataset holdout` reports the same three files for the frozen phase-E set, from
`holdout_conclusions.csv` and the holdout's own main path. Every yardstick is recomputed on
that dataset rather than carried over: the reference was re-scored four times on 2010 too,
so the noise band the holdout's forks are judged against is 2010's, not development's. A
band imported from the other dataset would be a number from one analysis deciding what
counts as a move in another.

The two are **not** pooled. `pair_holdout_development.py` joins them row by row on the
pairing batch 15 froze, which is where the question phase E exists to answer -- how far the
development spread transfers -- is actually answered.

Writes, at this node:
  results/distribution.json         the phase-D answer, and the counts behind it
  results/distribution_rows.csv     one row per analysis, ranked by skill score
  results/sensitivity_by_fork.csv   one row per fork: how far the conclusion moved
  results/holdout_distribution.json         the same three, for the held-out year
  results/holdout_distribution_rows.csv
  results/holdout_sensitivity_by_fork.csv

Seeds: none. Every number is an arithmetic summary of stored scores.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import median

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
RESULTS = NODE / "results"
COMPARE = ROOT / "analysis/04_score/03_compare/results"

# Forks the tree does not carry, with the reason they are absent. An absence has to be a
# visible decision (`AGENTS.md` §4), and the one fork this project considered and removed
# is removed for a reason that is a fact about the reference model rather than a
# preference. Text, not a number: nothing downstream computes with it.
NOT_PERTURBED = {
    "the forecast horizon": (
        "forced by the reference model, so a combination at another horizon has no "
        "reference to be compared against and the root's conclusion -- a ratio to the "
        "reference -- is uncomputable there. Removed by batch 4's reconnaissance, not by "
        "a budget decision; the plan's phase D records it."),
}


def rows_of(path: Path) -> list[dict]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> float | None:
    return float(value) if value not in ("", None) else None


def noise_band(our_model: str, main_combo: str) -> dict:
    """How far the reported skill score moves when only the reference's sampler does.

    The reference is unseeded and was evaluated four times. `03_compare` scores our model
    against each repeat separately as well as against their mean, so the spread of those
    four skill scores is a measurement of the conclusion's own irreducible noise -- in the
    units the conclusion is reported in, which the CRPS floor is not.
    """
    paired = rows_of(COMPARE / main_combo / "paired_summary.csv")
    repeats = [r for r in paired
               if r["model"] == our_model and r["against"].startswith("reference_r")
               and r["weighting"] == "unweighted"]
    if not repeats:
        raise SystemExit(f"no per-repeat comparison for our model in "
                         f"04_score/03_compare/results/{main_combo}/paired_summary.csv")
    skills = sorted(float(r["skill_score"]) for r in repeats)
    notes = json.loads((COMPARE / main_combo / "comparison_notes.json").read_text())
    return {
        "repeats": [r["against"] for r in repeats],
        "skill_against_each_repeat": skills,
        "skill_band": round(skills[-1] - skills[0], 6),
        "crps_floor": notes["noise_floor_largest_repeat_pair_mean_diff"],
        "source": [f"analysis/04_score/03_compare/results/{main_combo}/paired_summary.csv",
                   f"analysis/04_score/03_compare/results/{main_combo}/comparison_notes.json"],
        "means": ("the spread of our model's skill score against the four repeats of the "
                  "unseeded reference. A fork whose largest move is inside this band has "
                  "not been shown to move the conclusion."),
    }


def weighting_of(row: dict, aggregate_fork: dict) -> str:
    """Which aggregation this row's mean is over, read from the row's own fork columns."""
    moved = dict(zip(row["fork"].split("+"), row["child"].split("+")))
    return moved.get(aggregate_fork["fork"], aggregate_fork["main_child"])


def spread(values: list[float]) -> dict:
    values = sorted(values)
    return {"n": len(values), "min": round(values[0], 6),
            "median": round(median(values), 6), "max": round(values[-1], 6)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dataset", choices=("development", "holdout"),
                        default="development",
                        help="which set to report: the development perturbation set, or "
                             "the frozen phase-E set on the held-out year")
    args = parser.parse_args()
    holdout = args.dataset == "holdout"
    prefix = "holdout_" if holdout else ""
    # The combination this distribution is reported around. Everything below that used to
    # say "main" says this instead, including which `03_compare` directory the noise band
    # is measured in: the holdout's forks are judged against 2010's reference re-runs.
    main_combo = "main__holdout" if holdout else "main"

    conclusions = rows_of(RESULTS / f"{prefix}conclusions.csv")
    forks = rows_of(RESULTS / "forks.csv")
    notes = json.loads((RESULTS / "manifest_notes.json").read_text())
    freeze = (json.loads((RESULTS / "holdout_freeze.json").read_text())
              if holdout else None)
    # What the set actually cost, summed from the driver's own record rather than from
    # `cost_planned_vs_actual.json`, which compares only the rows the manifest costed.
    ran = sum(float(r["seconds"]) for r in rows_of(RESULTS / f"run_status{'_holdout' if holdout else ''}.csv")
              if r["seconds"] not in ("", None))
    reported = json.loads(
        (ROOT / f"analysis/results/{main_combo}/conclusion.json").read_text())

    aggregate_fork = next(f for f in forks if f["kind"] == "scoring")
    band = noise_band(reported["our_model"], main_combo)

    scored = [r for r in conclusions if r["skill_score"] != ""]
    unscored = [r for r in conclusions if r["skill_score"] == ""]
    if not any(r["combination"] == main_combo for r in scored):
        raise SystemExit(f"no conclusion for {main_combo}: there is nothing to report a "
                         f"distribution around")

    # ---- one row per analysis -------------------------------------------------------
    table = []
    for row in scored:
        delta = number(row["delta_skill_vs_main"])
        table.append({
            "combination": row["combination"],
            "tier": row["tier"],
            "kind": row["kind"],
            "fork": row["fork"],
            "child": row["child"],
            "our_model": row["our_model"],
            "weighting": weighting_of(row, aggregate_fork),
            "skill_score": row["skill_score"],
            "delta_skill_vs_main": row["delta_skill_vs_main"],
            "inside_reference_noise_band": abs(delta) <= band["skill_band"],
            "crps_ours": row["crps_ours"],
            "crps_reference": row["crps_reference"],
            "coverage_10_90_ours": row["coverage_10_90_ours"],
            "coverage_25_75_ours": row["coverage_25_75_ours"],
            "beats_reference": row["beats_reference"],
            "beats_all_baselines": row["beats_all_baselines"],
            "paired_mean_diff_vs_reference": row["paired_mean_diff_vs_reference"],
            "paired_se_cluster_split": row["paired_se_cluster_split"],
            "resolvable_difference_floor": row["resolvable_difference_floor"],
            "interaction": row["interaction"],
        })
    table.sort(key=lambda r: -float(r["skill_score"]))
    with (RESULTS / f"{prefix}distribution_rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    # ---- one row per fork -----------------------------------------------------------
    # A fork's move is the largest absolute change in the reported conclusion across the
    # tier-1 rows that take one of its children. Tier-2 rows move two forks at once and
    # cannot be attributed to either, so they are counted separately, below.
    by_fork = []
    for fork in forks:
        mine = [r for r in table if r["tier"] == "1" and r["fork"] == fork["fork"]]
        deltas = {r["combination"]: float(r["delta_skill_vs_main"]) for r in mine}
        largest = max(deltas, key=lambda c: abs(deltas[c])) if deltas else None
        by_fork.append({
            "fork": fork["fork"],
            "stage": fork["stage"],
            "kind": fork["kind"],
            "owner": fork["owner"],
            "main_child": fork["main_child"],
            "children_perturbed": ";".join(sorted(r["child"] for r in mine)),
            "rows": len(mine),
            "largest_move_combination": largest or "",
            "largest_abs_delta_skill": round(abs(deltas[largest]), 6) if largest else "",
            "signed_delta_skill": round(deltas[largest], 6) if largest else "",
            "moves_more_than_reference_noise": (
                abs(deltas[largest]) > band["skill_band"] if largest else ""),
            "skill_span_over_children": (
                round(max(deltas.values()) - min(deltas.values()), 6)
                if len(deltas) > 1 else 0.0 if deltas else ""),
        })
    by_fork.sort(key=lambda f: -(f["largest_abs_delta_skill"] or 0))
    for rank, entry in enumerate(by_fork, start=1):
        entry["sensitivity_rank"] = rank
    with (RESULTS / f"{prefix}sensitivity_by_fork.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(by_fork[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(by_fork)

    # ---- the answer -----------------------------------------------------------------
    skills = [float(r["skill_score"]) for r in table]
    main_skill = next(float(r["skill_score"]) for r in table
                      if r["combination"] == main_combo)
    weightings = sorted({r["weighting"] for r in table})
    crps_by_weighting = {
        w: spread([float(r["crps_ours"]) for r in table if r["weighting"] == w])
        for w in weightings}
    moved = [f for f in by_fork if f["moves_more_than_reference_noise"] is True]
    still = [f for f in by_fork if f["moves_more_than_reference_noise"] is False]
    pairs = [r for r in table if r["interaction"] != ""]
    coverage = [float(r["coverage_10_90_ours"]) for r in table]

    (RESULTS / f"{prefix}distribution.json").write_text(json.dumps({
        "what_this_is": (
            "The phase-D result: the conclusion this project reports, computed once per "
            "analysis in a set of analyses fixed before any of them ran. It is a "
            "distribution, and the reported number is one member of it."),
        "dataset": reported["dataset"],
        "reported_conclusion": {
            "combination": main_combo,
            "our_model": reported["our_model"],
            "skill_score": main_skill,
            "crps_ours": reported["crps_ours"],
            "crps_reference": reported["crps_reference"],
            "rank_within_the_distribution": (
                sorted(skills, reverse=True).index(main_skill) + 1),
            "of": len(skills),
        },
        "manifest": {
            "rows": len(conclusions),
            "with_a_conclusion": len(table),
            "without": [{"combination": r["combination"], "why": r["why_not"]}
                        for r in unscored],
            "cut_for_budget": [],
            "cut_note": (
                (f"Nothing was cut. The phase-E set was frozen at "
                 f"{freeze['estimated_hours_total']} h against a "
                 f"{freeze['budget_hours_both_datasets']} h budget for both datasets, of "
                 f"which development spent 3.66, and it ran in {ran / 3600:.2f} h "
                 f"(`results/run_status_holdout.csv`, summed). Nothing may be cut here "
                 f"in any case: the set was fixed before the year was opened.")
                if holdout else
                f"Nothing was cut. Tier 1 was planned at "
                f"{notes['estimated_hours_tier1_both_datasets']} h across both datasets "
                f"against a {notes['budget_hours_both_datasets']} h budget, and the "
                f"whole development manifest ran in {ran / 3600:.2f} h "
                f"(`results/run_status.csv`, summed). "
                f"`manifest_notes.json` carries the cut order against the day something "
                f"is cut."),
            "forks_not_perturbed": NOT_PERTURBED,
        },
        "reference_noise_band": band,
        "skill_score": {
            **spread(skills),
            "main_path": main_skill,
            "rows_above_main": sum(1 for s in skills if s > main_skill),
            "rows_below_main": sum(1 for s in skills if s < main_skill),
            "rows_inside_the_reference_noise_band": sum(
                1 for r in table if r["inside_reference_noise_band"]),
        },
        "does_the_conclusion_hold": {
            "beats_the_reference": sum(1 for r in table
                                       if r["beats_reference"] == "True"),
            "beats_both_required_baselines": sum(
                1 for r in table if r["beats_all_baselines"] == "True"),
            "of": len(table),
            "rows_where_it_does_not_beat_the_reference": sorted(
                r["combination"] for r in table if r["beats_reference"] != "True"),
            "rows_where_a_required_baseline_beats_it": sorted(
                r["combination"] for r in table if r["beats_all_baselines"] != "True"),
        },
        "crps_ours_by_weighting": crps_by_weighting,
        "crps_note": ("Mean CRPS is comparable only within a weighting: a re-weighted "
                      "mean is over a different set of weights and is not on the same "
                      "axis. The skill score is a ratio and is comparable across all of "
                      "them, which is why the conclusion is reported as one."),
        "coverage_10_90": {**spread(coverage), "nominal": 0.80,
                           "note": ("Calibration moves further than the score does. "
                                    "§2's rule is that a badly calibrated CRPS winner "
                                    "has not won, so this range is reported beside the "
                                    "skill range and not under it.")},
        "sensitivity": {
            "forks": len(by_fork),
            "moving_more_than_the_reference_noise_band": [
                {"fork": f["fork"], "kind": f["kind"],
                 "largest_abs_delta_skill": f["largest_abs_delta_skill"]}
                for f in moved],
            "not_moving_more_than_it": [
                {"fork": f["fork"], "kind": f["kind"],
                 "largest_abs_delta_skill": f["largest_abs_delta_skill"]}
                for f in still],
            "by_kind_largest": {
                kind: max((f["largest_abs_delta_skill"] for f in by_fork
                           if f["kind"] == kind and f["largest_abs_delta_skill"] != ""),
                          default=None)
                for kind in sorted({f["kind"] for f in by_fork})},
        },
        "interaction": {
            "pairs": len(pairs),
            **spread([float(r["interaction"]) for r in pairs]),
            "largest_absolute": max(abs(float(r["interaction"])) for r in pairs),
            "largest_absolute_pair": max(
                pairs, key=lambda r: abs(float(r["interaction"])))["combination"],
            "note": ("A pair's interaction is its own move minus the sum of its two "
                     "rows' moves. Where the largest one exceeds the main effects behind "
                     "it, the one-at-a-time table above cannot be added up."),
        },
        "sources": {
            "one row per analysis": f"results/{prefix}distribution_rows.csv",
            "one row per fork": f"results/{prefix}sensitivity_by_fork.csv",
            "the table they summarise": f"results/{prefix}conclusions.csv",
            "each row's own conclusion": "analysis/results/<combination>/conclusion.json",
        },
    }, indent=1, sort_keys=False) + "\n")

    print(f"{args.dataset}: {len(table)} analyses; skill {min(skills):.4f} to {max(skills):.4f} "
          f"around {main_skill:.4f}; reference noise band {band['skill_band']:.4f}")
    print(f"{len(moved)} of {len(by_fork)} forks move the conclusion further than that: "
          f"{', '.join(f['stage'] for f in moved)}")
    print(f"-> {(RESULTS / f'{prefix}distribution.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
