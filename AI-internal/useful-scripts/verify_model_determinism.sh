#!/usr/bin/env bash
# Rule 6, verified rather than asserted: run each of our models twice and compare.
#
# Two different claims are checked here, and the check is the same for both.
#
# Both baselines claim to contain no randomness at all -- their predictive distributions
# are empirical quantile functions evaluated at fixed levels, not samples from them -- so
# the claim to check is that there is nothing to seed, and the check is that two
# independent runs produce identical files. A model that failed this would need a seed,
# and the failure would be silent without a check like this one.
#
# The candidate does draw: from a Laplace posterior, from a prior on the province-year
# effect, and from the negative binomial on top of both. Its claim is that every one of
# those draws comes from a single generator seeded with a component seed derived from the
# project seed, so that two runs are identical anyway. That is the claim Rule 6 is
# actually about, and it fails silently in exactly one way -- a second generator
# somewhere, seeded from system entropy -- which two runs and a diff will catch.
#
# The combination mechanism makes this cheap: each run is an ordinary run of the same
# nodes under a scratch COMBO, so the check exercises the same code path the reported
# analysis uses rather than a copy of it. The scratch results are removed afterwards --
# they are evidence about the method, not analysis results, which is also why this script
# lives in AI-internal/ beside check_invariants.py rather than in the tree.
#
# ## Both passes run under ONE combination name, and that is what makes the check work
#
# Until 2026-08-27 the two passes ran under `determinism_<model>_1` and `_2`. Batch 9 then
# added a `scored_under_combo` column to `models.csv` -- the column that makes COMBO_BASE
# inheritance visible on the face of the file, and a good addition. From that commit the
# check compared, among other things, a field whose value *is* the pass's own scratch
# name, so it reported `differs` on every model on every run whatever the models did:
# a Rule 6 instrument stuck on red, which verifies nothing.
#
# The repair is not to stop comparing that column. It is to remove the difference at its
# source: both passes run under the same combination, pass 1's outputs are copied aside,
# pass 2 overwrites them, and the copy is compared with what replaced it. Nothing is
# excluded that was compared before, and a genuine difference in any of the three files
# still fails the check.
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

# Every candidate is named by **its own** node path, never by the family node above it.
# `03_candidate` is an alternatives node: it routes to whichever child is on the main
# path, so naming a candidate by it would run whatever the main path happens to be and
# report the answer under the name of a model that did not run. Batch 10 hit the near
# miss and named candidate 2 by its own path; batch 11 promoted the family fork, which
# would have turned `hier_nb:analysis/03_models/03_candidate` into a check of the
# ensemble reported as `hier_nb`. All three now name themselves.
#
# Batch 22 applies the same rule to the two baselines, which had been named by their fork
# nodes because each fork had one built child. Both now have two, and a fork node routes
# to whichever is on the main path -- so `persistence:.../01_persistence` would have
# checked one construction, called it `persistence`, and left the other unchecked. Every
# model in this project is now named by the leaf that holds its contract directory.
#
# The list has been edited three times for one reason, which is the argument for
# discovering the leaves instead. What stops that here is naming: the leaves of a fork
# hold models that score under the *same* name on the leaderboard -- both persistence
# constructions write `persistence` -- so a discovered list needs a rule for naming the
# check that the check does not currently have. Left explicit, and said out loud.
MODELS=(
  "persistence:analysis/03_models/01_baselines/01_persistence/a_empiricalChange"
  "persistence_negBinomialFloor:analysis/03_models/01_baselines/01_persistence/b_negBinomialFloor"
  "climatology:analysis/03_models/01_baselines/02_climatology/a_expandingWindow"
  "climatology_frozenWindow:analysis/03_models/01_baselines/02_climatology/b_frozenWindow"
  "hier_nb:analysis/03_models/03_candidate/a_hierNB"
  "boosted:analysis/03_models/03_candidate/b_boosted"
  "ensemble:analysis/03_models/03_candidate/c_ensemble"
)

# The seed is a project setting and is declared in one place. Read, not copied: a second
# copy of it in this file could disagree with the one the models are seeded from, and the
# report would then name a seed nothing used.
PROJECT_SEED="$("$ROOT/.venv/bin/python" -c "
import sys; sys.path.insert(0, '$ROOT/analysis/scripts/lib')
from pathlib import Path
from project_seed import project_seed
print(project_seed(Path('$ROOT')))")"

RESULTS=""
STATUS=identical

KEEP="$(mktemp -d)"
trap 'rm -rf "$KEEP"' EXIT

for entry in "${MODELS[@]}"; do
  name="${entry%%:*}"
  node="${entry#*:}"
  differing=""
  combo="determinism_${name}"
  collected="$ROOT/analysis/04_score/01_collect/results/$combo"

  # Pass 1, under `$combo`. Its outputs are copied aside, because pass 2 runs under the
  # same name and overwrites them -- which is the point: see the note above.
  COMBO="$combo" bash "$ROOT/analysis/02_setup/run.sh" > /dev/null
  COMBO="$combo" bash "$ROOT/$node/run.sh" > /dev/null
  COMBO="$combo" bash "$ROOT/analysis/04_score/01_collect/run.sh" > /dev/null

  mkdir -p "$KEEP/$name"
  cp "$collected/metrics_cell.csv" "$collected/models.csv" "$KEEP/$name/"
  fitted=$(find "$ROOT/$node" -path "*/results/$combo/fitted_model.json")
  cp "$fitted" "$KEEP/$name/fitted_model.json"

  # Pass 2, under the same name, overwriting pass 1 in place.
  COMBO="$combo" bash "$ROOT/analysis/02_setup/run.sh" > /dev/null
  COMBO="$combo" bash "$ROOT/$node/run.sh" > /dev/null
  COMBO="$combo" bash "$ROOT/analysis/04_score/01_collect/run.sh" > /dev/null

  for file in metrics_cell.csv models.csv; do
    cmp -s "$KEEP/$name/$file" "$collected/$file" \
      || { differing="$differing $file"; STATUS=differs; }
  done

  # The fitted model too: it is what the forecasts' spread comes from.
  fitted=$(find "$ROOT/$node" -path "*/results/$combo/fitted_model.json")
  cmp -s "$KEEP/$name/fitted_model.json" "$fitted" \
    || { differing="$differing fitted_model.json"; STATUS=differs; }

  RESULTS="$RESULTS
  {\"model\": \"$name\", \"node\": \"$node\", \"identical\": $([ -z "$differing" ] && echo true || echo false),
   \"files_compared\": [\"metrics_cell.csv\", \"models.csv\", \"fitted_model.json\"],
   \"differing_files\": \"$(echo $differing)\"},"

  # The scratch combination is removed: it is not an analysis result.
  rm -rf "$collected"
  find "$ROOT/analysis" -type d -name "$combo" -exec rm -rf {} + 2>/dev/null || true
done

cat > "$OUT/model_determinism.json" <<JSON
{
 "checked": "$(date +%Y-%m-%d)",
 "status": "$STATUS",
 "excluded_from_comparison": "eval.nc -- chap-core stamps created_date into it and serialises two set-valued attributes in run-dependent order (batch 2). Everything computed from it is compared.",
 "project_seed": $PROJECT_SEED,
 "models": [$(echo "$RESULTS" | sed '$ s/,$//')
 ]
}
JSON

echo "determinism: $STATUS -> $OUT/model_determinism.json"
