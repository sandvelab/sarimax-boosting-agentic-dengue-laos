#!/usr/bin/env python3
"""What batch 32's fix to the equal-weighting premise changed, field by field.

`01_weighting/a_equal/scripts/choose_weighting.py` registers, before the pool runs, the
shape the pool will have: how many members, what weight each carries, and what share of
the mass sits on the plan's two required baselines. It built that statement from its own
glob over Chap contract directories. `prepare_members.py`, a few seconds later in the same
node, built the pool by resolving every alternatives fork above a contract to the child the
combination takes. The two agreed until batch 22 gave the persistence baseline and the
climatology baseline a second published construction each; from then the specification said
**six members at 1/6 with two-thirds of the mass on required baselines** and **four at 1/4**
ran. Batch 32 makes both read `03_models/scripts/lib/pool_shape.py`.

Every `model_option_spec.json` under `a_equal/results/` therefore has to be written again,
and with it every `candidate_spec.json` that embeds one as its `stages[0]`. This script
does that by running the tree's own two steps under each combination -- never by editing a
file -- and then compares both versions of every document key by key: `HEAD`'s copy out of
git, the working tree's beside it.

**The claim it exists to check is that nothing computed moves.** The premise reaches no
model: `model_configuration.yaml` is built from `user_option_values`, the covariates and
the seed, and its sha256 is what `chap eval` was pointed at. So

  `model_configuration.yaml` must be **byte-identical** for every combination, and
  `configuration_sha256`, `user_option_values` and `members_sha256` must not move.

If any of them does, the reported model would have to be re-run to say what it is, and this
script stops rather than leaving a tree in which it has silently changed.

`prepare_members.py` is deliberately **not** re-run. Its output is unchanged by this batch
-- verified separately, byte for byte -- and `members.json`'s digest is carried inside the
pool's own configuration, so rewriting that file at all is a thing to avoid rather than a
thing to check afterwards.

Writes AI-generated/validation/<date>_weightingPremiseRewrite.json
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENSEMBLE = ROOT / "analysis/03_models/03_candidate/c_ensemble"
EQUAL = ENSEMBLE / "01_weighting/a_equal"
PYTHON = ROOT / "environment/chapenv/bin/python"

#: Fields the fix adds to the premise.
ADDED_BY_THE_FIX = {"contracts_not_on_this_combinations_path"}
#: Prose that says where the premise came from and what it does not read. Both are
#: rewritten because both were describing the glob that is gone.
REWORDED_BY_THE_FIX = {"source", "nothing_downstream_is_read"}
#: The membership statement itself -- the thing that was wrong.
MEMBERSHIP_KEYS = {
    "members", "member_count", "weight_each_member_will_carry",
    "required_baselines_among_them", "share_of_the_pool_on_the_required_baselines",
}
#: Anything here moving means the model would have to be run again to say what it is.
MUST_NOT_MOVE = {"configuration_sha256", "members_sha256", "seed"}


def head_version(path: Path) -> dict | None:
    rel = path.relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{rel}"],
                         capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 else None


def head_bytes(path: Path) -> bytes | None:
    rel = path.relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{rel}"],
                         capture_output=True)
    return out.stdout if out.returncode == 0 else None


def flatten(document, prefix="") -> dict[str, object]:
    """Every leaf of the document, keyed by its path, so two versions can be compared.

    A list of scalars is one leaf -- `members` is a statement, and a member appearing at a
    different index is not a separate change. A list of documents is descended into:
    `candidate_spec.json` carries the whole weighting specification as `stages[0]`, and a
    version of this that stopped at the list reported the entire premise as one opaque
    field that had moved, which says nothing about which part of it did.
    """
    out: dict[str, object] = {}
    if isinstance(document, dict):
        for key, value in document.items():
            out |= flatten(value, f"{prefix}/{key}")
    elif isinstance(document, list) and any(isinstance(v, (dict, list)) for v in document):
        for index, value in enumerate(document):
            out |= flatten(value, f"{prefix}/{index}")
    elif isinstance(document, list):
        out[prefix] = json.dumps(document)
    else:
        out[prefix] = document
    return out


def classify(key: str, before, after) -> str:
    leaf = key.rsplit("/", 1)[-1]
    if leaf in ADDED_BY_THE_FIX:
        return "added"
    if leaf in REWORDED_BY_THE_FIX:
        return "reworded"
    if leaf in MEMBERSHIP_KEYS:
        return "membership"
    if leaf in MUST_NOT_MOVE:
        return "must_not_move"
    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        return "numeric"
    return "other"


def run(script: Path, combination: str) -> None:
    result = subprocess.run([str(PYTHON), str(script)], cwd=ROOT,
                            capture_output=True, text=True,
                            env={**os.environ, "COMBO": combination,
                                 "COMBO_BASE": ""})
    if result.returncode != 0:
        raise SystemExit(f"{script.name} failed under {combination!r}"
                         f" ({result.returncode})\n{result.stdout}\n{result.stderr}")


def compare(path: Path) -> dict | None:
    before, after = head_version(path), json.loads(path.read_text())
    if before is None:
        return {"file": path.relative_to(ROOT).as_posix(), "status": "new file"}
    old, new = flatten(before), flatten(after)
    changes: dict[str, list[str]] = {}
    moved: list[dict] = []
    for key in sorted(set(old) | set(new)):
        if key in old and key in new and old[key] == new[key]:
            continue
        kind = classify(key, old.get(key), new.get(key))
        changes.setdefault(kind, []).append(key)
        if kind in ("must_not_move", "numeric", "other"):
            moved.append({"field": key, "before": old.get(key), "after": new.get(key)})
    return {"file": path.relative_to(ROOT).as_posix(),
            "unchanged": not changes,
            "kinds": sorted(changes),
            "changed_fields": {k: v for k, v in sorted(changes.items())},
            "fields_that_should_not_have_moved": moved}


def main() -> int:
    combinations = sorted(p.name for p in (EQUAL / "results").iterdir() if p.is_dir())

    rows: list[dict] = []
    configurations: list[dict] = []
    premise_before: dict[str, int | None] = {}
    for combination in combinations:
        spec = EQUAL / "results" / combination / "model_option_spec.json"
        was = head_version(spec)
        premise_before[combination] = (was or {}).get("premise", {}).get("member_count")

        run(EQUAL / "scripts" / "choose_weighting.py", combination)
        rows.append(compare(spec) | {"combination": combination})

        candidate = ENSEMBLE / "results" / combination / "candidate_spec.json"
        if not candidate.exists():
            continue
        configuration = ENSEMBLE / "results" / combination / "model_configuration.yaml"
        before = head_bytes(configuration)
        run(ENSEMBLE / "scripts" / "assemble_candidate_config.py", combination)
        after = configuration.read_bytes()
        configurations.append({
            "combination": combination,
            "identical_to_head": before == after,
            "sha256": hashlib.sha256(after).hexdigest(),
        })
        rows.append(compare(candidate) | {"combination": combination})

    moved = [{"file": r["file"], "combination": r["combination"],
              "fields": r["fields_that_should_not_have_moved"]}
             for r in rows if r.get("fields_that_should_not_have_moved")]
    configuration_changed = [c["combination"] for c in configurations
                             if not c["identical_to_head"]]
    after_counts = {
        c: json.loads((EQUAL / "results" / c / "model_option_spec.json").read_text())
        ["premise"]["member_count"] for c in combinations}

    document = {
        "what_this_is": (
            "every model_option_spec.json under 01_weighting/a_equal and every "
            "candidate_spec.json that embeds one, HEAD's version against the working "
            "tree's, classified field by field, after re-running the tree's own two "
            "steps under each combination"),
        "combinations": len(combinations),
        "documents": len(rows),
        "member_count_before": {
            "six": sorted(c for c, n in premise_before.items() if n == 6),
            "four": sorted(c for c, n in premise_before.items() if n == 4),
            "other": {c: n for c, n in sorted(premise_before.items())
                      if n not in (4, 6)},
        },
        "member_count_after": sorted(set(after_counts.values())),
        "documents_unchanged": sum(1 for r in rows if r.get("unchanged")),
        "documents_changed_in_the_premise_only": sum(
            1 for r in rows if not r.get("unchanged")
            and set(r.get("kinds", [])) <= {"added", "reworded", "membership"}),
        "model_configurations_rebuilt": len(configurations),
        "model_configurations_identical_to_head": sum(
            1 for c in configurations if c["identical_to_head"]),
        "model_configurations_that_changed": configuration_changed,
        "fields_that_should_not_have_moved": moved,
        "configuration_sha256_unchanged_everywhere": not configuration_changed,
        "rows": rows,
        "configurations": configurations,
    }
    out = (ROOT / "AI-generated" / "validation"
           / f"{date.today():%y-%m-%d}_weightingPremiseRewrite.json")
    out.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    print(f"weighting premise rewrite: {document['combinations']} combinations, "
          f"{document['documents']} documents, "
          f"{document['documents_unchanged']} unchanged, "
          f"{document['documents_changed_in_the_premise_only']} changed in the premise "
          f"only; member counts before "
          f"{len(document['member_count_before']['six'])} six / "
          f"{len(document['member_count_before']['four'])} four, after "
          f"{document['member_count_after']}; "
          f"{document['model_configurations_identical_to_head']} of "
          f"{len(configurations)} model configurations byte-identical to HEAD; "
          f"{len(moved)} document(s) with a field that should not have moved -> {out}")
    return 1 if moved or configuration_changed else 0


if __name__ == "__main__":
    sys.exit(main())
