#!/usr/bin/env bash
# Batch-4 reconnaissance: how reproducible is the reference model's score?
#
# `scripts/predict.R` in chapkit_ewars_model calls `inla.posterior.sample` and `rnbinom`
# and never calls `set.seed`. The reference is therefore stochastic and unseeded, which
# means the number the plan's §2 asks us to beat is not a fixed number but a draw. How wide
# that draw is decides how large a difference between our candidate and the reference can
# be read as anything at all -- so it is measured here rather than assumed small.
#
# Run from the repository root:  bash AI-internal/reconnaissance/ewars_reproducibility.sh
#
# Repeats the identical `chap eval` invocation REPEATS times against one service instance,
# scores each, and writes the per-repeat headline metrics to one table.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHAP="$ROOT/environment/chapenv/bin/chap"
PY="$ROOT/environment/chapenv/bin/python"
OUT="$ROOT/AI-generated/method-reconnaissance"
WORK="$OUT/ewars-work"
REPEAT_DIR="$WORK/repeats"
DEV="$ROOT/analysis/01_data/01_partition/results/development_1998-01_2009-12.csv"

IMAGE="ghcr.io/chap-models/chapkit_ewars_model@sha256:abd8098f2b828d3ef9899ed136d20a4f5387f8c3abe901f386905cec166d823a"
CONTAINER="ewars-repro"
PORT=8001
REPEATS=3

N_PERIODS=3
N_SPLITS=8
STRIDE=3
N_RETRAIN=1

mkdir -p "$REPEAT_DIR"
export PYTHONWARNINGS=ignore

cleanup() { docker rm -f "$CONTAINER" >/dev/null 2>&1 || true; }
trap cleanup EXIT

cleanup
docker run -d --name "$CONTAINER" --platform linux/amd64 -p "$PORT:8000" "$IMAGE" >/dev/null
for _ in $(seq 1 60); do
  if curl -sf --max-time 5 "http://localhost:$PORT/health" >/dev/null 2>&1; then break; fi
  sleep 2
done

for r in $(seq 1 "$REPEATS"); do
  echo "== repeat $r of $REPEATS =="
  CHAP_RUNS_DIR="$REPEAT_DIR/runs_$r" "$CHAP" eval \
      --model-name "http://localhost:$PORT" \
      --run-config.is-chapkit-model \
      --dataset-csv "$DEV" \
      --output-file "$REPEAT_DIR/ewars_repeat_$r.nc" \
      --backtest-params.n-periods "$N_PERIODS" \
      --backtest-params.n-splits "$N_SPLITS" \
      --backtest-params.stride "$STRIDE" \
      --backtest-params.n-retrain "$N_RETRAIN" \
      > "$REPEAT_DIR/ewars_repeat_$r.log" 2>&1
  "$PY" "$ROOT/AI-internal/reconnaissance/score_evaluation.py" \
      --evaluation "$REPEAT_DIR/ewars_repeat_$r.nc" \
      --out-dir "$REPEAT_DIR" \
      --prefix "repeat_$r"
done

# The run from run_ewars_reference.sh counts as a repeat too: same image, same command,
# same data. Including it makes the spread a spread over four draws rather than three.
"$PY" - "$OUT" "$REPEAT_DIR" "$REPEATS" <<'PYEOF'
import sys
from pathlib import Path

import pandas as pd

out_dir, repeat_dir, repeats = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])

rows = []
sources = [("reference_run", out_dir / "ewars_development_metrics_global.csv")]
sources += [(f"repeat_{r}", repeat_dir / f"repeat_{r}_metrics_global.csv") for r in range(1, repeats + 1)]
for label, path in sources:
    frame = pd.read_csv(path).set_index("metric")["value"]
    rows.append({"run": label, **frame.to_dict()})

per_run = pd.DataFrame(rows)
per_run.to_csv(out_dir / "ewars_repeatability_runs.csv", index=False)

summary = per_run.drop(columns="run").agg(["mean", "std", "min", "max"]).T
summary["spread_pct_of_mean"] = 100 * (summary["max"] - summary["min"]) / summary["mean"]
summary.rename_axis("metric").reset_index().to_csv(out_dir / "ewars_repeatability_summary.csv", index=False)
PYEOF

echo "done -> $OUT/ewars_repeatability_runs.csv"
