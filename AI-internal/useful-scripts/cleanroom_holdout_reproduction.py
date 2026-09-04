"""What a clean-room run establishes about the phase-E half, and what the freeze comparison found.

Batch 18 reproduced the reported development main path. Batch 25 reproduced the whole
development set and exited 1 before phase E. Batch 27 ran phase E from a clean checkout for
the first time and exited 1 at the last script. Batch 31 ran the whole thing to exit 0.
This script reports what came back.

Two questions, and they are different:

**Did the models reproduce?** Per model and per combination, on both halves, comparing
`crps_by_model` in each `analysis/results/<combo>/conclusion.json`. The models this project
wrote are seeded; the reference model is an external container that is not, so it is
counted separately and its movement is the expected finding rather than a defect.

**What did the frozen-figure comparison find?** Each frozen `development_skill_score` in
`manifest_holdout.csv` is a record of what was paired at the freeze; `conclusions.csv` is
what the tree computes today, and the two cannot agree on a tree whose development half has
been re-run, because that score divides by the unseeded reference. Until batch 30 the
difference was fatal to `pair_holdout_development.py` at a tolerance of 1e-9 -- which is why
batch 27 stopped -- and it is now reported instead. What stays fatal is a *moved pairing*: a
frozen row with no development twin of that name. This reports both, separately, so the
distinction the script now draws can be checked from outside it.

Writes one JSON. Reads only; runs no analysis. Seeds: none.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

FROZEN_TOLERANCE = 1e-9  # the value pair_holdout_development.py uses


def conclusions_of(tree: Path, holdout: bool) -> dict[str, dict]:
    out = {}
    for d in sorted((tree / "analysis/results").glob("*")):
        if not d.is_dir():
            continue
        if d.name.endswith("__holdout") != holdout:
            continue
        p = d / "conclusion.json"
        if p.exists():
            out[d.name] = json.loads(p.read_text())
    return out


def reproduction(archive: Path, clean: Path, holdout: bool) -> dict:
    a, b = conclusions_of(archive, holdout), conclusions_of(clean, holdout)
    shared = sorted(set(a) & set(b))
    ours: dict[str, dict] = {}
    reference: dict[str, dict] = {}
    for combo in shared:
        for model, va in a[combo].get("crps_by_model", {}).items():
            vb = b[combo].get("crps_by_model", {}).get(model)
            if vb is None:
                continue
            bucket = reference if model.startswith("reference") else ours
            entry = bucket.setdefault(model, {"identical": 0, "moved": 0, "deltas": {}})
            if va == vb:
                entry["identical"] += 1
            else:
                entry["moved"] += 1
                entry["deltas"][combo] = {"archived": va, "cleanroom": vb,
                                          "delta": vb - va}
    return {
        "combinations_compared": len(shared),
        "only_in_archive": sorted(set(a) - set(b)),
        "only_in_cleanroom": sorted(set(b) - set(a)),
        "our_models": ours,
        "the_unseeded_reference": reference,
        "our_scores_compared": sum(m["identical"] + m["moved"] for m in ours.values()),
        "our_scores_moved": sum(m["moved"] for m in ours.values()),
    }


def why_it_stopped(archive: Path, clean: Path) -> dict:
    """The rows pair_holdout_development.py raised on, and whether the pairing itself moved."""
    frozen = {r["combination"]: r for r in csv.DictReader(
        (clean / "analysis/05_stability/results/manifest_holdout.csv").open())}
    today = {r["combination"]: r for r in csv.DictReader(
        (clean / "analysis/05_stability/results/conclusions.csv").open())}

    drifted, pairing_moved = [], []
    for name, row in frozen.items():
        twin = row["development_combination"]
        if twin not in today:
            pairing_moved.append({"combination": name,
                                  "development_combination": twin,
                                  "why": "no development row of that name today"})
            continue
        fv, tv = row["development_skill_score"], today[twin].get("skill_score", "")
        if fv in ("", None) or tv in ("", None):
            continue
        if abs(float(fv) - float(tv)) > FROZEN_TOLERANCE:
            drifted.append({"combination": twin,
                            "frozen": float(fv), "today": float(tv),
                            "delta": float(tv) - float(fv)})

    def sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    man = "analysis/05_stability/results/manifest_holdout.csv"
    deltas = [d["delta"] for d in drifted]
    return {
        "what_is_compared": ("each frozen development_skill_score against what "
                             "conclusions.csv says today, at "
                             f"{FROZEN_TOLERANCE}. Before batch 30 a difference stopped "
                             "pair_holdout_development.py; it is now reported, and only a "
                             "moved pairing is fatal"),
        "rows_whose_frozen_figure_drifted": len(drifted),
        "rows_whose_pairing_actually_moved": pairing_moved,
        "frozen_manifest_sha256": {"cleanroom": sha(clean / man),
                                   "archive": sha(archive / man),
                                   "identical": sha(clean / man) == sha(archive / man)},
        "drift": sorted(drifted, key=lambda d: -abs(d["delta"])),
        "drift_summary": {
            "n": len(deltas),
            "min": min(deltas) if deltas else None,
            "max": max(deltas) if deltas else None,
            "all_within_the_development_noise_band": None,
        },
    }



def phase_e_headline(archive: Path, clean: Path) -> dict:
    """The holdout distribution, archived beside the clean-room's, on the fields phase E reports."""
    rel = "analysis/05_stability/results/holdout_distribution.json"
    a = json.loads((archive / rel).read_text())
    b = json.loads((clean / rel).read_text())

    def band(d):
        return d["reference_noise_band"]["skill_band"]

    def above(d):
        return sorted(f["fork"] for f in
                      d["sensitivity"]["moving_more_than_the_reference_noise_band"])

    pairs = {
        "skill_score_main_path": (a["reported_conclusion"]["skill_score"],
                                  b["reported_conclusion"]["skill_score"]),
        "crps_ours_main_path": (a["reported_conclusion"]["crps_ours"],
                                b["reported_conclusion"]["crps_ours"]),
        "crps_reference_main_path": (a["reported_conclusion"]["crps_reference"],
                                     b["reported_conclusion"]["crps_reference"]),
        "rank_within_the_distribution": (
            a["reported_conclusion"]["rank_within_the_distribution"],
            b["reported_conclusion"]["rank_within_the_distribution"]),
        "beats_the_reference": (a["does_the_conclusion_hold"]["beats_the_reference"],
                                b["does_the_conclusion_hold"]["beats_the_reference"]),
        "beats_both_required_baselines": (
            a["does_the_conclusion_hold"]["beats_both_required_baselines"],
            b["does_the_conclusion_hold"]["beats_both_required_baselines"]),
        "rows_inside_the_reference_noise_band": (
            a["skill_score"]["rows_inside_the_reference_noise_band"],
            b["skill_score"]["rows_inside_the_reference_noise_band"]),
        "reference_noise_band": (band(a), band(b)),
        "forks_above_the_band": (len(above(a)), len(above(b))),
    }
    return {
        "note": ("The phase-E answer, archived beside the clean-room's. crps_ours is a "
                 "model this project seeded; crps_reference is the external container "
                 "that is not."),
        "fields": {k: {"archived": x, "cleanroom": y, "identical": x == y}
                   for k, (x, y) in pairs.items()},
        "forks_above_the_band_archived": above(a),
        "forks_above_the_band_cleanroom": above(b),
        "identical_fields": sorted(k for k, (x, y) in pairs.items() if x == y),
    }



ANSI = re.compile(r"\x1b\[[0-9;]*m")


def environment_check(artefacts: Path) -> dict:
    """Whether the clean-room's environment was the lockfile's, colour codes aside.

    `install-chap.sh` compares its own `uv pip freeze` output against the lockfile by byte
    diff. On batch 27's run it reported `DOES NOT MATCH environment/lock.txt` against an
    environment that matched exactly: `uv` emits ANSI colour when the invoking shell forces
    it, which that session did, so every line differed by its wrapper and `sort` ordered the
    wrapped names differently on top of that. Batch 27 fixed the script; what it reports is
    read from `install_env.log` here rather than assumed, so this block says what the run it
    is describing actually printed. The set comparison below is the question the check means
    to ask, and it is answered independently of the check's own verdict.
    """
    reported = "no line matching matches/DOES NOT MATCH in install_env.log"
    log = artefacts / "install_env.log"
    if log.exists():
        for line in log.read_text(errors="replace").splitlines():
            if line.startswith(("matches environment/lock.txt",
                                "DOES NOT MATCH environment/lock.txt")):
                reported = line.strip()
                break
    freeze = (artefacts / "freeze_raw.txt").read_text().splitlines()
    lock = [l for l in (artefacts / "lock.txt").read_text().splitlines()
            if l and not l.startswith("#")]
    stripped = [ANSI.sub("", l) for l in freeze]
    coloured = sum(1 for l in freeze if ANSI.search(l))
    return {
        "install_chap_sh_reported": reported,
        "lines_carrying_ansi_colour": coloured,
        "packages_in_lockfile": len(lock),
        "packages_installed": len(stripped),
        "identical_as_sets_once_colour_is_stripped": sorted(stripped) == sorted(lock),
        "in_lockfile_not_installed": sorted(set(lock) - set(stripped)),
        "installed_not_in_lockfile": sorted(set(stripped) - set(lock)),
        "verdict": ("the environment is the lockfile's"
                    if sorted(stripped) == sorted(lock)
                    else "the package sets genuinely differ"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True, type=Path)
    ap.add_argument("--cleanroom", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--artefacts", required=True, type=Path,
                    help="the preserved clean-room artefacts: freeze_raw.txt and lock.txt")
    args = ap.parse_args()

    dev = reproduction(args.archive, args.cleanroom, holdout=False)
    hold = reproduction(args.archive, args.cleanroom, holdout=True)
    stop = why_it_stopped(args.archive, args.cleanroom)

    band = json.loads((args.cleanroom /
                       "analysis/05_stability/results/distribution.json").read_text()
                      )["reference_noise_band"]["skill_band"]
    stop["drift_summary"]["all_within_the_development_noise_band"] = all(
        abs(d["delta"]) < band for d in stop["drift"])
    stop["drift_summary"]["the_band_this_run_measured"] = band

    payload = {
        "what_this_is": (
            "A clean-room run of analysis/run.sh: what reproduced on each half, and what "
            "the comparison against the frozen development figures found."),
        "archive": str(args.archive),
        "cleanroom": str(args.cleanroom),
        "development_half": dev,
        "holdout_half": hold,
        "the_frozen_figure_comparison": stop,
        "phase_e_headline": phase_e_headline(args.archive, args.cleanroom),
        "environment": environment_check(args.artefacts),
    }
    args.out.write_text(json.dumps(payload, indent=1) + "\n")

    for half, d in (("development", dev), ("holdout", hold)):
        print(f"{half}: {d['combinations_compared']} combinations, "
              f"{d['our_scores_compared']} scores from models this project wrote, "
              f"{d['our_scores_moved']} moved")
    env = payload["environment"]
    print(f"environment: {env['packages_installed']} packages, "
          f"identical as sets: {env['identical_as_sets_once_colour_is_stripped']} "
          f"({env['lines_carrying_ansi_colour']} lines were colour-wrapped)")
    head = payload["phase_e_headline"]
    print(f"phase E headline: {len(head['identical_fields'])} of "
          f"{len(head['fields'])} reported fields identical")
    print(f"{stop['rows_whose_frozen_figure_drifted']} frozen figure(s) drifted; "
          f"pairing moved on {len(stop['rows_whose_pairing_actually_moved'])}; "
          f"frozen manifest identical: {stop['frozen_manifest_sha256']['identical']}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
