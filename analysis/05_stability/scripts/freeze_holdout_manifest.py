"""Fix what phase E runs on the held-out year, before the year is opened — and then defend it.

The plan's §3: the perturbation set run on the holdout is frozen **before** the holdout is
opened, because the holdout is opened once and evaluated many times, and that is only
honest if what gets evaluated was fixed in advance. A spread computed from a set chosen
after looking is not a spread. So this script writes the list phase E executes, and after
the first holdout number has been seen nothing is added to it, dropped from it, re-tuned or
re-run.

## The freeze wins over the recomputation

This script is the last step of the development half of `run.sh`, so it is reached on
**every** run of `analysis/run.sh` — and until batch 24 every one of those runs rebuilt the
frozen set from whatever the tree looked like at that moment. It returned byte-identical
because the tree had not changed, not because anything made it. `plan_manifest.py`, earlier
in the same block, re-derives the development manifest from the tree by design, and the
development manifest may legitimately grow: the plan's §3, clarified on 2026-09-01, binds
`manifest_holdout.csv` and nothing else, while `/validate invariants`'s `combos` check
*requires* every non-main child in the tree to have a development row. So a fork child added
after the opening was one `run.sh` away from being carried into the frozen set by a script
re-deriving what it had derived before — no
batch, no decision, plan §3 broken silently. Batch 18's outsider check added one child and
watched a 33-row frozen set become 34.

So the frozen file is now authoritative and this script has two modes, chosen by whether it
exists:

- **It does not exist** — this is the freeze. Refuse if the year has already been opened
  (below), refuse if the development half is unfinished, then write it. Batch 15's path.
- **It exists** — this is a verification, and nothing is written to it or to
  `holdout_freeze.json` at all. The set the tree would produce *now* is derived and compared
  against the set on disk, and the comparison is written to `results/holdout_freeze_check.json`.

What the comparison does with a difference follows the plan rather than being uniform:

  a development row with no frozen twin   reported as **unpaired**, never added. It is the
                                          case §3's clarification names: an alternative
                                          discovered after the freeze is carried in the tree
                                          and in the development manifest, has no holdout
                                          twin, and never joins the 32.
  a frozen row the tree no longer has     **fatal**. The frozen set names an analysis this
                                          repository can no longer run, so it can no longer
                                          be reproduced.
  a frozen row whose structure moved      **fatal**. The columns that say *what analysis
                                          runs* — its fork, its child, what it re-runs and
                                          what it inherits — are the set.
  a frozen row whose numbers moved        reported, not fatal. The development conclusions
                                          frozen beside each row are a record of what was
                                          paired, and the reference model is unseeded: a
                                          clean-room re-run moves the development skill
                                          score by about 0.006 without anything being wrong.
                                          Cost estimates drift for the same kind of reason.

The frozen file is never rewritten in either direction, so a difference stops the run or is
recorded — it is never absorbed.

## What is frozen, and what is not

**Frozen**: which combinations run, which fork child each takes, which models each re-runs
and which it inherits, the backtest scheme, the models on the leaderboard, the four repeats
of the unseeded reference, and — recorded row by row — the development conclusion each
holdout row is to be reported beside. The pairing matters as much as the set: reporting the
holdout spread against a development spread assembled afterwards would let the comparison
be chosen after the fact even though neither half was.

**Not frozen, because it is implementation**: how `02_setup` is pointed at the full file
rather than at the development file. That mechanism did not exist when the set was frozen and
batch 16 wrote it. It may not change anything in the paragraph above, and
`holdout_freeze.json` records the constraint so that a change would be visible rather than
convenient.

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

And it will not freeze at all once a holdout number has been seen. If the frozen file is
missing while `run_status_holdout.csv` records a row as `ran` or a `results/*__holdout/`
directory exists, the set is not re-derived — it is restored from git. Re-deriving it then
would be choosing the set after seeing the numbers, which is exactly what §3 forbids, and
the file is versioned precisely so that restoring it is the available move.

Writes, at this node:
  results/manifest_holdout.csv       the rows phase E runs, one per combination (once)
  results/holdout_freeze.json        what was frozen, when, against which files (once)
  results/holdout_freeze_check.json  what the tree would freeze now, against what is frozen

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
ANALYSIS_RESULTS = ROOT / "analysis/results"

SUFFIX = "__holdout"

# The columns that say *what analysis a row is*. A difference in any of them is a different
# set, whatever the row is called; a difference outside them is a number that moved under a
# set that did not. `built` belongs here: a row whose child has no scripts is a row the
# driver cannot run, so it decides what the frozen set can do as much as its fork does.
STRUCTURAL = ("rank", "tier", "combination", "development_combination", "kind", "fork",
              "child", "owner", "combo_base", "models_rerun", "models_inherited", "built")

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


def frozen_at() -> str:
    """The commit that first added the holdout manifest -- not HEAD.

    This field is the evidence that the phase-E set predates the year being opened, and
    writing HEAD into it meant that every later run overwrote that evidence with the
    current commit. Batch 16 ran the script once after the holdout and watched f3904c5
    become its own commit; the manifest itself came back byte-identical, so what was lost
    was only the date stamp, and only because the script was recomputing something git
    already records.

    So it is read from git: the commit that *adds* `manifest_holdout.csv`. On the very
    first run the file is not committed yet and there is no such commit, and HEAD is the
    honest answer then -- it is the commit the freeze was computed at, and the commit that
    adds the file is the next one, which is what the note beside this field says.

    Since batch 24 the field is written once and never again, because the file carrying it
    is written once and never again. This function is reached on the freeze and not on the
    verification.
    """
    found = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%h", "--",
         str((NODE / "results" / "manifest_holdout.csv").relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True).stdout.split()
    return found[-1] if found else commit()


def year_has_been_opened() -> list[str]:
    """Evidence, if any, that a holdout number has already been seen.

    Two independent kinds, and either is enough, because this guard is asked only when the
    frozen manifest is missing and the question is whether re-deriving it would be choosing
    the set after the event. `.holdout_opened` is deliberately not consulted: it is
    gitignored and says only that *this working tree* ran the year, which is the right
    question for the driver's re-run seal and the wrong one here. A fresh clone that has
    never run anything still inherits results computed from a set that was frozen, and
    re-deriving it there would be as wrong as doing it in the tree that opened the year.
    """
    seen = []
    status = RESULTS / "run_status_holdout.csv"
    if status.exists():
        ran = [r["combination"] for r in rows_of(status) if r["status"] == "ran"]
        if ran:
            seen.append(f"{status.relative_to(ROOT)} records {len(ran)} rows as `ran`")
    if ANALYSIS_RESULTS.is_dir():
        dirs = sorted(p.name for p in ANALYSIS_RESULTS.iterdir()
                      if p.is_dir() and p.name.endswith(SUFFIX))
        if dirs:
            seen.append(f"{len(dirs)} directories under "
                        f"{ANALYSIS_RESULTS.relative_to(ROOT)}/ carry the {SUFFIX} suffix")
    return seen


def refuse_if_the_year_has_been_opened() -> None:
    seen = year_has_been_opened()
    if not seen:
        return
    raise SystemExit(
        "results/manifest_holdout.csv is missing and the held-out year has already been "
        "opened (" + "; ".join(seen) + "). The frozen set is not re-derived after a "
        "holdout number has been seen — that is choosing the set after the event, which "
        "plan §3 forbids. The file is versioned so that the available move is to restore "
        "it:\n"
        "    git checkout -- analysis/05_stability/results/manifest_holdout.csv\n"
        "If it is genuinely to be re-frozen, that is a decision with a batch behind it, "
        "not something this script does because the file was absent.")


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


def derive(manifest: list[dict], conclusions: dict[str, dict]) -> tuple[list[dict], float]:
    """The set the development manifest and the current conclusions imply.

    On the freeze this is what gets written. Afterwards it is only ever compared against
    what was written, and this function is the reason the comparison is possible at all:
    one derivation, used both to freeze and to check the freeze, so the check cannot drift
    away from the thing it checks.
    """
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
    return out, total


def freeze(out: list[dict], total: float) -> None:
    """Write the set, once. Reached only when `manifest_holdout.csv` does not exist."""
    scheme = json.loads(SCHEME.read_text())
    notes = json.loads((RESULTS / "manifest_notes.json").read_text())

    with (RESULTS / "manifest_holdout.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)

    (RESULTS / "holdout_freeze.json").write_text(json.dumps({
        "what_this_is": (
            "The set of analyses phase E runs on the held-out year, fixed before the "
            "year is opened (plan §3). Phase E runs exactly this and nothing else."),
        "frozen_on": date.today().isoformat(),
        "frozen_at_commit": frozen_at(),
        "commit_note": ("The commit above is the one that added "
                        "`results/manifest_holdout.csv` to the repository, read from git "
                        "rather than recomputed -- so a later run of this script cannot "
                        "overwrite it. No file under `analysis/results/*__holdout/` "
                        "exists at that commit, which is what makes the set one that was "
                        "fixed before the year was opened. Before the manifest is "
                        "committed at all there is no such commit and this is HEAD, "
                        "which is then the commit the freeze was computed at."),
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


def verify(frozen: list[dict], derived: list[dict]) -> int:
    """Compare what the tree would freeze now against what is frozen. Write neither.

    Returns the number of fatal differences; the caller turns that into an exit status, so
    that a frozen set the tree has contradicted stops `analysis/run.sh` rather than being
    reported into a file nobody opens.
    """
    by_name_frozen = {r["combination"]: r for r in frozen}
    by_name_derived = {r["combination"]: r for r in derived}

    unpaired = sorted(set(by_name_derived) - set(by_name_frozen))
    missing = sorted(set(by_name_frozen) - set(by_name_derived))

    changed, drifted = [], []
    for name in sorted(set(by_name_frozen) & set(by_name_derived)):
        was, now = by_name_frozen[name], by_name_derived[name]
        moved = {c: {"frozen": was.get(c, ""), "now": now.get(c, "")}
                 for c in STRUCTURAL if was.get(c, "") != now.get(c, "")}
        if moved:
            changed.append({"combination": name, "columns": moved})
        numbers = {c: {"frozen": was.get(c, ""), "now": now.get(c, "")}
                   for c in now if c not in STRUCTURAL and was.get(c, "") != now.get(c, "")}
        if numbers:
            drifted.append({"combination": name, "columns": numbers})

    fatal = len(missing) + len(changed)
    frozen_path = RESULTS / "manifest_holdout.csv"
    recorded = json.loads((RESULTS / "holdout_freeze.json").read_text()).get(
        "frozen_inputs", {}).get("results/manifest_holdout.csv", "")
    digest = sha256(frozen_path)

    (RESULTS / "holdout_freeze_check.json").write_text(json.dumps({
        "what_this_is": (
            "What the tree would freeze now, compared against what is frozen. The frozen "
            "set is authoritative and is never rewritten; this file is the whole of what "
            "a later run of freeze_holdout_manifest.py produces (batch 24)."),
        "checked_on": date.today().isoformat(),
        "verdict": ("the frozen set is intact" if fatal == 0
                    else f"{fatal} difference(s) the frozen set cannot absorb"),
        "frozen": {
            "file": str(frozen_path.relative_to(ROOT)),
            "rows": len(frozen),
            "sha256": digest,
            "sha256_recorded_in_holdout_freeze_json": recorded,
            "still_the_file_that_was_frozen": digest == recorded,
        },
        "recomputed_rows": len(derived),
        "fatal": {
            "frozen_rows_the_tree_no_longer_carries": missing,
            "frozen_rows_whose_structure_moved": changed,
            "note": ("Either means the frozen set can no longer be reproduced, so the run "
                     "stops. The structural columns are " + ", ".join(STRUCTURAL) + "."),
        },
        "unpaired_development_rows": {
            "rows": unpaired,
            "note": ("Development rows with no twin in the frozen set. Plan §3, clarified "
                     "2026-09-01: the freeze binds this manifest and not the tree or the "
                     "development manifest, so an alternative discovered after the "
                     "opening is carried in both of those, has no holdout twin, and never "
                     "joins the 32. It is reported here and not added."),
        },
        "drift_under_an_unchanged_set": {
            "rows": drifted,
            "note": ("Non-structural columns that moved: the development conclusions "
                     "frozen beside each row, and the cost estimates. The reference model "
                     "is unseeded, so a re-run of the development half moves the skill "
                     "score by about 0.006 with nothing wrong; batch 18's clean-room run "
                     "measured 0.0065 on the headline. Reported, never absorbed — the "
                     "frozen columns stay as they were frozen."),
        },
        "binding": BINDING,
    }, indent=1, sort_keys=False) + "\n")

    where = (RESULTS / "holdout_freeze_check.json").relative_to(ROOT)
    print(f"frozen set verified, not rewritten: {len(frozen)} rows, "
          f"{len(unpaired)} unpaired development row(s), {len(drifted)} row(s) whose "
          f"numbers drifted -> {where}")
    if missing:
        print(f"  FATAL: the tree no longer carries {len(missing)} frozen row(s): "
              f"{', '.join(missing)}")
    for entry in changed:
        print(f"  FATAL: {entry['combination']} moved in "
              f"{', '.join(sorted(entry['columns']))}")
    if fatal:
        print("  The frozen set is what phase E ran. Fix the tree, or open a batch for "
              "the change; this script does not rewrite it.")
    return fatal


def main() -> None:
    manifest = rows_of(RESULTS / "manifest.csv")
    conclusions = {r["combination"]: r for r in rows_of(RESULTS / "conclusions.csv")}
    frozen_path = RESULTS / "manifest_holdout.csv"

    if frozen_path.exists():
        derived, _ = derive(manifest, conclusions)
        raise SystemExit(1 if verify(rows_of(frozen_path), derived) else 0)

    refuse_if_the_year_has_been_opened()
    refuse_if_development_is_unfinished(manifest, list(conclusions.values()))
    out, total = derive(manifest, conclusions)
    freeze(out, total)


if __name__ == "__main__":
    main()
