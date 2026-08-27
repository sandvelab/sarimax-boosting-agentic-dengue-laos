"""The one route by which a model of ours reaches Chap's evaluation.

Every model in this project must be scored the same way; a candidate compared on a
metric computed a different way is not compared at all. The cheapest guarantee of that
is that there is only one piece of code that calls `chap eval`, and every model node
calls it. This module is that code, and it lives under `03_models/scripts/lib/` rather
than at any one model, because a copy per model is a set of copies that will drift.

It is a library, not a step: `scripts/lib/` is a subdirectory, so `node.py` does not put
it in any node's `run.sh`. The steps are the one-screen runners at the model nodes, which
say what model they are running and nothing else.

What it guarantees for every caller:

  * the dataset and the evaluation flags come from `02_setup/results/$COMBO/`, so no
    model script carries the backtest scheme as a constant of its own;
  * the run is timed by the process that ran it and the cost written to a file;
  * the model's own files are hashed into its spec before the run, so the record names
    the bytes that were evaluated;
  * every model writes the same `model_spec.json`, which is what lets `04_score` collect
    them without knowing what any of them is;
  * a model that takes configuration is pointed at a **file** for it, and that file is
    hashed into the spec, so what a run was configured with is a stored artifact rather
    than a command line nobody kept.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "lib"))
from combos import combo, resolve  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup(root: Path, name: str) -> dict:
    """The common ground assembled by `02_setup` for this combination.

    A combination that moved only a candidate-internal fork faces the same common ground
    as the combination it branched from, so the lookup falls back to `COMBO_BASE` and
    records which combination answered it. `bash analysis/run.sh` sets no base, so the
    main path can inherit nothing.
    """
    path, from_combo = resolve(root / "analysis/02_setup/results", "setup_spec.json")
    spec = json.loads(path.read_text())
    spec["dataset_path"] = path.parent / spec["dataset"]
    spec["setup_from_combo"] = from_combo
    return spec


def chap_eval(root: Path, *, model_name: str, dataset: Path, output: Path, log: Path,
              flags: dict, runs_dir: Path, configuration: Path | None = None,
              extra: list[str] | None = None) -> float:
    """One `chap eval`, timed. Returns wall-clock seconds.

    The scheme flags are passed through from `02_setup`; this function chooses none of
    them. `configuration` is a model configuration YAML assembled by the model's own node
    -- chap-core parses it, writes it into the run directory and substitutes it for the
    `{model_config}` placeholder in the model's entry points. `extra` carries the few
    switches that are a property of how a model is served rather than of the evaluation
    -- `--run-config.is-chapkit-model` for a service.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(root / "environment/chapenv/bin/chap"), "eval",
        "--model-name", model_name,
        "--dataset-csv", str(dataset),
        "--output-file", str(output),
        "--backtest-params.n-periods", str(flags["n_periods"]),
        "--backtest-params.n-splits", str(flags["n_splits"]),
        "--backtest-params.stride", str(flags["stride"]),
        "--backtest-params.n-retrain", str(flags["n_retrain"]),
        *(["--model-configuration-yaml", str(configuration)] if configuration else []),
        *(extra or []),
    ]
    environment = {**os.environ, "CHAP_RUNS_DIR": str(runs_dir), "PYTHONWARNINGS": "ignore"}
    start = time.time()
    with log.open("w") as handle:
        handle.write("$ " + " ".join(command) + "\n\n")
        handle.flush()
        result = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT,
                                env=environment)
    seconds = time.time() - start
    if result.returncode != 0:
        raise SystemExit(f"chap eval failed ({result.returncode}); see {log}")
    return seconds


def run_local_model(node: Path, *, name: str, model_dir: Path, n_samples: int,
                    seeded: bool, seed: int | None = None, note: str = "",
                    configuration: Path | None = None) -> dict:
    """Evaluate one `MLproject` model of ours, and write the contract files.

    `model_dir` is the model contract directory -- the one holding `MLproject`. chap-core
    builds its environment from the `pyproject.toml` and `uv.lock` inside it, so the
    model's dependencies are pinned by a file that travels with the model rather than by
    whatever the evaluating machine happens to hold.

    `configuration`, when given, is the model configuration YAML this model's node
    assembled for this combination. It is hashed into the spec and its contents copied
    into it, so the record of the run names both the file and what was in it.
    """
    root = repo_root(node)
    name_combo = combo()
    out = node / "results" / name_combo
    out.mkdir(parents=True, exist_ok=True)
    work = node / "work" / name_combo
    shutil.rmtree(work, ignore_errors=True)

    common = setup(root, name_combo)
    flags = common["eval_flags"]

    # The contract files only. chap-core's `uv_env` runner builds the model's
    # environment into a `.venv` inside this directory, and that build is not part of
    # the model -- it is the lockfile's consequence, and the lockfile is hashed here.
    model_files = {
        str(p.relative_to(model_dir)): sha256(p)
        for p in sorted(model_dir.rglob("*"))
        if p.is_file() and not any(part.startswith(".") or part == "__pycache__"
                                   for part in p.relative_to(model_dir).parts)
    }

    seconds = chap_eval(
        root, model_name=str(model_dir), dataset=common["dataset_path"],
        output=out / "eval.nc", log=out / "eval.log", flags=flags,
        runs_dir=work / "runs", configuration=configuration)

    # chap-core fits into its run directory, which is working space and not tracked.
    # The fitted object is what the forecasts' spread comes from, so it is copied out.
    fitted = sorted(p for p in (work / "runs").rglob("model") if p.is_file())
    if fitted:
        shutil.copy(fitted[-1], out / "fitted_model.json")

    # The lockfile chap-core actually built from, compared with the tracked one. Batch 2
    # established that pinning chap-core does not pin the models; this is the check that
    # closes that gap for a model of ours, run every time rather than once.
    built_locks = sorted(p for p in (work / "runs").rglob("uv.lock") if p.is_file())
    lock_matches = None
    if built_locks and (model_dir / "uv.lock").exists():
        lock_matches = sha256(built_locks[-1]) == sha256(model_dir / "uv.lock")

    spec = {
        "model": name,
        "origin": "ours",
        "kind": "local-mlproject",
        "node": str(node.relative_to(root)),
        "combo": name_combo,
        "setup_from_combo": common["setup_from_combo"],
        "evaluations": ["eval.nc"],
        "repeats": 1,
        "route": "MLproject with uv_env, native",
        "n_samples": n_samples,
        "seeded": seeded,
        "seed": seed,
        "randomness": note,
        "eval_flags": flags,
        "setup_choices": common["choices"],
        "dataset": str(common["dataset_path"].relative_to(root)),
        "dataset_sha256": common["dataset_sha256"],
        "model_dir": str(model_dir.relative_to(root)),
        "model_files_sha256": model_files,
        "shipped_lockfile_is_the_one_built_from": lock_matches,
        "configuration": str(configuration.relative_to(root)) if configuration else None,
        "configuration_sha256": sha256(configuration) if configuration else None,
        "configuration_contents": (yaml.safe_load(configuration.read_text())
                                   if configuration else None),
    }
    (out / "model_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    cost = {
        "model": name,
        "combo": name_combo,
        "route": spec["route"],
        "wall_clock_seconds": round(seconds, 1),
        "seconds_per_split": round(seconds / flags["n_splits"], 1),
        "eval_flags": flags,
    }
    (out / "run_cost.json").write_text(json.dumps(cost, indent=1, sort_keys=True) + "\n")

    print(f"{name}[{name_combo}]: {seconds:.0f} s "
          f"({cost['seconds_per_split']} s/split) -> {out}")
    return spec
