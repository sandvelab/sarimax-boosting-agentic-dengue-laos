#!/usr/bin/env bash
# Batch-4 reconnaissance: establish that the reference model runs on this project's
# development dataset, at what cost, and with what score.
#
# The plan (§2) names https://github.com/chap-models/chapkit_ewars_model as the model to
# beat. It is a chapkit REST service in an amd64-only R-INLA container, so this script is
# also the answer to "can the reference be run at all on this machine".
#
# Run from the repository root:  bash AI-internal/reconnaissance/run_ewars_reference.sh
#
# This is reconnaissance, not an analysis node. The number it produces establishes that the
# criterion is attainable and what it costs; the *reported* reference score is produced
# inside the claim tree, from a node, once the tree exists.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHAP="$ROOT/environment/chapenv/bin/chap"
PY="$ROOT/environment/chapenv/bin/python"
OUT="$ROOT/AI-generated/method-reconnaissance"
WORK="$OUT/ewars-work"
DEV="$ROOT/analysis/01_data/01_partition/results/development_1998-01_2009-12.csv"

# The reference, pinned by image digest. The image carries
# org.opencontainers.image.revision = a4c2fa423d7030e6eb7c1031b066e147bbc5aaa5, which is the
# repository commit it was built from, so the digest pins bytes and commit at once. A
# floating :latest would make the headline comparison depend on another project's build
# schedule -- the objection the plan's §3 makes against a hosted Chap service, applied to
# the reference model.
IMAGE="ghcr.io/chap-models/chapkit_ewars_model@sha256:abd8098f2b828d3ef9899ed136d20a4f5387f8c3abe901f386905cec166d823a"
CONTAINER="ewars-ref"
PORT=8000

# The backtest scheme fixed in batch 3 and not moved again.
N_PERIODS=3
N_SPLITS=8
STRIDE=3
N_RETRAIN=1

mkdir -p "$OUT" "$WORK"
export PYTHONWARNINGS=ignore
export COLUMNS=110

cleanup() { docker rm -f "$CONTAINER" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "== the reference model, pinned =="
docker image inspect "$IMAGE" --format '{{json .Config.Labels}}' > "$WORK/image_labels.json" 2>/dev/null \
  || docker pull --platform linux/amd64 "$IMAGE"
docker image inspect "$IMAGE" \
  --format '{{.Id}} {{.Architecture}}/{{.Os}} {{.Size}} {{index .Config.Labels "org.opencontainers.image.revision"}}' \
  > "$OUT/ewars_image_pin.txt"
echo "$IMAGE" >> "$OUT/ewars_image_pin.txt"
docker image inspect "$IMAGE" --format '{{json .Config.Labels}}' > "$OUT/ewars_image_labels.json"

echo "== starting the service (amd64 under emulation on this machine) =="
cleanup
docker run -d --name "$CONTAINER" --platform linux/amd64 -p "$PORT:8000" "$IMAGE" > "$WORK/container_id.txt"
for _ in $(seq 1 60); do
  if curl -sf --max-time 5 "http://localhost:$PORT/health" > "$WORK/health.json" 2>/dev/null; then break; fi
  sleep 2
done
curl -sf --max-time 20 "http://localhost:$PORT/api/v1/info" > "$OUT/ewars_service_info.json"
curl -sf --max-time 20 "http://localhost:$PORT/api/v1/configs/\$schema" > "$OUT/ewars_config_schema.json"

echo "== chap eval: the reference on the development dataset, at the fixed scheme =="
START=$(date +%s)
CHAP_RUNS_DIR="$WORK/runs" "$CHAP" eval \
    --model-name "http://localhost:$PORT" \
    --run-config.is-chapkit-model \
    --dataset-csv "$DEV" \
    --output-file "$OUT/ewars_development_eval.nc" \
    --backtest-params.n-periods "$N_PERIODS" \
    --backtest-params.n-splits "$N_SPLITS" \
    --backtest-params.stride "$STRIDE" \
    --backtest-params.n-retrain "$N_RETRAIN" \
    > "$OUT/ewars_development_eval.log" 2>&1
END=$(date +%s)

# The cost figure batch 5's budget needs, written to a file rather than read off a clock.
cat > "$OUT/ewars_run_cost.json" <<JSON
{
  "model": "chapkit_ewars_model",
  "image": "$IMAGE",
  "host_platform": "$(uname -m) $(uname -s)",
  "emulated": true,
  "dataset": "development_1998-01_2009-12.csv",
  "n_periods": $N_PERIODS,
  "n_splits": $N_SPLITS,
  "stride": $STRIDE,
  "n_retrain": $N_RETRAIN,
  "wall_clock_seconds": $((END - START)),
  "seconds_per_split": $(python3 -c "print(round(($END-$START)/$N_SPLITS,1))")
}
JSON

echo "== the regions Chap dropped, from the run's own log =="
grep -E "Rejected regions|not used by the model" "$OUT/ewars_development_eval.log" \
  > "$OUT/ewars_dataset_warnings.txt" || true

echo "== chap export-metrics (the platform's own aggregate) =="
"$CHAP" export-metrics \
    --input-files "$OUT/ewars_development_eval.nc" \
    --output-file "$OUT/ewars_metrics_aggregate.csv" \
    >> "$OUT/ewars_development_eval.log" 2>&1

echo "== scoring at every resolution the project reports on =="
"$PY" "$ROOT/AI-internal/reconnaissance/score_evaluation.py" \
    --evaluation "$OUT/ewars_development_eval.nc" \
    --out-dir "$OUT" \
    --prefix ewars_development

echo "done -> $OUT"
