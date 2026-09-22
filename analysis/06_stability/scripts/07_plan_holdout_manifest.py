#!/usr/bin/env python3
"""`/perturb plan`, for phase E: plan and freeze the set of analyses the held-out year will be
evaluated across, before the year is opened.

**What the freeze is for.** Plan §3 opens 2010 once, and everything that makes that opening a
measurement rather than a selection rests on this file: `results/manifest_holdout.csv` fixes
which configurations run, `results/holdout_freeze.json` records its sha256 and the commit it
was fixed at, and `/validate invariants`' `freeze` check asserts afterwards that the file still
hashes to what was recorded and that no holdout result existed at that commit. A row added
after a holdout number has been seen is the failure this is built to make visible.

**The set.** Four tiers, the same discipline as the development manifest:

- **Tier 0** -- the reported comparison: the pre-registered main path (`h_levelOnlyBoosting`,
  chosen in batch 14 by a rule written before the results were seen, and kept at the freeze --
  plan §4b, 2026-09-22, human-set) and the two required baselines. Stage 1 alone needs no row
  of its own: every two-stage row's `conclusion.json` scores it on the same cells, which is
  what plan §2 makes the primary comparison.
- **Tier 1** -- the not-taken `04_stage2` siblings. Four are configurations of the verified
  parametrised pipeline and run; five are not, and say so with the reason.
- **Tier 2** -- the 26 parametric perturbations of the development v2 set, under holdout names,
  so that every judgment call measured on development is measured again on the held-out year
  and the two are paired by row name.
- **Tier 3** -- the five alternatives that need machinery this project has not built, carried
  forward unchanged with their reasons.

**Each row is executable before it is frozen.** `lib/holdout_eval.holdout_combinations()` says
what every row means; this script refuses a manifest and a configuration set that disagree in
either direction, and refuses to write at all unless `results/holdout_runner_verification.json`
records that the machinery reproduced the stored development results exactly
(`06_verify_holdout_runner.py`, run first). A frozen row nobody can run is a set that will be
edited after the year opens.

**Costs** are estimated, not guessed: a tier-2 row's development wall-clock
(`results/run_log_v2.csv`) scaled by the ratio of total training months between the holdout
schedule and the development one, since a run's cost is dominated by fitting stage 1 once per
province per split over the training window. The baselines carry their measured development
cost. `BUDGET_WALL_SECONDS` is the ceiling carried over from phase D.

**Re-running this script does not re-freeze.** Once `holdout_freeze.json` exists, the script
verifies instead: it rebuilds the manifest in memory, compares it with the frozen file, and
writes `results/holdout_freeze_check.json`. A difference is an error, not a rewrite.

Seeds: none drawn.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/06_stability
ANALYSIS = NODE.parents[0]
ROOT = ANALYSIS.parent
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.holdout_eval import HOLDOUT_SCHEME, MAIN, SUFFIX, holdout_combinations  # noqa: E402

RESULTS = NODE / "results"
MANIFEST = RESULTS / "manifest_holdout.csv"
SUMMARY = RESULTS / "manifest_holdout_summary.json"
FREEZE = RESULTS / "holdout_freeze.json"
FREEZE_CHECK = RESULTS / "holdout_freeze_check.json"
VERIFICATION = RESULTS / "holdout_runner_verification.json"
DEV_MANIFEST = RESULTS / "manifest.csv"
DEV_RUN_LOG = RESULTS / "run_log_v2.csv"
DEV_CONCLUSIONS = RESULTS / "conclusions_v2.csv"
DEV_DISTRIBUTION = RESULTS / "distribution_v2.json"
DEV_SCHEDULE = ANALYSIS / "01_data" / "03_backtest_scheme" / "results" / "split_schedule.csv"
STAGE2 = ANALYSIS / "04_stage2"
PREPARE = ANALYSIS / "01_data" / "01_prepare" / "results"

BUDGET_WALL_SECONDS = 3600  # the phase-D ceiling, carried over (agent-autonomous, revisable)
SENSITIVITY_POINTS = 2.0    # "moves the size", unchanged from v1 and v2 so the three compare

FIELDS = ["combination", "tier", "development_row", "node", "parameter", "main_value", "value",
          "basis", "informativeness_rank", "est_cost_s", "cumulative_cost_s", "n_expected_cells",
          "config_digest", "status", "reason_if_not_run"]

# The five siblings the parametrised pipeline does not express, with the reason they are not
# run on the held-out year. Each is a node in the tree and keeps its development result.
TIER1_NOT_RUN = {
    "a_linearLags": "+0.78% vs stage 1 alone on development",
    "b_gradientBoosting": "+6.25% on development",
    "c_bayesianRidge": "+7.73% on development",
    "d_linearClimate": "+3.05% on development",
    "e_pooledRandomForest": "-0.63% on development but 64.4% coverage, which plan §2 disqualifies",
}
TIER1_NOT_RUN_REASON = (
    "trained on stage 1's in-sample one-step residual -- a construction lib/stage2_perturb.py "
    "does not express, so running it on the holdout means a holdout-capable rewrite of the "
    "node's own script. Batch 10's diagnostics explain the failure mechanically (that residual "
    "is white), the development result is decisive, and the held-out year is spent on the "
    "configurations whose margin is in question"
)

TIER3 = [
    ("stage1=log1p_transform", "analysis/02_stage1", "target transform", "raw counts",
     "log1p, bias-corrected back-transform",
     "stage 1 is not repaired (human-set, 2026-09-21, reaffirmed at the freeze 2026-09-22); "
     "would also need a verified CRPS on the transformed scale"),
    ("stage1=negative_binomial_family", "analysis/02_stage1", "predictive family", "Gaussian",
     "negative binomial or zero-truncated normal",
     "stage 1 is not repaired (human-set); the most consequential fork not run -- the coverage "
     "deficit is a heavy tail a Gaussian cannot carry"),
    ("stage2=multiplicative", "analysis/04_stage2", "combination rule", "additive",
     "multiplicative on the log scale",
     "undefined where stage 1's mean is near or below zero; needs a design decision"),
    ("stage2=enso_covariate", "analysis/04_stage2", "features", "dataset columns only",
     "add ONI/Nino3.4 at lags 3-6 months",
     "a new data acquisition and a governance decision; human call"),
    ("evaluation=chap_native", "analysis/00_metric", "harness", "native Python CRPS",
     "chap-core evaluation", "decided against in plan §4"),
]

REPORTING_RULE = {
    "written": "before the held-out year was opened; this is what batch 17 reports, whatever it finds",
    "primary": ("main@h__holdout's mean CRPS and 90% coverage against stage 1 alone on the same "
                "cells, from its own conclusion.json. The two-stage ensemble earns its place on "
                "the held-out year if and only if it clears both of plan §2's bars there: lower "
                "mean CRPS than stage 1 alone, and 90% coverage not worse"),
    "secondary": ("stage 1 alone and the two-stage ensemble against persistence and seasonal "
                  "climatology on the same cells (plan §2, §4)"),
    "spread": (f"the distribution of pct_change_vs_stage1 over the tier-2 rows that ran: how many "
               f"beat stage 1 alone, how many with coverage not worse, min/quartiles/median/max, "
               f"the rows more than {SENSITIVITY_POINTS} percentage points from the main path's "
               f"margin (the same threshold as v1 and v2), splits improved, and the province and "
               f"horizon concentration -- reported as a distribution, never as a best row"),
    "pairing": ("every holdout row paired by name with its development v2 row, so the held-out "
                "margin is read beside the development one rather than on its own"),
    "binding": ("nothing is added, dropped, re-tuned or re-run on the holdout after a number from "
                "it has been seen; no configuration is promoted on held-out evidence; a holdout "
                "result that contradicts the development conclusion is the finding and is reported "
                "as such. If the year is ever opened a second time, that is recorded (plan §3)"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config_digest(spec: tuple) -> str:
    """A row's configuration, canonically. What `holdout_freeze_check` compares against, so a
    row cannot keep its name while its meaning moves."""
    if spec[0] == "baseline":
        payload = {"kind": "baseline", "function": spec[1].__name__}
    else:
        payload = {"kind": "two_stage",
                   "stage1": asdict(spec[0]), "scheme": asdict(spec[1]), "stage2": asdict(spec[2])}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def train_month_scale() -> tuple[float, int, int]:
    """Holdout training months over development training months -- the cost scale factor."""
    with DEV_SCHEDULE.open(newline="") as f:
        dev_total = sum(int(r["n_train_months"]) for r in csv.DictReader(f))
    schedule = json.loads(VERIFICATION.read_text())["holdout_schedule"]
    holdout_total = sum(s["n_train_months"] for s in schedule["splits"])
    return holdout_total / dev_total, holdout_total, dev_total


def development_costs() -> dict[str, float]:
    with DEV_RUN_LOG.open(newline="") as f:
        return {r["combination"]: float(r["wall_seconds"]) for r in csv.DictReader(f)}


def development_rows() -> dict[str, dict]:
    with DEV_MANIFEST.open(newline="") as f:
        return {r["combination"]: r for r in csv.DictReader(f)}


def n_cells(spec: tuple, n_provinces: int) -> int:
    """Cell slots a row produces: provinces x splits x horizon."""
    sc = HOLDOUT_SCHEME if spec[0] == "baseline" else spec[1]
    return n_provinces * sc.n_splits * sc.n_periods


def build_rows() -> tuple[list[dict], dict]:
    verification = json.loads(VERIFICATION.read_text())
    if not verification["all_reproductions_identical"]:
        raise RuntimeError("the phase-E machinery has not reproduced the stored development "
                           "results; re-run 06_verify_holdout_runner.py before freezing")
    n_provinces = verification["frozen_province_set"]["n_provinces"]
    combos = holdout_combinations()
    dev_manifest = development_rows()
    dev_cost = development_costs()
    scale, holdout_months, dev_months = train_month_scale()
    baseline_cost = {f"baseline=persistence{SUFFIX}":
                     verification["reproduction_checks"]["baseline_persistence"]["wall_seconds_on_development"],
                     f"baseline=climatology{SUFFIX}":
                     verification["reproduction_checks"]["baseline_climatology"]["wall_seconds_on_development"]}

    def est(name: str, dev_row: str | None) -> float:
        if name in baseline_cost:
            return round(baseline_cost[name] * scale, 1)
        # A row with no development counterpart (a tier-1 sibling) is the main path's
        # pipeline with a different stage-2 configuration, so it carries the main path's cost.
        source = dev_cost.get(dev_row or "", dev_cost["main@h"])
        return round(source * scale, 1)

    rows: list[dict] = []

    # --- tier 0: the reported comparison ---------------------------------------------------
    tier0 = [
        (f"main@h{SUFFIX}", "main@h", f"analysis/04_stage2/{MAIN}", "the pre-registered configuration",
         MAIN, "every parameter at its main-path value",
         "the main path annotated in batch 14 by a rule written before the results were seen, kept "
         "at the freeze (plan §4b, 2026-09-22, human-set). Its conclusion.json carries stage 1 "
         "alone on the same cells, which is plan §2's primary comparison"),
        (f"baseline=persistence{SUFFIX}", None, "analysis/03_baselines/01_persistence",
         "required baseline", "-", "last observed value held flat, sigma from training-window "
         "one-step differences", "plan §2 and §4 require both baselines on both datasets, scored "
         "through the same pipeline"),
        (f"baseline=climatology{SUFFIX}", None, "analysis/03_baselines/02_climatology",
         "required baseline", "-", "mean of the same calendar month in the training window, sigma "
         "its standard deviation", "plan §2 and §4 require both baselines on both datasets"),
    ]
    for combo, dev_row, node, parameter, main_value, value, basis in tier0:
        rows.append({"combination": combo, "tier": 0, "development_row": dev_row or "-", "node": node,
                     "parameter": parameter, "main_value": main_value, "value": value, "basis": basis,
                     "informativeness_rank": 0, "est_cost_s": est(combo, dev_row),
                     "n_expected_cells": n_cells(combos[combo], n_provinces),
                     "config_digest": config_digest(combos[combo]), "status": "planned",
                     "reason_if_not_run": ""})

    # --- tier 1: the not-taken siblings -----------------------------------------------------
    siblings = sorted(p.name for p in STAGE2.iterdir() if p.is_dir() and (p / "claim.md").exists())
    for child in siblings:
        if child == MAIN:
            continue
        combo = f"04_stage2={child}{SUFFIX}"
        if child in TIER1_NOT_RUN:
            rows.append({"combination": combo, "tier": 1, "development_row": f"04_stage2={child}",
                         "node": f"analysis/04_stage2/{child}", "parameter": "stage-2 family / input (a node)",
                         "main_value": MAIN, "value": child,
                         "basis": f"a sibling built and scored in batches 4-9; {TIER1_NOT_RUN[child]}",
                         "informativeness_rank": "-", "est_cost_s": "-", "cumulative_cost_s": "-",
                         "n_expected_cells": "-", "config_digest": "-", "status": "not_run",
                         "reason_if_not_run": TIER1_NOT_RUN_REASON})
            continue
        rows.append({"combination": combo, "tier": 1, "development_row": f"04_stage2={child}",
                     "node": f"analysis/04_stage2/{child}", "parameter": "stage-2 family / input / combination rule (a node)",
                     "main_value": MAIN, "value": child,
                     "basis": "a sibling built and scored in batches 10-14, and expressible as a "
                              "configuration of the verified parametrised pipeline; its own claim.md "
                              "holds the argument",
                     "informativeness_rank": 1, "est_cost_s": est(combo, None),
                     "n_expected_cells": n_cells(combos[combo], n_provinces),
                     "config_digest": config_digest(combos[combo]), "status": "planned",
                     "reason_if_not_run": ""})

    # --- tier 2: the development v2 perturbations, under holdout names ------------------------
    tier2 = []
    for combo in combos:
        if combo.endswith(SUFFIX) and (combo.startswith(("stage1=", "stage2=", "window=", "scheme=",
                                                         "modelable="))):
            dev_row = combo[: -len(SUFFIX)]
            source = dev_manifest.get(dev_row)
            if source is None:
                raise RuntimeError(f"{combo} has no development counterpart {dev_row!r} in the "
                                   f"development manifest; the pairing the report rests on would be broken")
            tier2.append({"combination": combo, "tier": 2, "development_row": dev_row,
                          "node": source["node"], "parameter": source["parameter"],
                          "main_value": source["main_value"], "value": source["value"],
                          "basis": source["basis"],
                          "informativeness_rank": source["informativeness_rank"],
                          "est_cost_s": est(combo, dev_row),
                          "n_expected_cells": n_cells(combos[combo], n_provinces),
                          "config_digest": config_digest(combos[combo]), "status": "planned",
                          "reason_if_not_run": ""})
    tier2.sort(key=lambda r: (int(r["informativeness_rank"]), r["combination"]))

    cumulative, line_index = 0.0, None
    for r in rows:
        if r["status"] != "planned":
            continue
        cumulative += r["est_cost_s"]
        r["cumulative_cost_s"] = round(cumulative, 1)
    for i, r in enumerate(tier2):
        cumulative += r["est_cost_s"]
        r["cumulative_cost_s"] = round(cumulative, 1)
        if cumulative > BUDGET_WALL_SECONDS:
            r["status"] = "below_budget_line"
            r["reason_if_not_run"] = f"cumulative cost exceeds BUDGET_WALL_SECONDS={BUDGET_WALL_SECONDS}"
            if line_index is None:
                line_index = i
    rows.extend(tier2)

    # --- tier 3: not run, with the reason -----------------------------------------------------
    for combo, node, parameter, main_value, value, reason in TIER3:
        rows.append({"combination": f"{combo}{SUFFIX}", "tier": 3, "development_row": combo,
                     "node": node, "parameter": parameter, "main_value": main_value, "value": value,
                     "basis": "carried forward unchanged from the development manifest",
                     "informativeness_rank": "-", "est_cost_s": "-", "cumulative_cost_s": "-",
                     "n_expected_cells": "-", "config_digest": "-", "status": "not_run",
                     "reason_if_not_run": reason})

    # The set and the configurations must close on each other in both directions.
    named = {r["combination"] for r in rows if r["status"] == "planned"}
    missing = sorted(named - set(combos))
    extra = sorted(set(combos) - named)
    if missing or extra:
        raise RuntimeError(f"manifest/configuration disagreement: rows without a configuration "
                           f"{missing}; configurations without a planned row {extra}")

    planned = [r for r in rows if r["status"] == "planned"]
    summary = {
        "phase": "E", "main_path": MAIN, "suffix": SUFFIX,
        "n_rows": len(rows), "n_planned": len(planned),
        "n_tier0": sum(r["tier"] == 0 for r in rows), "n_tier1_planned": sum(r["tier"] == 1 and r["status"] == "planned" for r in rows),
        "n_tier1_not_run": sum(r["tier"] == 1 and r["status"] == "not_run" for r in rows),
        "n_tier2_planned": sum(r["tier"] == 2 and r["status"] == "planned" for r in rows),
        "n_tier2_below_budget_line": sum(r["status"] == "below_budget_line" for r in rows),
        "n_tier3_not_run": sum(r["tier"] == 3 for r in rows),
        "evaluation_design": verification["holdout_schedule"],
        "province_set": verification["frozen_province_set"],
        "cost_model": {"scale_factor": round(scale, 4),
                       "holdout_training_months_total": holdout_months,
                       "development_training_months_total": dev_months,
                       "source": "results/run_log_v2.csv for rows with a development counterpart; "
                                 "the measured development cost in holdout_runner_verification.json "
                                 "for the baselines"},
        "budget_wall_seconds": BUDGET_WALL_SECONDS,
        "planned_cost_s": round(sum(r["est_cost_s"] for r in planned), 1),
        "where_the_line_fell": ("below every planned row: nothing is excluded for budget"
                                if line_index is None else f"after ranked tier-2 row {line_index}"),
        "gate": {"source": "results/holdout_runner_verification.json",
                 "reproduction_checks": {k: v["n_mismatched_values"] for k, v in
                                         verification["reproduction_checks"].items()},
                 "all_identical": True},
        "reporting_rule": REPORTING_RULE,
        "sensitivity_points": SENSITIVITY_POINTS,
    }
    return rows, summary


def write_manifest(rows: list[dict]) -> bytes:
    RESULTS.mkdir(exist_ok=True)
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return MANIFEST.read_bytes()


def render(rows: list[dict]) -> bytes:
    """The bytes the manifest would have, without touching the file."""
    import io
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode()


def verify_only(rows: list[dict]) -> None:
    """The frozen set exists: check it rather than rewrite it."""
    record = json.loads(FREEZE.read_text())
    frozen_sha = digest(MANIFEST)
    recorded = record["frozen_inputs"][f"results/{MANIFEST.name}"]
    with MANIFEST.open(newline="") as f:
        frozen_rows = list(csv.DictReader(f))
    combos = holdout_combinations()
    tree = {p.name for p in STAGE2.iterdir() if p.is_dir() and (p / "claim.md").exists()}

    no_longer_carried, structure_moved = [], []
    for r in frozen_rows:
        if r["tier"] == "1" and r["value"] not in tree:
            no_longer_carried.append(r["combination"])
        if r["config_digest"] == "-":
            continue
        spec = combos.get(r["combination"])
        if spec is None or config_digest(spec) != r["config_digest"]:
            structure_moved.append(r["combination"])
    rebuilt = render(rows)
    check = {
        "checked_on": time.strftime("%Y-%m-%d"),
        "frozen": {"file": f"results/{MANIFEST.name}", "sha256": frozen_sha,
                   "matches_holdout_freeze_json": frozen_sha == recorded,
                   "rows": len(frozen_rows)},
        "replanned_now": {"sha256": hashlib.sha256(rebuilt).hexdigest(),
                          "identical_to_frozen": rebuilt == MANIFEST.read_bytes()},
        "fatal": {"frozen_rows_the_tree_no_longer_carries": no_longer_carried,
                  "frozen_rows_whose_structure_moved": structure_moved},
        "note": "The frozen phase-E set is not rewritten. This file records that it is still the "
                "file that was frozen, that every frozen row still has the configuration it was "
                "frozen with, and that re-planning now would produce the same set.",
    }
    FREEZE_CHECK.write_text(json.dumps(check, indent=2) + "\n")
    print(json.dumps(check, indent=2))
    if frozen_sha != recorded:
        raise RuntimeError("manifest_holdout.csv does not hash to the frozen digest")
    if no_longer_carried or structure_moved:
        raise RuntimeError("frozen rows no longer match the tree or the configuration set")


def main() -> None:
    rows, summary = build_rows()
    if FREEZE.exists() and MANIFEST.exists():
        verify_only(rows)
        return

    manifest_bytes = write_manifest(rows)
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n")
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    freeze = {
        "frozen_file": f"results/{MANIFEST.name}", "phase": "E", "main_path": MAIN,
        "rows": len(rows), "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "frozen_at_commit": head, "frozen_on": time.strftime("%Y-%m-%d"),
        "frozen_inputs": {
            f"results/{MANIFEST.name}": hashlib.sha256(manifest_bytes).hexdigest(),
            "results/manifest.csv": digest(DEV_MANIFEST),
            "results/conclusions_v2.csv": digest(DEV_CONCLUSIONS),
            "results/distribution_v2.json": digest(DEV_DISTRIBUTION),
            "results/holdout_runner_verification.json": digest(VERIFICATION),
            "analysis/01_data/01_prepare/results/development.csv": digest(PREPARE / "development.csv"),
            "analysis/01_data/01_prepare/results/holdout.csv": digest(PREPARE / "holdout.csv"),
        },
        "note": ("The set the held-out year is evaluated across, fixed before it was opened. "
                 "frozen_at_commit is HEAD at the moment of freezing, so it precedes the commit "
                 "that adds this file; no holdout result exists at it, which is what "
                 "/validate invariants' freeze check asserts. The holdout file's own digest is "
                 "recorded so that the file phase E opens is the file that was sealed -- its "
                 "case values are not read here. Changing this set is not an edit: it is a "
                 "recorded decision in the plan's §4b, made before the year is opened."),
        "reporting_rule": REPORTING_RULE,
    }
    FREEZE.write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("evaluation_design", "province_set", "reporting_rule")}, indent=2))
    print(json.dumps({k: v for k, v in freeze.items() if k != "reporting_rule"}, indent=2))


if __name__ == "__main__":
    main()
