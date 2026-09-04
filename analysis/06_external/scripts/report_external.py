#!/usr/bin/env python3
"""Report the external check: the sibling countries beside Laos, on one axis.

Two questions, and the file answers both from the stored conclusions rather than from
anything computed here for the first time.

**Does the margin hold?** The reported conclusion is a skill score against the reference
model, `1 - CRPS_ours / CRPS_reference`, and it is relative precisely so that datasets whose
raw CRPS differ can be read together. Thailand's mean case count is half Vietnam's and four
times Laos's; the ratio is what controls for that.

**Does the drop replicate?** Laos scored +0.1485 on its development backtest and +0.0868 on
the year it had never seen — a drop of 0.0617 — and phase E's largest open question is
whether that is about 2010, about one-year backtests, or about an agent optimising against a
development set. This project cannot answer it from inside itself: it has one held-out year
and four splits. Two more countries, evaluated on the same months under the same two
schemes, are two more measurements of the same difference. They do not settle the question
either, and this file does not claim they do — three countries from one harmonisation are
not a sample. What they can do is say whether the drop is a thing that happens repeatedly or
a thing that happened once.

**Every figure is reported against the reference's own re-run spread.** The reference is
unseeded, and on each dataset it is scored four times; the largest paired difference between
two of those repeats is the size of a difference that dataset cannot attribute to a model at
all. It is a draw and not a constant — the Lao development band has now been drawn four
times, at 0.0218 to 0.0483 of skill — so every band below is reported as the draw it is.

**The pool's independent reconstruction is not available here, and that is recorded rather
than left blank.** `check_pool.py` rebuilds a pool from its members' own separate
evaluations, and a member is evaluated separately only under the family fork's own
combination — a perturbation row. The external check runs the reported model unchanged and
perturbs nothing, so no such row exists on these four datasets and no order of execution
would have produced one. `AGENTS.md` §4: an absence must be a visible decision.

Writes:
  results/external_conclusions.csv   one row per analysis, Laos's two included
  results/external_vs_laos.json      the margins, the drops, and what each is measured
                                     against
  results/pool_reconstruction_external.json   why the second path is not available here

Seeds: none. This reads stored conclusions and arranges them.

Usage:  "$PYTHON" scripts/report_external.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
RESULTS = NODE / "results"
ANALYSIS = ROOT / "analysis"
MANIFEST = RESULTS / "manifest_external.csv"
COMPARE = ANALYSIS / "04_score/03_compare/results"
ENSEMBLE = ANALYSIS / "03_models/03_candidate/c_ensemble/results"

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
import combos  # noqa: E402

#: Every analysis this file puts on one axis: the two Lao arrangements the project already
#: reports, and the external rows the manifest names. The Lao pair is not re-computed here
#: -- it is read from the same `conclusion.json` the headline is read from.
LAO = [("Laos", "main", "development backtest, 3/8/3, evaluating 2008-01..2009-12"),
       ("Laos", "main__holdout", "final year, 3/4/3, evaluating 2010")]


def conclusion(combo: str) -> dict:
    path = ANALYSIS / "results" / combo / "conclusion.json"
    if not path.exists():
        raise SystemExit(f"no conclusion for {combo}: {path} does not exist. "
                         f"The row that produces it has not run.")
    return json.loads(path.read_text())


def notes(combo: str) -> dict:
    return json.loads((COMPARE / combo / "comparison_notes.json").read_text())


def arrangement_of(combo: str) -> str:
    """`development` or `final`, from the dataset the combination faces."""
    return "final" if combos.dataset(combo).endswith(("Final", "holdout")) else "development"


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    rows = list(csv.DictReader(MANIFEST.open()))
    wanted = LAO + [(r["country"], r["combination"], r["arrangement"])
                    for r in rows if r["status"] == "planned"]

    table, by_country = [], {}
    for country, combo, description in wanted:
        c = conclusion(combo)
        n = notes(combo)
        table.append({
            "country": country,
            "combination": combo,
            "dataset": c["dataset"],
            "arrangement": arrangement_of(combo),
            "description": description,
            "our_model": c["our_model"],
            "skill_score": c["skill_score"],
            "crps_ours": c["crps_ours"],
            "crps_reference": c["crps_reference"],
            "coverage_10_90_ours": c["coverage_10_90_ours"],
            "coverage_10_90_reference": c["coverage_10_90_reference"],
            "n_cells": c["n_cells"],
            "n_locations": c["n_locations"],
            "n_splits": c["n_splits"],
            "beats_reference": c["beats_reference"],
            "beats_all_baselines": c["beats_all_baselines"],
            "paired_mean_diff_vs_reference": c["paired_mean_diff_vs_reference"],
            "paired_se_cluster_split": c["paired_se_cluster_split"],
            "standard_errors_from_reference": (
                abs(c["paired_mean_diff_vs_reference"]) / c["paired_se_cluster_split"]
                if c["paired_se_cluster_split"] else None),
            "reference_repeat_spread_crps": c["resolvable_difference_floor"],
            "reference_repeat_spread_skill":
                c["resolvable_difference_floor"] / c["crps_reference"],
            "crps_by_model": json.dumps(c["crps_by_model"], sort_keys=True),
            "reference_unpaired_sd_across_splits": n["unpaired_sd_across_splits_reference"],
        })
        by_country.setdefault(country, {})[arrangement_of(combo)] = table[-1]

    with (RESULTS / "external_conclusions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)

    drops = {}
    for country, pair in by_country.items():
        if {"development", "final"} - set(pair):
            drops[country] = {"complete": False,
                              "why": "only one of the two arrangements has run"}
            continue
        dev, fin = pair["development"], pair["final"]
        drops[country] = {
            "complete": True,
            "skill_development": dev["skill_score"],
            "skill_final_year": fin["skill_score"],
            "drop": fin["skill_score"] - dev["skill_score"],
            "beats_reference_development": dev["beats_reference"],
            "beats_reference_final_year": fin["beats_reference"],
            "beats_all_baselines_development": dev["beats_all_baselines"],
            "beats_all_baselines_final_year": fin["beats_all_baselines"],
            "crps_development": [dev["crps_ours"], dev["crps_reference"]],
            "crps_final_year": [fin["crps_ours"], fin["crps_reference"]],
            "coverage_10_90_development": dev["coverage_10_90_ours"],
            "coverage_10_90_final_year": fin["coverage_10_90_ours"],
            # The drop is a difference of two ratios, each measured against a reference
            # drawn once. Both draws move, so the band on the drop is the two added.
            "reference_spread_skill_development": dev["reference_repeat_spread_skill"],
            "reference_spread_skill_final_year": fin["reference_repeat_spread_skill"],
            "drop_exceeds_the_two_bands_together": abs(
                fin["skill_score"] - dev["skill_score"]) > (
                dev["reference_repeat_spread_skill"] + fin["reference_repeat_spread_skill"]),
            "cells": [dev["n_cells"], fin["n_cells"]],
            "provinces": [dev["n_locations"], fin["n_locations"]],
        }

    complete = {k: v for k, v in drops.items() if v["complete"]}
    external = {k: v for k, v in complete.items() if k != "Laos"}
    lao = complete.get("Laos")
    summary = {
        "what_this_is": (
            "the reported model, unchanged, on the sibling harmonised datasets for "
            "Thailand and Vietnam, in the same two arrangements Laos is reported in and "
            "on the same months. No model was developed on these files and no fork moves "
            "in any of these rows"),
        "per_country": drops,
        "margin_holds_everywhere": all(
            v["beats_reference_development"] and v["beats_reference_final_year"]
            for v in complete.values()),
        "beats_reference_count": sum(
            int(v["beats_reference_development"]) + int(v["beats_reference_final_year"])
            for v in complete.values()),
        "analyses_compared": 2 * len(complete),
        "drop_replicates": (
            all(v["drop"] < 0 for v in external.values()) if external else None),
        "drop_direction_by_country": {k: ("worse on the final year" if v["drop"] < 0
                                          else "better on the final year")
                                      for k, v in complete.items()},
        "lao_drop": lao["drop"] if lao else None,
        "external_drops": {k: v["drop"] for k, v in external.items()},
        "external_drop_mean": (sum(v["drop"] for v in external.values()) / len(external)
                               if external else None),
        "what_this_does_not_establish": (
            "three countries from one harmonisation are not a sample, and the two "
            "sibling analyses were not held out from anything -- no model was developed "
            "on them, so there was nothing to hold them out from. What they can say is "
            "whether the development-to-final-year drop measured on Laos is a thing that "
            "happens repeatedly or a thing that happened once"),
        "every_band_is_a_draw": (
            "the reference model is unseeded and is scored four times on each dataset; "
            "the band each figure is measured against is the largest paired difference "
            "between two of those repeats, which is itself a draw. On Laos's development "
            "backtest that band has been drawn four times across this project's runs, at "
            "0.0218 to 0.0483 of skill"),
    }
    (RESULTS / "external_vs_laos.json").write_text(json.dumps(summary, indent=2) + "\n")

    # The second path behind the pool, and why it is not available on these datasets.
    reconstruction = {}
    for row in rows:
        combo = row["combination"]
        path = ENSEMBLE / combo / "pool_check.json"
        if not path.exists():
            continue
        document = json.loads(path.read_text())["reconstruction"]
        reconstruction[combo] = {
            "mean_crps_as_run": document["mean_crps_as_run"],
            "mean_crps_rebuilt": document["mean_crps_rebuilt"],
            "not_done_because": document["not_done_because"],
        }
    (RESULTS / "pool_reconstruction_external.json").write_text(json.dumps({
        "what_this_is": (
            "whether each external pool could be rebuilt from its members' own separate "
            "evaluations, and why not where it could not"),
        "why_it_is_not_available_here": (
            "a candidate family is evaluated on its own only under the family fork's own "
            "combination, which is a perturbation row. The external check runs the "
            "reported model unchanged and moves no fork, so no such row exists on these "
            "four datasets. This is not the ordering defect batch 28 removed -- no order "
            "of execution would produce the missing runs -- and it is recorded here "
            "rather than left blank because an absence has to be a visible decision "
            "(AGENTS.md §4)"),
        "what_it_would_cost_to_have": (
            "two more model evaluations per external dataset, running candidate 1 and "
            "candidate 2 on their own. Not run: the check the plan asks for is the "
            "reported model unchanged, and adding rows to it would make it a small "
            "perturbation set on data the project does not report a distribution over"),
        "combinations": reconstruction,
    }, indent=2) + "\n")

    for r in table:
        print(f"{r['country']:9s} {r['arrangement']:12s} skill {r['skill_score']:+.4f}  "
              f"CRPS {r['crps_ours']:8.3f} vs {r['crps_reference']:8.3f}  "
              f"cells {r['n_cells']:5d}  beats reference {r['beats_reference']}  "
              f"band {r['reference_repeat_spread_skill']:.4f}")
    for country, v in drops.items():
        if v["complete"]:
            print(f"{country:9s} drop {v['drop']:+.4f} "
                  f"({v['skill_development']:+.4f} -> {v['skill_final_year']:+.4f}), "
                  f"outside the two bands together: "
                  f"{v['drop_exceeds_the_two_bands_together']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
