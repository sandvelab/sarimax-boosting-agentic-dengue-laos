#!/usr/bin/env bash
# Rule 6, verified rather than asserted: run the slice twice and compare bit for bit.
#
# The persistence baseline contains no randomness — its predictive distribution is the
# empirical quantile function evaluated at fixed levels, not a sample from it — so the
# claim to be checked is that there is nothing to seed, and the check is that two
# independent runs produce identical files.
#
# The evaluation `.nc` is excluded from the comparison and that is not a loophole:
# batch 2 established that chap-core stamps `created_date` into it and serialises
# `split_periods` and `org_units` from unordered sets, so two identical runs differ in
# those bytes while nothing numeric moves. Everything computed *from* the file is
# compared, which is what the project reports from.
#
# Run from the repository root:
#   bash AI-internal/vertical-slice/verify_determinism.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SLICE="$ROOT/AI-internal/vertical-slice"
OUT="$ROOT/AI-generated/vertical-slice"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

for run in 1 2; do
    SLICE_OUT="$TMP/run$run" bash "$SLICE/run_vertical_slice.sh" > "$TMP/run$run.log" 2>&1
done

STATUS=identical
DIFFERING=""
for file in $(cd "$TMP/run1/results/main" && ls *.csv); do
    if ! cmp -s "$TMP/run1/results/main/$file" "$TMP/run2/results/main/$file"; then
        STATUS=differs
        DIFFERING="$DIFFERING $file"
    fi
done
if ! cmp -s "$TMP/run1/persistence_fitted_model.json" "$TMP/run2/persistence_fitted_model.json"; then
    STATUS=differs
    DIFFERING="$DIFFERING persistence_fitted_model.json"
fi

cat > "$OUT/determinism_check.json" <<JSON
{
  "check": "two independent runs of run_vertical_slice.sh, compared byte for byte",
  "compared": "every file under results/main/, plus the fitted model",
  "excluded": "the evaluation .nc — chap-core stamps created_date and serialises two set-valued attributes in run-dependent order (batch 2); nothing numeric is in the excluded bytes",
  "randomness_in_the_model": "none — the predictive distribution is the empirical quantile function evaluated at fixed levels, not sampled from",
  "seeds": "none required; project seed 20260822 has no surface in this model",
  "files_compared": $(cd "$TMP/run1/results/main" && ls *.csv | wc -l | tr -d ' '),
  "result": "$STATUS",
  "differing_files": "${DIFFERING# }"
}
JSON

echo "determinism: $STATUS -> $OUT/determinism_check.json"
[ "$STATUS" = identical ]
