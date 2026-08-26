#!/usr/bin/env bash
# Rule 6, verified rather than asserted: run each of our models twice and compare.
#
# Both baselines claim to contain no randomness at all -- their predictive distributions
# are empirical quantile functions evaluated at fixed levels, not samples from them -- so
# the claim to check is that there is nothing to seed, and the check is that two
# independent runs produce identical files. A model that failed this would need a seed,
# and the failure would be silent without a check like this one.
#
# The combination mechanism makes this cheap: each run is an ordinary run of the same
# nodes under a scratch COMBO, so the check exercises the same code path the reported
# analysis uses rather than a copy of it. The scratch results are removed afterwards --
# they are evidence about the method, not analysis results, which is also why this script
# lives in AI-internal/ beside check_invariants.py rather than in the tree.
#
# The evaluation `.nc` is excluded from the comparison and that is not a loophole: batch 2
# established that chap-core stamps `created_date` into it and serialises two set-valued
# attributes in run-dependent order, so two identical runs differ in those bytes while
# nothing numeric moves. Everything computed *from* the file is compared, and that is what
# the project reports from.
#
# Run from the repository root:
#   bash AI-internal/useful-scripts/verify_model_determinism.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/AI-generated/determinism-checks"
mkdir -p "$OUT"

MODELS=(
  "persistence:analysis/03_models/01_baselines/01_persistence"
  "climatology:analysis/03_models/01_baselines/02_climatology"
)

RESULTS=""
STATUS=identical

for entry in "${MODELS[@]}"; do
  name="${entry%%:*}"
  node="${entry#*:}"
  differing=""

  for run in 1 2; do
    combo="determinism_${name}_${run}"
    COMBO="$combo" bash "$ROOT/analysis/02_setup/run.sh" > /dev/null
    COMBO="$combo" bash "$ROOT/$node/run.sh" > /dev/null
    COMBO="$combo" bash "$ROOT/analysis/04_score/01_collect/run.sh" > /dev/null
  done

  a="$ROOT/analysis/04_score/01_collect/results/determinism_${name}_1"
  b="$ROOT/analysis/04_score/01_collect/results/determinism_${name}_2"
  for file in metrics_cell.csv models.csv; do
    cmp -s "$a/$file" "$b/$file" || { differing="$differing $file"; STATUS=differs; }
  done

  # The fitted model too: it is what the forecasts' spread comes from.
  fa=$(find "$ROOT/$node" -path "*/results/determinism_${name}_1/fitted_model.json")
  fb=$(find "$ROOT/$node" -path "*/results/determinism_${name}_2/fitted_model.json")
  cmp -s "$fa" "$fb" || { differing="$differing fitted_model.json"; STATUS=differs; }

  RESULTS="$RESULTS
  {\"model\": \"$name\", \"node\": \"$node\", \"identical\": $([ -z "$differing" ] && echo true || echo false),
   \"files_compared\": [\"metrics_cell.csv\", \"models.csv\", \"fitted_model.json\"],
   \"differing_files\": \"$(echo $differing)\"},"

  # The scratch combinations are removed: they are not analysis results.
  rm -rf "$ROOT/analysis/04_score/01_collect/results/determinism_${name}_"[12]
  find "$ROOT/analysis" -type d -name "determinism_${name}_[12]" -exec rm -rf {} + 2>/dev/null || true
done

cat > "$OUT/model_determinism.json" <<JSON
{
 "checked": "$(date +%Y-%m-%d)",
 "status": "$STATUS",
 "excluded_from_comparison": "eval.nc -- chap-core stamps created_date into it and serialises two set-valued attributes in run-dependent order (batch 2). Everything computed from it is compared.",
 "project_seed": 20260822,
 "models": [$(echo "$RESULTS" | sed '$ s/,$//')
 ]
}
JSON

echo "determinism: $STATUS -> $OUT/model_determinism.json"
