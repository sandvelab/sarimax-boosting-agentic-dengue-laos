"""Time the steps of the pipeline that no model's `run_cost.json` covers.

Every model in this project writes what its backtest cost, so the expensive part of a
combination's cost is already on disk and the manifest reads it. The cheap part is not:
nothing times the setup chain that assembles the dataset, the scoring chain that turns
evaluations into a leaderboard, or the root's conclusion. Those three are what a
combination pays on top of its models, and a manifest whose cost column was part measured
and part asserted would be a manifest nobody could check.

So they are measured, the only way a duration can be: by running them. **All three are
re-runs of the main path under `COMBO=main`**, not runs of a scratch combination — they
recompute the files they already produced, from the same inputs, and leave the working tree
byte-identical. That property is not assumed: `--check-clean` asks git whether anything
under `analysis/` changed and fails if it did, because a step that is not idempotent cannot
be timed this way and the manifest would rather know.

What is deliberately *not* here: `03_models`. Re-running it would re-run the reference
model, which is unseeded, and would move the denominator of every comparison in the project
by up to 0.57 CRPS for no reason but a stopwatch.

Writes, at this node:
  results/step_costs.json   seconds per step, and what was excluded
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
PYTHON = ROOT / "environment/chapenv/bin/python"

# Each step, as the command that runs it. The manifest needs the setup chain and the
# scoring chain separately, because a scoring fork pays the second and not the first.
STEPS = {
    "02_setup": ["bash", str(ROOT / "analysis/02_setup/run.sh")],
    "04_score": ["bash", str(ROOT / "analysis/04_score/run.sh")],
    "conclude": [str(PYTHON), str(ROOT / "analysis/scripts/conclude.py")],
}


def dirty() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain", "--", "analysis"],
        capture_output=True, text=True, check=True)
    return [line for line in result.stdout.splitlines()
            if line[:2] in (" M", "M ", "MM", " D", "D ")]


def main() -> None:
    check_clean = "--check-clean" in sys.argv
    before = dirty() if check_clean else []

    environment = {**os.environ, "COMBO": "main"}
    environment.pop("COMBO_BASE", None)
    timings = {}
    for name, command in STEPS.items():
        started = time.time()
        result = subprocess.run(command, cwd=ROOT, env=environment,
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise SystemExit(f"{name} failed ({result.returncode}):\n{result.stdout[-2000:]}"
                             f"\n{result.stderr[-2000:]}")
        timings[name] = round(time.time() - started, 2)
        print(f"  {name}: {timings[name]:.2f} s")

    after = dirty() if check_clean else []
    changed = sorted(set(after) - set(before))
    if check_clean and changed:
        raise SystemExit(
            "re-running the main path under COMBO=main changed files:\n  "
            + "\n  ".join(changed)
            + "\nThese steps are timed by re-running them, which is only honest if they "
              "are idempotent. Fix the step, not this check.")

    out = NODE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "step_costs.json").write_text(json.dumps({
        "seconds": timings,
        "measured_by": "05_stability/scripts/measure_step_costs.py",
        "method": ("each step re-run under COMBO=main and timed; the working tree is "
                   "byte-identical afterwards, which is what makes a re-run a legitimate "
                   "measurement of the original"),
        "idempotence_checked": bool(check_clean),
        "excluded": {
            "03_models": ("not timed: re-running it re-runs the unseeded reference model "
                          "and would move the denominator of every comparison in the "
                          "project. Its cost is read from each model's own run_cost.json "
                          "instead."),
        },
        "splits": 8,
        "machine": f"{platform.system()} {platform.machine()}",
    }, indent=1, sort_keys=True) + "\n")
    print(f"-> {(out / 'step_costs.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
