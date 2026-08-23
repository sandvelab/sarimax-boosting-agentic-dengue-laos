#!/usr/bin/env bash
# Batch-2 reconnaissance: capture what the installed chap-core actually is and does, into
# files, so that the batch report quotes stored output rather than terminal scrollback.
#
# Run from the repository root:  bash AI-internal/reconnaissance/capture_chap_surface.sh
#
# Everything it writes lands in AI-generated/chap-reconnaissance/ and is regenerable by
# re-running this script against the same pinned environment.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHAP="$ROOT/environment/chapenv/bin/chap"
PY="$ROOT/environment/chapenv/bin/python"
OUT="$ROOT/AI-generated/chap-reconnaissance"
WORK="$OUT/smoke-work"

# Pins. The example data comes from the chap-core release tag we installed; the smoke-test
# model from a specific commit. Neither is allowed to float: an install recipe verified
# against a moving target verifies nothing.
CHAP_TAG="v2.1.0"
EXAMPLE_CSV="hydromet_5_filtered.csv"
MODEL_REPO="https://github.com/dhis2-chap/minimalist_example_uv.git"
MODEL_COMMIT="a67d427bfde1341be6618e64c9a4a9a2c79cec2a"

mkdir -p "$OUT" "$WORK"
export PYTHONWARNINGS=ignore
export COLUMNS=110

echo "== CLI surface =="
"$CHAP" --version           > "$OUT/chap_version.txt" 2>&1
"$CHAP" --help              > "$OUT/chap_help.txt" 2>&1
"$CHAP" eval --help         > "$OUT/chap_eval_help.txt" 2>&1
"$CHAP" export-metrics --help > "$OUT/chap_export_metrics_help.txt" 2>&1
"$CHAP" test                > "$OUT/chap_test.txt" 2>&1

echo "== fetching pinned smoke-test inputs =="
curl -sSL --max-time 120 -o "$WORK/$EXAMPLE_CSV" \
  "https://raw.githubusercontent.com/dhis2-chap/chap-core/$CHAP_TAG/example_data/$EXAMPLE_CSV"
(cd "$WORK" && shasum -a 256 "$EXAMPLE_CSV") > "$OUT/smoke_inputs.sha256"

rm -rf "$WORK/model"
git clone -q "$MODEL_REPO" "$WORK/model"
git -C "$WORK/model" checkout -q "$MODEL_COMMIT"
git -C "$WORK/model" log -1 --format="model %H %cI" >> "$OUT/smoke_inputs.sha256"

echo "== chap eval (smoke test: 5 regions, monthly, 3 periods x 4 splits) =="
# CHAP_RUNS_DIR is set explicitly: chap-core otherwise writes run directories to ./runs
# relative to the working directory, which makes where you stood part of the recipe.
CHAP_RUNS_DIR="$WORK/runs" "$CHAP" eval \
    --model-name "$WORK/model" \
    --dataset-csv "$WORK/$EXAMPLE_CSV" \
    --output-file "$OUT/smoke_eval.nc" \
    --backtest-params.n-periods 3 \
    --backtest-params.n-splits 4 \
    > "$OUT/smoke_eval.log" 2>&1

echo "== chap export-metrics =="
"$CHAP" export-metrics \
    --input-files "$OUT/smoke_eval.nc" \
    --output-file "$OUT/smoke_metrics_aggregate.csv" \
    >> "$OUT/smoke_eval.log" 2>&1

echo "== describing the evaluation output =="
"$PY" "$ROOT/AI-internal/reconnaissance/describe_evaluation.py" \
    --evaluation "$OUT/smoke_eval.nc" \
    --out-dir "$OUT"

echo "done -> $OUT"
