#!/usr/bin/env bash
# Batch 6 — the vertical slice: one model, end to end, through Chap's own evaluation.
#
# The point is not the score. The point is that every link in the chain has been
# exercised once on the real dataset, at the fixed scheme, with a file at every join:
#
#   archived data -> development file -> model contract -> chap eval -> chap-core's
#   metric -> the contract files the claim tree consumes
#
# Run from the repository root:
#   bash AI-internal/vertical-slice/run_vertical_slice.sh
#
# The model implemented here is a required baseline of the plan's §4, so it is real
# project code rather than a throwaway: batch 7 moves persistence_model/ into
# analysis/03_models/01_baselines/01_persistence/ and re-runs it from the node.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHAP="$ROOT/environment/chapenv/bin/chap"
PY="$ROOT/environment/chapenv/bin/python"
SLICE="$ROOT/AI-internal/vertical-slice"
OUT="${SLICE_OUT:-$ROOT/AI-generated/vertical-slice}"
WORK="$OUT/slice-work"
MODEL="$SLICE/persistence_model"
DEV="$ROOT/analysis/01_data/01_partition/results/development_1998-01_2009-12.csv"

MODEL_NAME="persistence"
COMBO="${COMBO:-main}"

# The scheme fixed in batch 3. It does not move (readme-at-start.md).
N_PERIODS=3
N_SPLITS=8
STRIDE=3
N_RETRAIN=1

mkdir -p "$OUT" "$WORK" "$OUT/results"
export PYTHONWARNINGS=ignore

# --- What went in ----------------------------------------------------------------
# Hashed before the run, so the record names the bytes that were read rather than the
# path they were read from.
{
    shasum -a 256 "$DEV"
    shasum -a 256 "$MODEL"/MLproject "$MODEL"/pyproject.toml "$MODEL"/uv.lock \
                  "$MODEL"/train.py "$MODEL"/predict.py
} | sed "s|$ROOT/||" > "$OUT/slice_inputs.sha256"

# --- The run ---------------------------------------------------------------------
START=$(date +%s)
CHAP_RUNS_DIR="$WORK/runs" "$CHAP" eval \
    --model-name "$MODEL" \
    --dataset-csv "$DEV" \
    --output-file "$OUT/persistence_development_eval.nc" \
    --backtest-params.n-periods "$N_PERIODS" \
    --backtest-params.n-splits "$N_SPLITS" \
    --backtest-params.stride "$STRIDE" \
    --backtest-params.n-retrain "$N_RETRAIN" \
    > "$OUT/persistence_development_eval.log" 2>&1
END=$(date +%s)

# --- The contract files ----------------------------------------------------------
"$PY" "$SLICE/collect_metrics.py" \
    --evaluation "$OUT/persistence_development_eval.nc" \
    --model "$MODEL_NAME" \
    --out-dir "$OUT/results" \
    --combo "$COMBO"

# --- What it cost ----------------------------------------------------------------
# Written by the script that held the clock, not read off a terminal.
cat > "$OUT/slice_run_cost.json" <<JSON
{
  "model": "$MODEL_NAME",
  "route": "MLproject with uv_env, native arm64",
  "dataset": "development_1998-01_2009-12.csv",
  "n_periods": $N_PERIODS,
  "n_splits": $N_SPLITS,
  "stride": $STRIDE,
  "n_retrain": $N_RETRAIN,
  "combination": "$COMBO",
  "wall_clock_seconds": $((END - START)),
  "seconds_per_split": $(python3 -c "print(round(($END-$START)/$N_SPLITS,1))")
}
JSON

# --- The fitted model, kept -------------------------------------------------------
# chap-core fits once (n_retrain 1) into its run directory, which is not tracked. The
# fitted object is what the forecasts' spread comes from, so it is copied out.
find "$WORK/runs" -name "model" -type f -newermt "@$START" -print0 \
    | xargs -0 -I{} cp {} "$OUT/persistence_fitted_model.json" 2>/dev/null || true

echo "done -> $OUT/results/$COMBO/"
