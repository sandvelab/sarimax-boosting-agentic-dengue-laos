"""Why the clean-room run of batch 25 could not finish: the development manifest is
re-derived at run time from numbers the unseeded reference model moves.

`cleanroom_compare.py` says *what* differs between a clean-room run and the archive. This
says *why the run stopped*, which is a different question and needed its own file because
AGENTS.md §1 does not allow the answer to be read out of a terminal and carried into a
report by hand.

Three things are established here, each from files both runs wrote:

  models      whether every model this project wrote returned the same CRPS, per
              combination and per model, with the unseeded reference separated out
  tier2       whether the tier-2 selection rule, applied to each run's own tier-1
              conclusions, selects the same eight pairs -- and by what margin the
              comparisons that flipped were decided
  band        what the reference's four repeats did to the noise band that the phase-D
              headline ("N of 17 forks move the conclusion further than the reference
              moves on its own") is measured against

The tier-2 ranking is recomputed here rather than imported: `select_tier2` lives in
`analysis/05_stability/scripts/plan_manifest.py`, which runs under the pinned analysis
environment, and this is repository machinery running under .venv. A reimplementation can
drift from the original silently, so it is checked rather than trusted --
`tier2.reimplementation_reproduces_the_archived_selection` must be true, and it is false
if this file's idea of the rule has stopped matching the manifest the project actually
carries. Read the rest of the tier2 block only if it is true.

Usage:
  .venv/bin/python AI-internal/useful-scripts/cleanroom_tier2_drift.py \
      --archive . --cleanroom <clean-room>/repo --out <file>.json
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

# Mirrors `select_tier2` in analysis/05_stability/scripts/plan_manifest.py: rank every
# tier-1 row that has a conclusion by how far its skill score sits from the main path's,
# furthest first, ties broken by name; then take the top two `setup` rows, the top two
# model rows and the top `scoring` row, and pair the groups.
GROUPS = {"S": (("setup",), 2), "M": (("candidate", "family", "baseline"), 2),
          "A": (("scoring",), 1)}
PAIRINGS = (("S", "M"), ("S", "A"), ("M", "A"))


def read_conclusions(root: Path) -> dict[str, float]:
    p = root / "analysis/05_stability/results/conclusions.csv"
    return {r["combination"]: float(r["skill_score"])
            for r in csv.DictReader(p.open())
            if r.get("skill_score") not in (None, "")}


def read_manifest(root: Path, name: str = "manifest.csv") -> list[dict]:
    return list(csv.DictReader((root / "analysis/05_stability/results" / name).open()))


def rank_and_select(skill: dict[str, float], kind: dict[str, str],
                    tier1: set[str]) -> dict:
    """Apply the rule to one run's conclusions and report the margins it decided on."""
    main = skill["main"]
    ranked = sorted((c for c in skill if c != "main" and c in tier1),
                    key=lambda c: (-abs(skill[c] - main), c))
    order = [{"combination": c, "kind": kind[c], "skill_score": skill[c],
              "abs_delta_from_main": abs(skill[c] - main)} for c in ranked]
    groups, margins = {}, {}
    for g, (kinds, n) in GROUPS.items():
        eligible = [c for c in ranked if kind[c] in kinds]
        groups[g] = eligible[:n]
        # The margin that decided the group: how far the last row admitted sits above the
        # first row excluded. A margin far below the reference's own noise is a coin toss.
        if len(eligible) > n:
            last_in, first_out = eligible[n - 1], eligible[n]
            margins[g] = {
                "last_admitted": last_in, "first_excluded": first_out,
                "margin_in_abs_delta_skill":
                    abs(skill[last_in] - main) - abs(skill[first_out] - main)}
    pairs = [f"{a}__{b}" for x, y in PAIRINGS
             for a in groups[x] for b in groups[y]]
    return {"ranking": order, "groups": groups,
            "deciding_margins": margins, "pairs": sorted(pairs)}


def models_block(archive: Path, cleanroom: Path) -> dict:
    """Per combination and per model, did the CRPS come back identical?"""
    ours, reference, missing = {}, {}, []
    for p in sorted((cleanroom / "analysis/results").glob("*/conclusion.json")):
        combo = p.parent.name
        if combo.endswith("__holdout"):
            continue
        a = archive / "analysis/results" / combo / "conclusion.json"
        if not a.exists():
            missing.append(combo)
            continue
        A, B = json.loads(a.read_text()), json.loads(p.read_text())
        for model, vb in sorted(B.get("crps_by_model", {}).items()):
            va = A.get("crps_by_model", {}).get(model)
            if va is None:
                continue
            bucket = reference if model.startswith("reference") else ours
            bucket.setdefault(model, {"identical": [], "moved": {}})
            if va == vb:
                bucket[model]["identical"].append(combo)
            else:
                bucket[model]["moved"][combo] = {"archived": va, "cleanroom": vb,
                                                 "delta": vb - va}
    def summarise(b):
        return {m: {"combinations_identical": len(v["identical"]),
                    "combinations_moved": len(v["moved"]),
                    "moved": v["moved"]} for m, v in sorted(b.items())}
    return {
        "our_models": summarise(ours),
        "the_unseeded_reference": summarise(reference),
        "combinations_only_the_cleanroom_has": sorted(missing),
        "note": "Our models are seeded and are expected to be identical. The reference "
                "model is an external container with no seed; it is the only thing in "
                "the analysis that cannot reproduce, and every number that moves "
                "downstream moves because of it.",
    }


def band_block(archive: Path, cleanroom: Path) -> dict:
    def load(root):
        d = json.loads((root / "analysis/05_stability/results/distribution.json").read_text())
        b, s = d["reference_noise_band"], d["sensitivity"]
        return {
            "skill_band": b["skill_band"],
            "crps_floor": b["crps_floor"],
            "skill_against_each_repeat": b["skill_against_each_repeat"],
            "forks_above_the_band": [f["fork"] for f in s["moving_more_than_the_reference_noise_band"]],
            "n_forks_above_the_band": len(s["moving_more_than_the_reference_noise_band"]),
            "n_forks": s["forks"],
            "n_analyses": d["skill_score"]["n"],
            "main_path_skill": d["skill_score"]["main_path"],
        }
    A, B = load(archive), load(cleanroom)
    crossed = sorted(set(A["forks_above_the_band"]) - set(B["forks_above_the_band"]))
    return {
        "archived": A, "cleanroom": B,
        "skill_band_ratio": B["skill_band"] / A["skill_band"] if A["skill_band"] else None,
        "forks_that_fell_below_the_band": crossed,
        "note": "The band is the range of our model's skill against the reference's four "
                "unseeded repeats -- a max minus a min over four draws. The forks listed "
                "as having fallen below it did not move; the band did.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True, type=Path)
    ap.add_argument("--cleanroom", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    archive, cleanroom = a.archive.resolve(), a.cleanroom.resolve()

    man = read_manifest(cleanroom)
    kind = {r["combination"]: r["kind"] for r in man}
    tier1 = {r["combination"] for r in man if r["tier"] == "1" and r["combination"]}

    arch_sel = rank_and_select(read_conclusions(archive), kind, tier1)
    cr_sel = rank_and_select(read_conclusions(cleanroom), kind, tier1)

    frozen_pairs = sorted(r["combination"].removesuffix("__holdout")
                          for r in read_manifest(cleanroom, "manifest_holdout.csv")
                          if r["tier"] == "2")
    faithful = arch_sel["pairs"] == frozen_pairs

    status = {r["combination"]: r["status"] for r in
              csv.DictReader((cleanroom / "analysis/05_stability/results/run_status.csv").open())}
    freeze = json.loads((cleanroom / "analysis/05_stability/results/holdout_freeze_check.json").read_text())

    out = {
        "what_this_is": "Why batch 25's clean-room run of analysis/run.sh exited 1 before "
                        "the phase-E half: the development manifest's tier-2 selection is "
                        "re-derived at run time from tier-1 skill scores, and those divide "
                        "by an unseeded model.",
        "archive": str(archive),
        "cleanroom": str(cleanroom),
        "models": models_block(archive, cleanroom),
        "tier2": {
            "rule": "results/tier2_rule.md, applied by select_tier2 in plan_manifest.py",
            "reimplementation_reproduces_the_archived_selection": faithful,
            "frozen_tier2_pairs": frozen_pairs,
            "archived_run": arch_sel,
            "cleanroom_run": cr_sel,
            "pairs_lost": sorted(set(arch_sel["pairs"]) - set(cr_sel["pairs"])),
            "pairs_gained": sorted(set(cr_sel["pairs"]) - set(arch_sel["pairs"])),
            "groups_that_changed": sorted(
                g for g in GROUPS if arch_sel["groups"][g] != cr_sel["groups"][g]),
        },
        "band": band_block(archive, cleanroom),
        "the_run": {
            "rows_that_did_not_run": {c: s for c, s in status.items() if s != "ran"},
            "freeze_check_verdict": freeze["verdict"],
            "frozen_rows_the_tree_no_longer_carries":
                freeze["fatal"]["frozen_rows_the_tree_no_longer_carries"],
            "frozen_rows_whose_structure_moved":
                freeze["fatal"]["frozen_rows_whose_structure_moved"],
            "unpaired_development_rows": freeze["unpaired_development_rows"]["rows"],
        },
    }
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"reimplementation reproduces the archived tier-2 selection: {faithful}")
    print(f"groups that changed: {out['tier2']['groups_that_changed']}")
    print(f"pairs lost: {len(out['tier2']['pairs_lost'])}, "
          f"gained: {len(out['tier2']['pairs_gained'])}")
    print(f"skill band {out['band']['archived']['skill_band']} -> "
          f"{out['band']['cleanroom']['skill_band']}; forks above it "
          f"{out['band']['archived']['n_forks_above_the_band']} -> "
          f"{out['band']['cleanroom']['n_forks_above_the_band']}")
    print(f"-> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
