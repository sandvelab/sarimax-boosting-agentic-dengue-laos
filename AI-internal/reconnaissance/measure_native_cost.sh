#!/usr/bin/env bash
# Batch-4 reconnaissance: what does an evaluation run cost for a model of *our own* kind?
#
# The reference's 149 seconds is an amd64 R-INLA fit under emulation, which is not the unit
# batch 5's budget needs: our own candidates will be native Python served through an
# `MLproject` with a `uv_env`, and nothing has yet measured one of those on this dataset at
# this scheme. This runs chap-core's own minimal Python example — a linear regression that
# emits a single sample — over the development file, purely to price the machinery.
#
# Run from the repository root:  bash AI-internal/reconnaissance/measure_native_cost.sh
#
# The CRPS this produces is NOT a candidate score. The model is a placeholder that emits one
# draw per cell, which makes its CRPS numerically equal to its MAE; it is reported only so
# that the cost figure beside it is not a number with an unexamined provenance.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHAP="$ROOT/environment/chapenv/bin/chap"
PY="$ROOT/environment/chapenv/bin/python"
OUT="$ROOT/AI-generated/method-reconnaissance"
WORK="$OUT/native-work"
DEV="$ROOT/analysis/01_data/01_partition/results/development_1998-01_2009-12.csv"

MODEL_REPO="https://github.com/dhis2-chap/minimalist_example_uv.git"
MODEL_COMMIT="a67d427bfde1341be6618e64c9a4a9a2c79cec2a"   # the pin batch 2 used

N_PERIODS=3
N_SPLITS=8
STRIDE=3
N_RETRAIN=1

mkdir -p "$OUT" "$WORK"
export PYTHONWARNINGS=ignore

rm -rf "$WORK/model"
git clone -q "$MODEL_REPO" "$WORK/model"
git -C "$WORK/model" checkout -q "$MODEL_COMMIT"

START=$(date +%s)
CHAP_RUNS_DIR="$WORK/runs" "$CHAP" eval \
    --model-name "$WORK/model" \
    --dataset-csv "$DEV" \
    --output-file "$WORK/native_development_eval.nc" \
    --backtest-params.n-periods "$N_PERIODS" \
    --backtest-params.n-splits "$N_SPLITS" \
    --backtest-params.stride "$STRIDE" \
    --backtest-params.n-retrain "$N_RETRAIN" \
    > "$OUT/native_development_eval.log" 2>&1
END=$(date +%s)

"$PY" "$ROOT/AI-internal/reconnaissance/score_evaluation.py" \
    --evaluation "$WORK/native_development_eval.nc" \
    --out-dir "$WORK" \
    --prefix native_development
cp "$WORK/native_development_metrics_global.csv" "$OUT/native_development_metrics_global.csv"

cat > "$OUT/native_run_cost.json" <<JSON
{
  "model": "dhis2-chap/minimalist_example_uv@$MODEL_COMMIT",
  "kind": "MLproject with uv_env, native arm64, linear regression, one sample per cell",
  "purpose": "cost measurement only -- not a candidate score",
  "dataset": "development_1998-01_2009-12.csv",
  "n_periods": $N_PERIODS,
  "n_splits": $N_SPLITS,
  "stride": $STRIDE,
  "n_retrain": $N_RETRAIN,
  "wall_clock_seconds": $((END - START)),
  "seconds_per_split": $(python3 -c "print(round(($END-$START)/$N_SPLITS,1))")
}
JSON

echo "done -> $OUT/native_run_cost.json"
