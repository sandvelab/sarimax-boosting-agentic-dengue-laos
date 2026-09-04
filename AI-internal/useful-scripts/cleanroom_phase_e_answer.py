"""The three phase-E answer files, archived beside a clean-room run's, field by field.

Batch 27's clean-room run exited 1 at `pair_holdout_development.py`, the script that writes
`holdout_vs_development.json`, `holdout_vs_development.csv` and `fork_sensitivity_both.csv`.
Those three were therefore carried unchanged out of the clone's index, and batch 27's
comparison reported them as *identical* -- a reading that was wrong for the same reason
batch 25's holdout half had to be read as absent: a file that was never written cannot have
reproduced. Batch 31's run wrote them, so they can be compared for the first time.

None of the three is expected to come back byte-identical: every skill score in them divides
by the reference model, which is an unseeded external container. Byte-identity was never the
question. The question is *which* fields moved, and specifically whether the fields the
phase-E answer reports as counts and orderings -- the ones a reader would quote -- moved with
the reference or held.

So each scalar is classified into one of two kinds:

  reference-derived   a skill score, a CRPS of the reference, a noise band, or a figure
                      computed from one. Expected to move; reported with its delta.
  structural          a count, a rank, a rank correlation, a name, a membership list. These
                      are what the phase-E answer asserts, and a move here is a finding.

The split is by field path, listed below rather than inferred, so that a field added later
is classified deliberately rather than falling into whichever bucket a heuristic picks.

Usage:
  .venv/bin/python AI-internal/useful-scripts/cleanroom_phase_e_answer.py \
      --archive . --artefacts <artefacts-dir> --out <file>.json

Writes one JSON. Reads only; runs no analysis. Seeds: none.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REL = "analysis/05_stability/results"

# Field paths in holdout_vs_development.json whose value is a skill score, a reference CRPS,
# a noise band, or arithmetic on one. Everything else in the file is treated as structural.
REFERENCE_DERIVED = {
    "/the_reported_analysis/development_skill_score",
    "/the_reported_analysis/holdout_skill_score",
    "/the_reported_analysis/gap",
    "/the_reported_analysis/development_crps_reference",
    "/the_reported_analysis/holdout_crps_reference",
    "/how_hard_the_year_was/reference_crps_development",
    "/how_hard_the_year_was/reference_crps_holdout",
    "/the_two_spreads/development/min",
    "/the_two_spreads/development/median",
    "/the_two_spreads/development/max",
    "/the_two_spreads/development/range",
    "/the_two_spreads/development/noise_band",
    "/the_two_spreads/holdout/min",
    "/the_two_spreads/holdout/median",
    "/the_two_spreads/holdout/max",
    "/the_two_spreads/holdout/range",
    "/the_two_spreads/holdout/noise_band",
    "/the_gap/min",
    "/the_gap/median",
    "/the_gap/max",
    "/the_gap/range",
}


def flatten(o, p: str = "") -> dict[str, object]:
    """Every scalar in the document, keyed by its path. Lists are kept whole."""
    out: dict[str, object] = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flatten(v, f"{p}/{k}"))
    else:
        out[p] = o
    return out


def compare_json(archive: Path, clean: Path, name: str) -> dict:
    a, b = flatten(json.loads((archive / REL / name).read_text())), \
           flatten(json.loads((clean / name).read_text()))
    moved_ref, moved_struct, identical = {}, {}, []
    for key in sorted(set(a) | set(b)):
        va, vb = a.get(key), b.get(key)
        if va == vb:
            identical.append(key)
            continue
        entry: dict[str, object] = {"archived": va, "cleanroom": vb}
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) \
                and not isinstance(va, bool) and not isinstance(vb, bool):
            entry["delta"] = vb - va
        (moved_ref if key in REFERENCE_DERIVED else moved_struct)[key] = entry
    return {
        "file": name,
        "scalars": len(set(a) | set(b)),
        "identical": len(identical),
        "moved_reference_derived": moved_ref,
        "moved_structural": moved_struct,
        "structural_fields_all_held": not moved_struct,
        "identical_fields": identical,
    }


def compare_csv(archive: Path, clean: Path, name: str, key_column: str) -> dict:
    def rows(p: Path) -> dict[str, dict[str, str]]:
        with p.open() as fh:
            return {r[key_column]: r for r in csv.DictReader(fh)}

    a, b = rows(archive / REL / name), rows(clean / name)
    shared = sorted(set(a) & set(b))
    cells, identical, moved = 0, 0, {}
    for k in shared:
        for col in sorted(set(a[k]) | set(b[k])):
            cells += 1
            if a[k].get(col) == b[k].get(col):
                identical += 1
            else:
                moved.setdefault(col, []).append(
                    {"row": k, "archived": a[k].get(col), "cleanroom": b[k].get(col)})
    return {
        "file": name,
        "rows_archived": len(a),
        "rows_cleanroom": len(b),
        "same_rows_by_name": sorted(set(a)) == sorted(set(b)),
        "rows_only_in_archive": sorted(set(a) - set(b)),
        "rows_only_in_cleanroom": sorted(set(b) - set(a)),
        "cells_compared": cells,
        "cells_identical": identical,
        "columns_that_moved": {c: len(v) for c, v in sorted(moved.items())},
        "columns_that_held": sorted(
            c for c in (set(a[shared[0]]) if shared else set()) if c not in moved),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True, type=Path)
    ap.add_argument("--artefacts", required=True, type=Path,
                    help="the preserved clean-room copies of the three answer files")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    payload = {
        "what_this_is": (
            "The three files pair_holdout_development.py writes, archived beside a "
            "clean-room run's. Batch 27 never wrote them -- it exited 1 at that script -- "
            "so its comparison reported them unchanged and that reading was wrong. This is "
            "the first run in which they can be compared at all."),
        "archive": str(args.archive),
        "cleanroom_artefacts": str(args.artefacts),
        "holdout_vs_development_json": compare_json(
            args.archive, args.artefacts, "holdout_vs_development.json"),
        "holdout_vs_development_csv": compare_csv(
            args.archive, args.artefacts, "holdout_vs_development.csv", "combination"),
        "fork_sensitivity_both_csv": compare_csv(
            args.archive, args.artefacts, "fork_sensitivity_both.csv", "fork"),
    }
    args.out.write_text(json.dumps(payload, indent=1) + "\n")

    j = payload["holdout_vs_development_json"]
    print(f"holdout_vs_development.json: {j['identical']} of {j['scalars']} scalars "
          f"identical; {len(j['moved_reference_derived'])} reference-derived moved, "
          f"{len(j['moved_structural'])} structural moved")
    for k in ("holdout_vs_development_csv", "fork_sensitivity_both_csv"):
        c = payload[k]
        print(f"{c['file']}: {c['cells_identical']} of {c['cells_compared']} cells "
              f"identical; same rows by name: {c['same_rows_by_name']}; "
              f"columns that moved: {list(c['columns_that_moved'])}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
