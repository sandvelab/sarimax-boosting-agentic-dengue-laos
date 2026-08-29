"""Enumerate the analyses that would have been just as reasonable, and cost them.

`/perturb plan`. The manifest this writes is the list of combinations phase D runs, and it
is written **before** any of them runs, because a perturbation set assembled after the
numbers are in is a selection wearing a stability analysis's clothes.

## What is in it

**Tier 1 — one fork at a time.** The main path, plus every child of every fork that the
main path does not take, with every other fork left where it is. This is the tier that
answers the question the plan calls the most valuable single output of the project: does
the conclusion move when this choice is taken instead?

**Tier 2 — pairs, chosen by a rule and not by looking.** Eight combinations, selected from
tier 1's own results by the rule in `TIER2_RULE`, which is written to
`results/tier2_rule.md` and hashed into `results/manifest_notes.json` by this batch, before
tier 1 has run. When tier 1 exists, running this script again fills the eight slots in;
`--freeze-check` refuses to do it if the rule's text has changed since the hash was
recorded, so the pairs cannot be chosen after the event by editing the rule that chooses
them.

## Where every number comes from

Nothing here is typed. The forks come from the tree (`lib/inventory.py`), the model costs
from each model's own `run_cost.json`, the pipeline's own costs from `step_costs.json`,
and the informativeness prior from the phase-C fork sweeps -- and only from a sweep whose
recorded base configuration still matches the family's current one, so a table taken
around a main path that has since moved cannot order this one.

The prior orders the rows and selects nothing: with the whole manifest inside budget, the
order decides what runs first, not what runs. If a later batch does cut, the cut falls at
the end of this order and `manifest_notes.json` says where.

Writes, at this node:
  results/forks.csv           the inventory: one row per fork
  results/manifest.csv        one row per combination
  results/manifest_notes.json the totals, the budget, the cut order, what is not costed
  results/tier2_rule.md       the pair-selection rule, fixed before tier 1 runs
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import inventory as inv  # noqa: E402

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
SWEEPS = ROOT / "AI-generated/candidate-forks"

# Splits in the two backtests, fixed in batch 3 and not moved again. The holdout column is
# the development column with the model terms rescaled by the ratio.
DEV_SPLITS, HOLDOUT_SPLITS = 8, 4

# The budget, in wall-clock hours for the whole manifest run twice -- once on development,
# once on the held-out year. Set here rather than measured: it is a resource decision, and
# the figure is roughly one unattended overnight run on the machine this project runs on.
# Recorded as agent-autonomous and raised with the human in the batch report.
BUDGET_HOURS = 12.0

TIER2_RULE = """\
# Tier 2 — how the eight pairs are selected

Fixed in batch 12, **before any tier-1 combination had been run**, and applied by
`plan_manifest.py` from `conclusions.csv` rather than by anyone reading it. Choosing which
pairs to explore after seeing tier 1's numbers is selection with extra steps, which is the
objection this plan makes to an unfrozen holdout manifest, applied one level down.

1. Rank every tier-1 row that has a conclusion by `|skill_score − skill_score(main)|`,
   largest first, read from `results/conclusions.csv`.
2. **Group S** — the two highest-ranked rows whose fork kind is `setup`.
3. **Group M** — the two highest-ranked rows whose fork kind is `candidate`, `family` or
   `baseline`: the three kinds that move our model and leave the dataset alone.
4. **Group A** — the one highest-ranked row whose fork kind is `scoring`.
5. Tier 2 is every pair drawn from **two different groups**: S×M gives four, S×A two,
   M×A two. Eight combinations.
6. No pair is ever formed from two children of the same fork. The three groups are
   disjoint by fork kind and no fork has two kinds, so this holds by construction rather
   than by a check.
7. If a group has fewer rows than it asks for, it contributes what it has and the
   shortfall is recorded in `manifest_notes.json`. The rule is not adjusted to reach eight.

Ties in step 1 are broken by combination name, ascending, so the rule is deterministic.
"""


def read_json(path: Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def model_costs() -> dict[tuple[str, str], dict]:
    """Every measured backtest cost in the tree, keyed by (combination, model)."""
    out = {}
    for path in sorted((ROOT / "analysis/03_models").rglob("results/*/run_cost.json")):
        cost = json.loads(path.read_text())
        out[(path.parent.name, cost["model"])] = cost
    return out


def sweep_priors() -> tuple[dict[str, float], list[dict]]:
    """|Δ mean CRPS| per combination, from the phase-C sweeps that are still current.

    A sweep is current when the base configuration it was taken around is still the one
    the family assembles. `candidate_fork_sweep.py` refuses to re-tabulate a stale sweep
    for the same reason, and the same test is applied here rather than trusting the
    directory name.
    """
    priors, used = {}, []
    for summary_path in sorted(SWEEPS.glob("*/fork_sweep.json")):
        summary = json.loads(summary_path.read_text())
        family = ROOT / summary["swept"]
        recorded = summary.get("base_configuration_sha256")
        current = None
        spec = family / "results" / summary["base_combination"] / "candidate_spec.json"
        if spec.exists():
            current = json.loads(spec.read_text())["configuration_sha256"]
        stale = bool(recorded) and recorded != current
        base = summary["main_path_mean_crps"]
        rows = list(csv.DictReader((summary_path.parent / "fork_leaderboard.csv").open()))
        contributed = 0
        for row in rows:
            if row["fork"] == "-":
                continue
            if not stale:
                priors[row["combo"]] = abs(float(row["mean_crps"]) - base)
                contributed += 1
        used.append({"sweep": summary_path.parent.name, "swept": summary["swept"],
                     "base_combination": summary["base_combination"],
                     "still_current": not stale, "rows_contributed": contributed})

    # The family fork's own children, from the across-family table rather than a sweep.
    board = SWEEPS / "families/family_leaderboard.csv"
    if board.exists():
        rows = list(csv.DictReader(board.open()))
        main_row = next((r for r in rows if r["on_the_main_path"] == "True"), None)
        if main_row:
            for row in rows:
                if row["on_the_main_path"] != "True":
                    priors[row["combination"]] = abs(
                        float(row["mean_crps"]) - float(main_row["mean_crps"]))
            used.append({"sweep": "families", "swept": "03_models/03_candidate",
                         "base_combination": main_row["combination"],
                         "still_current": True, "rows_contributed": len(rows) - 1})
    return priors, used


# Which models a combination re-runs, by the kind of fork it moves. `our` is filled in
# from the tree: the model the main path reports.
def plan_row(fork: inv.Fork, child: str, our: str, baselines: list[str],
             reference: str) -> dict:
    combo = fork.combination(child)
    every = [*baselines, reference, our]
    if fork.kind == "setup":
        rerun, inherited = every, []
    elif fork.kind == "scoring":
        rerun, inherited = [], every
    elif fork.kind == "baseline":
        # The pool takes both required baselines as members, so a fork on how one of them
        # is constructed moves our reported model too. Batch 5 costed this fork as moving
        # one leaderboard row; batch 11's promotion is what changed that.
        moved = fork.stage
        rerun = [moved, our]
        inherited = [m for m in every if m not in rerun]
    else:  # family, candidate
        rerun = [our]
        inherited = [m for m in every if m != our]
    return {"combination": combo, "kind": fork.kind, "fork": fork.rel, "child": child,
            "models_rerun": rerun, "models_inherited": inherited}


def cost_of(row: dict, costs: dict, steps: dict, our: str, our_family: str,
            fork_owner: str, family_combo: dict[str, str]) -> tuple[float, str]:
    """Estimated development seconds for one combination, and what the estimate rests on.

    The model terms are measured backtests. Where a combination has its own measurement
    for a model, that one is used; otherwise the model's cost at its own main path stands
    in. The one adjustment: a fork inside a *member* of the pool changes what the pool
    costs, by roughly what it changes that member's standalone backtest by, and both of
    those are measured numbers.
    """
    basis = []
    seconds = steps["04_score"] + steps["conclude"]
    if row["kind"] in ("setup", "cold"):
        seconds += steps["02_setup"]
    if not row["models_rerun"]:
        basis.append("re-aggregation only; no model is re-run")
    combo = row["combination"]
    for model in row["models_rerun"]:
        here = costs.get((combo, model))
        if here:
            seconds += here["wall_clock_seconds"]
            basis.append(f"{model}=measured under {combo}")
            continue
        at_main = costs.get(("main", model)) or costs.get((f"family_{model}", model))
        if not at_main:
            basis.append(f"{model}=no measurement")
            continue
        seconds += at_main["wall_clock_seconds"]
        basis.append(f"{model}=measured under {at_main['combo']}")
        # A moved fork inside a member family: add what it does to that member alone.
        if model == our and fork_owner not in ("-", our_family):
            member = next((m for (c, m) in costs if c == combo and m != our), None)
            member_base = None
            if member:
                for candidate_combo in (family_combo.get(fork_owner, ""), "main"):
                    if (candidate_combo, member) in costs:
                        member_base = costs[(candidate_combo, member)]
                        break
            if member and member_base:
                delta = (costs[(combo, member)]["wall_clock_seconds"]
                         - member_base["wall_clock_seconds"])
                seconds += delta
                basis.append(f"{member} member delta {delta:+.1f}s vs "
                             f"{member_base['combo']}")
    return round(seconds, 1), "; ".join(basis)


def directory_bytes(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def footprints() -> dict[str, int]:
    """What one combination costs in stored bytes, part by part, measured on disk.

    The same shape as the cost model: a combination's storage is the sum of the parts it
    writes, and each part's size is read from a combination that already wrote it. Where
    a part exists under several combinations the largest is taken, because a projection
    that used the smallest would be an estimate designed to look affordable.
    """
    parts: dict[str, int] = {}
    places = {
        "02_setup": ROOT / "analysis/02_setup",
        "04_score": ROOT / "analysis/04_score",
        "persistence": ROOT / "analysis/03_models/01_baselines/01_persistence",
        "climatology": ROOT / "analysis/03_models/01_baselines/02_climatology",
        "reference": ROOT / "analysis/03_models/02_reference",
    }
    family_root = ROOT / "analysis/03_models/03_candidate"
    for path in family_root.iterdir():
        if path.is_dir() and (path / "claim.md").exists():
            places[path.name] = path
    for name, place in places.items():
        sizes = [directory_bytes(d) for d in place.glob("**/results/*") if d.is_dir()]
        parts[name] = max(sizes) if sizes else 0
    return parts


def storage_of(row: dict, parts: dict[str, int], our_family: str,
               family_of: dict[str, str]) -> int:
    """Projected stored bytes for one combination."""
    total = parts["04_score"]
    if row["kind"] == "setup":
        total += parts["02_setup"]
    for model in row["models_rerun"]:
        total += parts.get(family_of.get(model, model), 0)
    return total


def holdout_seconds(row: dict, dev: float, steps: dict) -> float:
    """The same combination at four splits instead of eight.

    Only the model terms scale: every model's own `run_cost.json` records a
    `seconds_per_split`, which is what asserts that they do. The pipeline steps are work
    on files whose size the split count barely moves, so they are carried across unscaled.

    **The main path is the one row whose two columns are not the same analysis.** On
    development it is already computed and the driver only recomputes its conclusion; on
    the held-out year nothing has ever run, so the main path there is a cold start --
    the setup chain, all four models, the scoring chain. Costing it at 0.3 s in both
    columns would understate the holdout run by the most expensive row it has.
    """
    fixed = steps["04_score"] + steps["conclude"] + (
        steps["02_setup"] if row["kind"] in ("setup", "main") else 0.0)
    return round(fixed + (dev - fixed) * HOLDOUT_SPLITS / DEV_SPLITS, 1)


def main() -> None:
    out = NODE / "results"
    out.mkdir(parents=True, exist_ok=True)
    steps = read_json(out / "step_costs.json")
    if not steps:
        raise SystemExit("run measure_step_costs.py first: the manifest's cost column is "
                         "measured, not asserted.")
    steps = steps["seconds"]

    forks = inv.forks()
    inv.assert_unique_names(forks)
    costs = model_costs()
    priors, sweeps_used = sweep_priors()

    family_fork = next(f for f in forks if f.kind == "family")
    our_family = family_fork.main
    # Each model family's own combination -- the one its main path was measured under.
    family_combo = {c: family_fork.combination(c) for c in family_fork.children}
    our = json.loads(
        sorted((family_fork.node / our_family).glob("results/main/model_spec.json"))[0]
        .read_text())["model"] if sorted(
        (family_fork.node / our_family).glob("results/main/model_spec.json")) else None
    if not our:
        raise SystemExit(f"the main path {our_family} has not run under `main`; the "
                         f"manifest cannot say which model a combination re-runs")
    board = inv.leaderboard_models()
    reference = "reference"
    baselines = [f.stage for f in forks if f.kind == "baseline"]

    # ---- the fork inventory -------------------------------------------------------
    reach = {"setup": len([m for m in board if not m.startswith("reference_r")]),
             "scoring": len([m for m in board if not m.startswith("reference_r")]),
             "baseline": 2, "family": 1, "candidate": 1}
    with (out / "forks.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, lineterminator="\n", fieldnames=[
            "fork", "stage", "kind", "owner", "main_child", "n_children",
            "siblings", "siblings_built", "reach_rows"])
        writer.writeheader()
        for fork in forks:
            writer.writerow({
                "fork": fork.rel, "stage": fork.stage, "kind": fork.kind,
                "owner": fork.owner, "main_child": fork.main,
                "n_children": len(fork.children),
                "siblings": ";".join(fork.siblings),
                "siblings_built": ";".join(str(fork.built[c]) for c in fork.siblings),
                "reach_rows": reach[fork.kind]})

    # ---- tier 0: combinations that exist and are not perturbations ----------------
    # A fork's *main* child can also have been run under a combination of its own --
    # `family_ensemble` is the reported model run under its own name so that the three
    # families could be compared each at its own main path. It is the same analysis as
    # `main` and perturbs nothing, so it is not a tier-1 row; but it is a combination in
    # the tree, and the manifest is the register of those. Found on disk, not listed.
    held = []
    for fork in forks:
        name = fork.combination(fork.main)
        if any((ROOT / "analysis").glob(f"**/results/{name}")):
            held.append({"combination": name, "kind": "held", "fork": fork.rel,
                         "child": fork.main, "owner": fork.owner, "combo_base": "main",
                         "built": True, "models_rerun": [], "models_inherited": [],
                         "tier": 0, "reach_rows": 0, "prior_abs_delta_crps": None,
                         "est_seconds_dev": "", "est_seconds_holdout": "",
                         "cost_basis": "not a perturbation; nothing to cost",
                         "status": ("the main path's own choice, run under its own name; "
                                    "the same analysis as `main`")})

    # ---- tier 1 -------------------------------------------------------------------
    rows = [{"combination": "main", "kind": "main", "fork": "-", "child": "-",
             "models_rerun": [], "models_inherited": [],
             "combo_base": "-", "built": True}]
    for fork in forks:
        for child in fork.siblings:
            row = plan_row(fork, child, our, baselines, reference)
            row["combo_base"] = "main"
            row["built"] = fork.built[child]
            row["owner"] = fork.owner
            rows.append(row)

    for row in rows:
        row.setdefault("owner", "-")
        if row["combination"] == "main":
            row["est_seconds_dev"] = round(steps["conclude"], 1)
            row["cost_basis"] = ("development: conclude.py only, because the main path is "
                                 "the analysis that has already run. Holdout: a cold "
                                 "start, every model")
            cold = {**row, "kind": "setup",
                    "models_rerun": [*baselines, reference, our]}
            row["est_seconds_holdout"] = holdout_seconds(
                cold, cost_of(cold, costs, steps, our, our_family, "-", family_combo)[0],
                {**steps, "02_setup": steps["02_setup"]})
        else:
            row["est_seconds_dev"], row["cost_basis"] = cost_of(
                row, costs, steps, our, our_family, row["owner"], family_combo)
            row["est_seconds_holdout"] = holdout_seconds(
                row, row["est_seconds_dev"], steps)
        row["reach_rows"] = reach.get(row["kind"], 0)
        row["prior_abs_delta_crps"] = priors.get(row["combination"])
        row["tier"] = 1
        row["status"] = "planned"

    # Rank: reach first, then what phase C measured the fork to be worth where it
    # measured anything, then cheapest first. Order of execution, not of inclusion.
    body = [r for r in rows if r["combination"] != "main"]
    body.sort(key=lambda r: (-r["reach_rows"], -(r["prior_abs_delta_crps"] or 0.0),
                             r["est_seconds_dev"], r["combination"]))
    ordered = [rows[0], *body]

    # ---- tier 2 -------------------------------------------------------------------
    (out / "tier2_rule.md").write_text(TIER2_RULE)
    rule_sha = hashlib.sha256(TIER2_RULE.encode()).hexdigest()
    conclusions = out / "conclusions.csv"
    tier2, shortfall = [], {}
    if conclusions.exists():
        tier2, shortfall = select_tier2(
            conclusions, {r["combination"]: r for r in ordered}, attempted_rows(out))
    if not tier2:
        tier2 = [{"combination": "", "kind": "pair", "fork": "-", "child": "-",
                  "combo_base": "main", "built": False, "owner": "-",
                  "models_rerun": [], "models_inherited": [],
                  "est_seconds_dev": "", "est_seconds_holdout": "",
                  "cost_basis": "unresolved until tier 1 has conclusions",
                  "reach_rows": "", "prior_abs_delta_crps": None, "tier": 2,
                  "status": f"pending-selection (slot {i + 1} of 8, by tier2_rule.md)"}
                 for i in range(8)]

    # ---- write --------------------------------------------------------------------
    # Which batch owns each row. Recorded in the manifest rather than in a batch report,
    # so that a row nobody has run says who was supposed to run it.
    assigned = {"setup": 13, "scoring": 13, "baseline": 22, "family": 14,
                "candidate": 14, "main": 12, "pair": 15, "held": "-"}
    fields = ["rank", "tier", "combination", "kind", "fork", "child", "owner",
              "combo_base", "models_rerun", "models_inherited", "reach_rows", "built",
              "prior_abs_delta_crps", "est_seconds_dev", "est_seconds_holdout",
              "projected_bytes", "cost_basis", "assigned_batch", "status"]
    with (out / "manifest.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n",
                                extrasaction="ignore")
        writer.writeheader()
        for rank, row in enumerate([*ordered, *tier2, *held], start=1):
            writer.writerow({
                **row, "rank": rank,
                "assigned_batch": assigned[row["kind"]],
                "models_rerun": ";".join(row["models_rerun"]),
                "models_inherited": ";".join(row["models_inherited"])})

    parts = footprints()
    # Which directory holds each model's results: a baseline's node is named for it, ours
    # is the family that produces it.
    family_of = {our: our_family}
    for child in family_fork.children:
        spec = sorted((family_fork.node / child).glob("results/*/model_spec.json"))
        if spec:
            family_of[json.loads(spec[0].read_text())["model"]] = child
    for row in ordered:
        row["projected_bytes"] = storage_of(row, parts, our_family, family_of)

    dev = sum(r["est_seconds_dev"] for r in ordered)
    hold = sum(r["est_seconds_holdout"] for r in ordered)
    unbuilt = [r["combination"] for r in ordered if not r["built"]]
    stale = stale_directories(ordered, our, baselines, family_fork)

    (out / "manifest_notes.json").write_text(json.dumps({
        "our_reported_model": our,
        "our_reported_family": our_family,
        "leaderboard_models": board,
        "n_forks": len(forks),
        "n_forks_by_kind": {k: sum(1 for f in forks if f.kind == k)
                            for k in sorted({f.kind for f in forks})},
        "n_tier1": len(ordered),
        "n_tier2": len(tier2),
        "n_tier0_held": len(held),
        "tier0_held": [r["combination"] for r in held],
        "n_combinations": len(ordered) + len(tier2) + len(held),
        "tier2_rule_file": "results/tier2_rule.md",
        "tier2_rule_sha256": rule_sha,
        "tier2_group_shortfall": shortfall,
        "estimated_seconds": {
            "tier1_development": round(dev, 1),
            "tier1_holdout": round(hold, 1),
            "tier2_development": "unresolved until tier 1 has conclusions",
        },
        "estimated_hours_tier1_both_datasets": round((dev + hold) / 3600, 2),
        "storage": {
            "measured_parts_mb": {k: round(v / 1e6, 1) for k, v in sorted(parts.items())},
            "projected_tier1_development_mb": round(
                sum(r["projected_bytes"] for r in ordered) / 1e6, 1),
            "projected_tier1_both_datasets_mb": round(
                2 * sum(r["projected_bytes"] for r in ordered) / 1e6, 1),
            "on_disk_now_results_mb": round(sum(
                directory_bytes(d) for d in (ROOT / "analysis").glob("**/results")
                if d.is_dir() and "work" not in d.parts) / 1e6, 1),
            "method": ("each row's parts summed from the largest measured example of "
                       "that part on disk; the holdout run is assumed the same size, "
                       "which slightly overstates it at four splits rather than eight"),
            "what_dominates": ("chap eval's NetCDF: one eval.nc is about 9.4 MB and the "
                               "per-cell CSV derived from it is about 0.18 MB, so the "
                               "prune target is unambiguous and is annotated at "
                               "03_models rather than here"),
        },
        "budget_hours_both_datasets": BUDGET_HOURS,
        "budget_source": ("set in batch 12, agent-autonomous: roughly one unattended "
                          "overnight run on the machine this project runs on. Compute has "
                          "never been what binds this project; implementation effort is."),
        "cut_order_if_the_budget_binds": [
            "tier 2, from the bottom of the rank order upward -- pairs are the least "
            "informative rows per second and the manifest is designed so they go first",
            "the reference's four repeats on tier-2 setup rows, reduced to two -- this "
            "doubles the noise on those rows' denominators and is recorded as such",
            "tier-1 rows below the rank line, in rank order, never by kind",
        ],
        "not_costed": {
            "02_setup on non-setup rows": ("not run there, so not charged"),
            "building the children that do not exist yet": (
                f"{len(unbuilt)} of the tier-1 rows have no scripts. Writing them is "
                f"implementation effort, which this manifest does not cost, and it is "
                f"what batches 13 and 22 are for."),
            "the external population series b_backCast needs": (
                "an annual Lao population series is an input the repository does not "
                "hold. Acquiring and archiving it is a batch-13 dependency, not a "
                "compute cost."),
        },
        "unbuilt_children": unbuilt,
        "results_on_disk_that_this_manifest_row_would_replace": stale,
        "measured_from": {
            "model backtests": "analysis/03_models/**/results/*/run_cost.json",
            "pipeline steps": "analysis/05_stability/results/step_costs.json",
            "informativeness prior": "AI-generated/candidate-forks/*/fork_leaderboard.csv",
        },
        "sweeps_consulted": sweeps_used,
        "splits": {"development": DEV_SPLITS, "holdout": HOLDOUT_SPLITS},
    }, indent=1, sort_keys=True) + "\n")

    print(f"{len(forks)} forks -> {len(ordered)} tier-1 rows + {len(tier2)} tier-2 slots")
    print(f"tier 1: {dev / 60:.0f} min development + {hold / 60:.0f} min holdout "
          f"= {(dev + hold) / 3600:.2f} h against a {BUDGET_HOURS:.0f} h budget")
    print(f"{len(unbuilt)} children have no scripts yet: {', '.join(unbuilt)}")
    print(f"-> {(out / 'manifest.csv').relative_to(ROOT)}")


def stale_directories(rows: list[dict], our: str, baselines: list[str],
                      family_fork: inv.Fork) -> dict[str, dict]:
    """Manifest rows whose results directory already holds a *different* analysis.

    Twelve of the tier-1 rows were run during phase C, when the main path through
    `03_models/03_candidate` was a single family rather than the pool. The combination
    names are the same and the analyses are not: `observation_negBinomial` then meant
    "our model is candidate 1 with a plain negative binomial", and now means "our model
    is the pool, whose candidate-1 member has a plain negative binomial".

    Which is which is not guessed from the name. `04_score/01_collect` writes a
    `models.csv` naming every model it scored, so the test is whether the models of ours
    that a directory already holds are the ones its manifest row would produce.
    """
    out: dict[str, dict] = {}
    collect = ROOT / "analysis/04_score/01_collect/results"
    for row in rows:
        board = collect / row["combination"] / "models.csv"
        if not board.exists():
            continue
        present = {r["model"] for r in csv.DictReader(board.open())
                   if r["origin"] == "ours" and r["model"] not in baselines}
        expected = {our}
        if row["kind"] == "family":
            spec = sorted((family_fork.node / row["child"]).glob(
                f"results/{row['combination']}/model_spec.json"))
            expected = ({json.loads(spec[0].read_text())["model"]} if spec else set())
        if present != expected:
            out[row["combination"]] = {
                "holds": sorted(present), "the manifest row produces": sorted(expected),
                "produced_by": "phase C, around a main path that has since moved"}
    return out


def attempted_rows(out: Path) -> set[str]:
    """The combinations the driver has actually tried, from its own run record.

    `run_status.csv` is written by `run_manifest.py` and is the only file that
    distinguishes "ran and concluded nothing" from "nobody has run it yet". Read here
    rather than inferred from what is on disk, because a directory left by an earlier
    phase is not evidence that this manifest's row was run.
    """
    path = out / "run_status.csv"
    if not path.exists():
        return set()
    return {r["combination"] for r in csv.DictReader(path.open())
            if r["status"] == "ran" or r["status"].startswith("failed")}


def select_tier2(conclusions: Path, tier1: dict,
                 attempted: set[str]) -> tuple[list[dict], dict]:
    """Apply `tier2_rule.md` to tier 1's conclusions. Nothing here is a judgment call."""
    rows = list(csv.DictReader(conclusions.open()))
    have = {r["combination"]: float(r["skill_score"]) for r in rows
            if r.get("skill_score") not in (None, "")}
    if "main" not in have:
        return [], {"reason": "no conclusion for the main path"}

    # The rule ranks "every tier-1 row that has a conclusion", and step 7 lets a group
    # contribute fewer rows than it asks for. Both are written for a tier 1 that has
    # *run* and come out wrong for one that is part-way through: after batch 13 the
    # setup and scoring rows have conclusions and no row that moves our model does, so
    # the rule would fill group A and half of group S, select two pairs instead of
    # eight, and record a shortfall that is an artefact of the running order. Batch 15
    # would then re-run it and get a different tier 2, with nothing in the record to
    # say which was the frozen one.
    #
    # So the rule is applied once, when every tier-1 row has been attempted. This does
    # not change `tier2_rule.md` -- its text and its sha256 are what batch 12 fixed --
    # it fixes *when* a rule about the ranking of tier 1 is allowed to read a tier 1.
    # A row that ran and produced no conclusion still counts as attempted, which is the
    # case step 7 is for.
    waiting = sorted(c for c in tier1 if c != "main" and c not in attempted)
    if waiting:
        return [], {"reason": "tier 1 has not been run through: no attempt recorded for "
                              + ", ".join(waiting)}
    ranked = sorted(
        (c for c in have if c != "main" and c in tier1),
        key=lambda c: (-abs(have[c] - have["main"]), c))
    groups = {
        "S": [c for c in ranked if tier1[c]["kind"] == "setup"][:2],
        "M": [c for c in ranked if tier1[c]["kind"] in ("candidate", "family",
                                                        "baseline")][:2],
        "A": [c for c in ranked if tier1[c]["kind"] == "scoring"][:1],
    }
    shortfall = {k: n - len(groups[k]) for k, n in (("S", 2), ("M", 2), ("A", 1))
                 if len(groups[k]) < n}
    pairs = [(a, b) for x, y in (("S", "M"), ("S", "A"), ("M", "A"))
             for a in groups[x] for b in groups[y]]
    out = []
    for a, b in pairs:
        out.append({
            "combination": f"{a}__{b}", "kind": "pair",
            "fork": f"{tier1[a]['fork']}+{tier1[b]['fork']}",
            "child": f"{tier1[a]['child']}+{tier1[b]['child']}",
            "owner": "-", "combo_base": "main",
            "built": tier1[a]["built"] and tier1[b]["built"],
            "models_rerun": sorted(set(tier1[a]["models_rerun"])
                                   | set(tier1[b]["models_rerun"])),
            "models_inherited": sorted(set(tier1[a]["models_inherited"])
                                       & set(tier1[b]["models_inherited"])),
            "reach_rows": max(tier1[a]["reach_rows"], tier1[b]["reach_rows"]),
            "prior_abs_delta_crps": None, "tier": 2,
            "est_seconds_dev": max(tier1[a]["est_seconds_dev"],
                                   tier1[b]["est_seconds_dev"]),
            "est_seconds_holdout": max(tier1[a]["est_seconds_holdout"],
                                       tier1[b]["est_seconds_holdout"]),
            "cost_basis": f"the more expensive of {a} and {b}",
            "status": "selected by tier2_rule.md",
        })
    return out, shortfall


if __name__ == "__main__":
    main()
