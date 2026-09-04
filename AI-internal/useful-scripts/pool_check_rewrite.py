#!/usr/bin/env python3
"""What batch 28's rewrite of the pool checks changed, field by field.

`check_pool.py` matched each pool member to a stored evaluation by globbing sibling result
directories and taking the first hit, so which evaluation it named -- and whether it found
one at all -- depended on which combinations existed on disk when it ran. Batch 28 replaced
the tie-break with a rule over the combination names and made the last step of
`05_stability/run.sh` settle every row once the whole set has run.

That rewrites 49 of the 51 `pool_check.json` files, and the claim the batch report makes
about them -- that no number moved except in the rows that gained a reconstruction -- is a
comparison of two versions of every file, which is a thing to compute rather than to read
off a diff. So this walks both versions key by key: `HEAD`'s copy out of git, the working
tree's beside it.

A change is classified as
  `naming`         the evaluation a member is compared against is named differently, and it
                   is the same model on the same data, so nothing computed moves;
  `annotation`     a field the rewrite adds, `chosen_by`, saying which clause of the rule
                   chose the evaluation;
  `reconstruction` the row gained (or lost) its independent rebuild of the pool, and with
                   it the members' own scores, coverages and flat-interval shares;
  `numeric`        a number that existed before and is different now. **The batch's own
                   check: this list must be empty.**

Writes AI-generated/validation/<date>_poolCheckRewrite.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENSEMBLE = ROOT / "analysis/03_models/03_candidate/c_ensemble"
ADDED_BY_THE_REWRITE = {"chosen_by"}
#: Everything the reconstruction fills in, and only fills in, when it can be done.
RECONSTRUCTION_KEYS = {
    "mean_crps_rebuilt", "difference", "not_done_because",
    "members_without_a_matching_stored_evaluation", "member_mean_crps_by_this_path",
    "best_member_mean_crps", "mean_of_member_mean_crps", "pool_beats_its_best_member_by",
    "member_coverage_10_90", "largest_member_coverage_10_90",
    "members_ranked_on_the_evaluated_period",
}


def head_version(path: Path) -> dict | None:
    rel = path.relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{rel}"],
                         capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 else None


def flatten(document, prefix="") -> dict[str, object]:
    """Every leaf of the document, keyed by its path, so two versions can be compared."""
    out: dict[str, object] = {}
    if isinstance(document, dict):
        for key, value in document.items():
            out |= flatten(value, f"{prefix}/{key}")
    elif isinstance(document, list):
        out[prefix] = json.dumps(document)
    else:
        out[prefix] = document
    return out


def classify(key: str, before, after) -> str:
    leaf = key.rsplit("/", 1)[-1]
    if leaf in ADDED_BY_THE_REWRITE:
        return "annotation"
    if leaf in RECONSTRUCTION_KEYS or (before is None) != (after is None):
        return "reconstruction"
    if leaf in ("combination", "evaluation"):
        return "naming"
    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        return "numeric"
    return "other"


def main() -> int:
    rows, numeric = [], []
    for directory in sorted((ENSEMBLE / "results").iterdir()):
        path = directory / "pool_check.json"
        if not path.exists():
            continue
        before, after = head_version(path), json.loads(path.read_text())
        if before is None:
            rows.append({"combination": directory.name, "status": "new file"})
            continue
        old, new = flatten(before), flatten(after)
        changes: dict[str, list[str]] = {}
        for key in sorted(set(old) | set(new)):
            if old.get(key) == new.get(key) and key in old and key in new:
                continue
            kind = classify(key, old.get(key), new.get(key))
            changes.setdefault(kind, []).append(key)
            if kind == "numeric":
                numeric.append({"combination": directory.name, "field": key,
                                "before": old.get(key), "after": new.get(key)})
        rows.append({
            "combination": directory.name,
            "unchanged": not changes,
            "kinds": sorted(changes),
            "changed_fields": {k: v for k, v in sorted(changes.items())},
            "reconstruction_before": before["reconstruction"]["mean_crps_rebuilt"],
            "reconstruction_after": after["reconstruction"]["mean_crps_rebuilt"],
            "mean_crps_as_run_before": before["reconstruction"]["mean_crps_as_run"],
            "mean_crps_as_run_after": after["reconstruction"]["mean_crps_as_run"],
        })

    gained = [r for r in rows if r.get("reconstruction_before") is None
              and r.get("reconstruction_after") is not None]
    lost = [r for r in rows if r.get("reconstruction_before") is not None
            and r.get("reconstruction_after") is None]
    document = {
        "what_this_is": ("every pool_check.json in the tree, HEAD's version against the "
                         "working tree's, classified field by field"),
        "files": len(rows),
        "unchanged": sum(1 for r in rows if r.get("unchanged")),
        "changed_in_naming_only": sum(1 for r in rows
                                      if set(r.get("kinds", [])) <= {"naming", "annotation"}
                                      and not r.get("unchanged")),
        "gained_a_reconstruction": [r["combination"] for r in gained],
        "lost_a_reconstruction": [r["combination"] for r in lost],
        "numeric_changes_to_values_that_existed_before": numeric,
        "as_run_scores_all_unchanged": all(
            r["mean_crps_as_run_before"] == r["mean_crps_as_run_after"] for r in rows
            if "mean_crps_as_run_before" in r),
        "rows": rows,
    }
    out = (ROOT / "AI-generated" / "validation"
           / f"{date.today():%y-%m-%d}_poolCheckRewrite.json")
    out.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    print(f"pool check rewrite: {document['files']} files, "
          f"{document['unchanged']} unchanged, "
          f"{document['changed_in_naming_only']} changed in naming only, "
          f"{len(gained)} gained a reconstruction, {len(lost)} lost one, "
          f"{len(numeric)} numeric change(s) to values that existed before -> {out}")
    return 1 if numeric or lost else 0


if __name__ == "__main__":
    sys.exit(main())
