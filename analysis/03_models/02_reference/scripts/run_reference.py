"""Run the field's own model on this dataset, from inside the tree.

The reference is WHO EWARS-csd as published at `chap-models/chapkit_ewars_model`, at its
own default configuration. It is not a candidate of ours and it is never tuned by us: the
project's success criterion is defined against what that model does out of the box, so
touching its configuration would be moving the target.

Three things make this node different from the model nodes beside it.

**It is pinned by image digest, not by a URL.** `chap eval --model-name <URL>` fetches at
run time, which would make the headline comparison depend on another repository's current
state. The digest below pins bytes; the image's `org.opencontainers.image.revision` label
carries the source commit those bytes were built from, so one pin fixes both, and the
label is read back out of the image at every run rather than trusted.

**It is served, not built.** The model is an amd64 R-INLA container that speaks the
chapkit REST protocol, so the script starts the service, waits for it to become healthy,
and points `chap eval` at the port with `--run-config.is-chapkit-model`. On an arm64
machine it runs under emulation, which is why it costs about ten times what a native
model of ours does.

**It is unseeded, so it is run more than once.** `scripts/predict.R` calls
`inla.posterior.sample` and `rnbinom` and never `set.seed`, and the service exposes no
seed, so the number the project is measured against is a draw rather than a constant.
Batch 4 measured that draw's spread at sd 0.196 CRPS. The project's reported conclusion
divides by this model's CRPS, so an unaveraged denominator would put a wobble of about
2 % on every conclusion -- the same size as the fork effects the stability run exists to
detect. This node therefore evaluates the reference REPEATS times and hands all of them
downstream; the scoring node forms the per-cell mean and keeps the individual repeats
beside it, so the spread stays visible rather than being averaged away silently.

Rule 6 cannot be satisfied for this model. It is quantified instead, which is the honest
alternative, and the asymmetry -- our baselines are bit-reproducible, the model we are
measured against is not -- is one of the project's findings rather than an inconvenience.

**Each repeat gets its own container, and a crashed repeat is retried.** See the comments
at the loop: batch 13 found that
one service shared across four repeats accumulates state and dies under a setup
combination that asks it for sixteen jobs a repeat instead of two.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[0] / "scripts" / "lib"))

from chap_eval import chap_eval, combo, repo_root, setup  # noqa: E402

IMAGE = ("ghcr.io/chap-models/chapkit_ewars_model@sha256:"
         "abd8098f2b828d3ef9899ed136d20a4f5387f8c3abe901f386905cec166d823a")
CONTAINER = "chap-reference-node"
PORT = 8010
REPEATS = 4
# Attempts allowed per repeat before the node gives up. The reference crashes
# intermittently -- "Prediction script did not create output file" -- at a rate batch 13
# measured at roughly one job in a hundred, so a 36-job row fails about a third of the
# time and nothing about the row is wrong when it does. A crashed repeat is replaced by
# another draw, not by a better one: the model is unseeded, so every repeat is a draw
# already, and `attempts_per_repeat` in the specification records how many it took. That
# is what keeps this a retry rather than a selection.
ATTEMPTS = 3

ROOT = repo_root(NODE)
COMBO = combo()


def run(*command: str, check: bool = True) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise SystemExit(f"{' '.join(command)} failed:\n{result.stderr}")
    return result.stdout.strip()


def image_pin() -> dict:
    """What the pinned image actually is, read back out of it rather than assumed."""
    if not run("docker", "image", "inspect", IMAGE, "--format", "{{.Id}}", check=False):
        print("pulling the reference image (4.7 GB, once)")
        run("docker", "pull", "--platform", "linux/amd64", IMAGE)
    fields = run("docker", "image", "inspect", IMAGE, "--format",
                 "{{.Id}}\t{{.Architecture}}/{{.Os}}\t{{.Size}}").split("\t")
    labels = json.loads(run("docker", "image", "inspect", IMAGE,
                            "--format", "{{json .Config.Labels}}") or "{}")
    return {
        "reference": IMAGE,
        "image_id": fields[0],
        "platform": fields[1],
        "size_bytes": int(fields[2]),
        "source_revision": (labels or {}).get("org.opencontainers.image.revision"),
        "source_url": (labels or {}).get("org.opencontainers.image.source"),
        "labels": labels,
    }


def start_service(out: Path) -> None:
    run("docker", "rm", "-f", CONTAINER, check=False)
    run("docker", "run", "-d", "--name", CONTAINER, "--platform", "linux/amd64",
        "-p", f"{PORT}:8000", IMAGE)
    for _ in range(90):
        health = subprocess.run(
            ["curl", "-sf", "--max-time", "5", f"http://localhost:{PORT}/health"],
            capture_output=True, text=True)
        if health.returncode == 0:
            break
        time.sleep(2)
    else:
        run("docker", "logs", CONTAINER, check=False)
        raise SystemExit("the reference service did not become healthy")
    for name, path in (("service_info", "api/v1/info"), ("config_schema", "api/v1/configs/$schema")):
        body = subprocess.run(["curl", "-sf", "--max-time", "20", f"http://localhost:{PORT}/{path}"],
                              capture_output=True, text=True).stdout
        if body:
            (out / f"{name}.json").write_text(body)


def main() -> None:
    out = NODE / "results" / COMBO
    # Cleared, not merged into. A failed re-run used to leave some repeats from this run
    # and some from the last, with the previous run's model_spec.json and run_cost.json
    # still beside them -- a set that looks complete and is a mean over draws from two
    # different commits. Nothing downstream could have detected that. The repeats are
    # not reproducible, so this does destroy draws; it destroys them at the point where
    # keeping them would mean reporting a mixture.
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    work = NODE / "work" / COMBO

    common = setup(ROOT, COMBO)
    flags = common["eval_flags"]
    pin = image_pin()

    # One container per repeat, not one for all four. The repeats are meant to be
    # independent draws of an unseeded model, and serving them from a single long-lived
    # service was a convenience that made them share accumulated state. Batch 13 found
    # what that costs: under `n_retrain = 8` the reference runs sixteen jobs per repeat
    # instead of two, the service slowed monotonically across the run -- 3.6, 5.6, then
    # 7.5 minutes -- and died nine jobs into the fourth repeat with "Server disconnected
    # without sending a response". A fresh container per repeat removes the accumulation
    # and makes the repeats independent in fact as well as in intent; it costs about
    # thirty seconds of start-up each.
    try:
        seconds = []
        attempts = []
        for repeat in range(1, REPEATS + 1):
            print(f"reference repeat {repeat} of {REPEATS}")
            for attempt in range(1, ATTEMPTS + 1):
                start_service(out)
                try:
                    seconds.append(chap_eval(
                        ROOT, model_name=f"http://localhost:{PORT}",
                        dataset=common["dataset_path"],
                        output=out / f"eval_repeat_{repeat}.nc",
                        log=out / f"eval_repeat_{repeat}.log",
                        flags=flags, runs_dir=work / f"runs_{repeat}",
                        extra=["--run-config.is-chapkit-model"]))
                except SystemExit:
                    if attempt == ATTEMPTS:
                        raise
                    print(f"  repeat {repeat} attempt {attempt} crashed; retrying")
                    continue
                attempts.append(attempt)
                break
    finally:
        run("docker", "rm", "-f", CONTAINER, check=False)

    spec = {
        "model": "reference",
        "origin": "external",
        "kind": "chapkit-service",
        "node": str(NODE.relative_to(ROOT)),
        "combo": COMBO,
        "evaluations": [f"eval_repeat_{r}.nc" for r in range(1, REPEATS + 1)],
        "repeats": REPEATS,
        "attempts_per_repeat": attempts,
        "repeat_names": [f"reference_r{r}" for r in range(1, REPEATS + 1)],
        "route": "chapkit REST service, amd64 image under emulation",
        "n_samples": 1000,
        "seeded": False,
        "seed": None,
        "randomness": "unseeded and not seedable. predict.R calls inla.posterior.sample "
                      "and rnbinom and never set.seed, and the service exposes no seed. "
                      "Quantified by repeating the evaluation rather than worked around.",
        "tuned_by_us": False,
        "eval_flags": flags,
        "setup_choices": common["choices"],
        "dataset": str(common["dataset_path"].relative_to(ROOT)),
        "dataset_sha256": common["dataset_sha256"],
        **pin,
    }
    (out / "model_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    cost = {
        "model": "reference",
        "combo": COMBO,
        "route": spec["route"],
        "repeats": REPEATS,
        "wall_clock_seconds_per_repeat": [round(s, 1) for s in seconds],
        "wall_clock_seconds": round(sum(seconds), 1),
        "seconds_per_split": round(sum(seconds) / (REPEATS * flags["n_splits"]), 1),
        "eval_flags": flags,
    }
    (out / "run_cost.json").write_text(json.dumps(cost, indent=1, sort_keys=True) + "\n")

    print(f"reference[{COMBO}]: {REPEATS} repeats, {cost['wall_clock_seconds']:.0f} s total "
          f"({cost['seconds_per_split']} s/split) -> {out}")


if __name__ == "__main__":
    main()
