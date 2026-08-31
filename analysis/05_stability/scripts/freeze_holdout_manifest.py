"""Fix what phase E runs on the held-out year, before the year is opened.

The plan's §3: the perturbation set run on the holdout is frozen **before** the holdout is
opened, because the holdout is opened once and evaluated many times, and that is only
honest if what gets evaluated was fixed in advance. A spread computed from a set chosen
after looking is not a spread. So this script writes the list phase E executes, and after
the first holdout number has been seen nothing is added to it, dropped from it, re-tuned or
re-run.

## What is frozen here, and what is not

**Frozen**: which combinations run, which fork child each takes, which models each re-runs
and which it inherits, the backtest scheme, the models on the leaderboard, the four repeats
of the unseeded reference, and — recorded row by row — the development conclusion each
holdout row is to be reported beside. The pairing matters as much as the set: reporting the
holdout spread against a development spread assembled afterwards would let the comparison
be chosen after the fact even though neither half was.

**Not frozen, because it is implementation**: how `02_setup` is pointed at the full file
rather than at the development file. That mechanism does not exist yet and batch 16 writes
it. It may not change anything in the paragraph above, and `holdout_freeze.json` records
the constraint so that a change would be visible rather than convenient.

## Why the rows are renamed

A holdout row writes under `analysis/results/<combination>/`, and a run that reused the
development names would overwrite the development results the holdout is to be reported
against. So every row carries its development name with `__holdout` appended, and the
development directories survive untouched. The suffix is not the pair separator being
reused: `collect_conclusions.py` and the driver both read a row's forks from its own `fork`
and `child` columns and never from its name, which is a label.

## What this refuses to do

It will not freeze a manifest whose development half is unfinished. Every row must have a
conclusion or a recorded reason that is not "waiting for a batch", every tier-2 slot must
be resolved, and `tier2_rule.md` must still hash to what `manifest_notes.json` recorded
before tier 1 ran. A holdout set frozen around rows nobody had run would be a set chosen by
what happened to finish.

Writes, at this node:
  results/manifest_holdout.csv  the rows phase E runs, one per combination
  results/holdout_freeze.json   what was frozen, when, against which files

Seeds: none.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
RESULTS = NODE / "results"
SCHEME = ROOT / "analysis/01_data/02_characterise/results/backtest_scheme_chosen.json"
PARTITION = ROOT / "analysis/01_data/01_partition/results"

SUFFIX = "__holdout"

# The obligations phase E inherits, quoted from where they were decided rather than
# restated. Text; nothing computes with it.
BINDING = {
    "the holdout is opened once": (
        "plan §3. If it has to be opened a second time, that it happened and why is "
        "recorded. It is opened once and evaluated many times, across this manifest."),
    "nothing is added, dropped, re-tuned or re-run after a holdout number has been seen": (
        "plan §3. This file is the set; a row that fails is reported as a row that "
        "failed, not replaced."),
    "the reference is re-scored four times on the holdout": (
        "plan, phase E. It is unseeded and the conclusion divides by it, so an "
        "unaveraged denominator would put the reference's own re-run noise on every "
        "number reported."),
    "the holdout numbers are reported beside the development numbers": (
        "plan, phase E, and the pairing is frozen here row by row. If the holdout "
        "numbers are much worse, that gap is the result and is reported plainly."),
    "nothing is promoted out of this set": (
        "phase C is closed. A perturbation that scores better on the holdout than the "
        "main path does not become the main path."),
}


def rows_of(path: Path) -> list[dict]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def refuse_if_development_is_unfinished(manifest: list[dict],
                                        conclusions: list[dict]) -> None:
    by_combination = {r["combination"]: r for r in conclusions}
    unresolved = [r["rank"] for r in manifest if not r["combination"]]
    if unresolved:
        raise SystemExit(f"tier-2 slots {unresolved} are unresolved: the pair rule has "
                         f"not been applied, so there is no set to freeze")
    waiting = [r["combination"] for r in manifest
               if by_combination.get(r["combination"], {}).get("skill_score", "") == ""
               and "not run yet" in by_combination.get(r["combination"], {}).get(
                   "why_not", "")]
    if waiting:
        raise SystemExit(f"{len(waiting)} development rows have not run: "
                         f"{', '.join(waiting)}. Freezing the holdout set around the "
                         f"rows that happened to finish is the selection this freeze "
                         f"exists to prevent.")
    notes = json.loads((RESULTS / "manifest_notes.json").read_text())
    rule = sha256(RESULTS / "tier2_rule.md")
    recorded = notes["tier2_rule_sha256"]
    if rule != recorded:
        raise SystemExit(
            f"tier2_rule.md hashes to {rule[:12]} and manifest_notes.json records "
            f"{recorded[:12]}. The rule that chose the pairs has changed since it was "
            f"fixed; the pairs would be chosen after the event.")


def main() -> None:
    manifest = rows_of(RESULTS / "manifest.csv")
    conclusions = {r["combination"]: r for r in rows_of(RESULTS / "conclusions.csv")}
    refuse_if_development_is_unfinished(manifest, list(conclusions.values()))

    scheme = json.loads(SCHEME.read_text())
    notes = json.loads((RESULTS / "manifest_notes.json").read_text())

    out, total = [], 0.0
    for row in manifest:
        development = conclusions.get(row["combination"], {})
        seconds = float(row["est_seconds_holdout"] or 0.0)
        total += seconds
        out.append({
            "rank": row["rank"],
            "tier": row["tier"],
            "combination": row["combination"] + SUFFIX,
            "development_combination": row["combination"],
            "kind": row["kind"],
            "fork": row["fork"],
            "child": row["child"],
            "owner": row["owner"],
            "combo_base": ("-" if row["combo_base"] in ("-", "")
                           else row["combo_base"] + SUFFIX),
            "models_rerun": row["models_rerun"],
            "models_inherited": row["models_inherited"],
            "built": row["built"],
            "est_seconds_holdout": row["est_seconds_holdout"],
            # The development conclusion this row is to be reported beside, carried here
            # so the pairing is fixed with the set rather than assembled afterwards.
            "development_skill_score": development.get("skill_score", ""),
            "development_crps_ours": development.get("crps_ours", ""),
            "development_crps_reference": development.get("crps_reference", ""),
            "development_coverage_10_90": development.get("coverage_10_90_ours", ""),
            "development_our_model": development.get("our_model", ""),
            "status": ("frozen" if development.get("skill_score", "") != ""
                       else "frozen; " + development.get("why_not", "")),
        })

    with (RESULTS / "manifest_holdout.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)

    (RESULTS / "holdout_freeze.json").write_text(json.dumps({
        "what_this_is": (
            "The set of analyses phase E runs on the held-out year, fixed before the "
            "year is opened (plan §3). Phase E runs exactly this and nothing else."),
        "frozen_on": date.today().isoformat(),
        "frozen_at_commit": commit(),
        "commit_note": ("The commit above is HEAD when this file was written. The "
                        "evidence that the set predates the holdout is the commit that "
                        "*adds* this file, which is the next one, and the fact that no "
                        "file under `analysis/results/*__holdout/` exists at it."),
        "rows": len(out),
        "rows_by_tier": {tier: sum(1 for r in out if r["tier"] == tier)
                         for tier in sorted({r["tier"] for r in out})},
        "naming": {
            "rule": f"every development combination name with `{SUFFIX}` appended",
            "why": ("a holdout row writes under analysis/results/<combination>/, and "
                    "reusing the development names would overwrite the results the "
                    "holdout is to be reported against"),
        },
        "dataset": {
            "reads": "Archive/lao-dataset/chap_LAO_admin1_monthly.csv, the full file",
            "the development runs read": str(
                (PARTITION / "development_1998-01_2009-12.csv").relative_to(ROOT)),
            "the sealed part": str(
                (PARTITION / "holdout_2010_SEALED.csv").relative_to(ROOT)),
            "evaluated_span": scheme["phase_e_evaluated_span"],
            "train_set_last_period": scheme["phase_e_train_set_last_period"],
            "training_never_reaches_2010": scheme["phase_e_training_never_reaches_2010"],
            "source": str(SCHEME.relative_to(ROOT)),
        },
        "backtest_scheme": {**scheme["phase_e_scheme"],
                            "n_retrain": scheme["n_retrain"],
                            "source": str(SCHEME.relative_to(ROOT)),
                            "note": ("fixed in batch 3 and not moved since. Four splits "
                                     "rather than eight, because the evaluated span is "
                                     "one year rather than two.")},
        "leaderboard_models": notes["leaderboard_models"],
        "our_reported_model": notes["our_reported_model"],
        "our_reported_family": notes["our_reported_family"],
        "estimated_seconds_total": round(total, 1),
        "estimated_hours_total": round(total / 3600, 2),
        "budget_hours_both_datasets": notes["budget_hours_both_datasets"],
        "cut_for_budget": [],
        "cut_note": ("Nothing is cut. `manifest_notes.json` carries the cut order "
                     "against the day something is; the holdout half is the cheaper of "
                     "the two and the development half already ran inside budget."),
        "frozen_inputs": {
            "results/manifest.csv": sha256(RESULTS / "manifest.csv"),
            "results/manifest_holdout.csv": sha256(RESULTS / "manifest_holdout.csv"),
            "results/tier2_rule.md": sha256(RESULTS / "tier2_rule.md"),
            "results/conclusions.csv": sha256(RESULTS / "conclusions.csv"),
            "results/distribution.json": sha256(RESULTS / "distribution.json"),
        },
        "left_to_batch_16": {
            "how 02_setup reaches the full file": (
                "the development runs read the file `01_data/01_partition` wrote, and "
                "phase E reads the archived file. The switch is implementation and does "
                "not exist yet. It may not change the rows, the scheme, the models or "
                "the pairing above."),
            "what it may not do": (
                "add a row, drop a row, re-tune anything, or re-run a row after seeing "
                "its number"),
        },
        "binding": BINDING,
    }, indent=1, sort_keys=False) + "\n")

    print(f"{len(out)} rows frozen for the holdout, "
          f"{total / 3600:.2f} h estimated -> "
          f"{(RESULTS / 'manifest_holdout.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
