#!/usr/bin/env bash
# `/validate cleanroom`: build the environment from nothing in a fresh clone, run the whole
# analysis, and report differences against the archived results rather than announcing success.
#
# Why a clone and not this tree: the point is to find what only exists here. A path that is
# untracked, a file a script happens to find because a previous run left it, a digest that is
# true of the working copy and of nothing else — none of those show up in a re-run in place.
# Batch 19 found exactly that class of defect before this script existed: a fresh clone received
# `holdout.csv` with different bytes from the ones the phase-E freeze recorded, so the holdout
# runner would have refused to open it and phase E was not reproducible at all.
#
#   AI-internal/useful-scripts/cleanroom.sh            full run: clone, build, run, compare
#   SKIP_RUN=1 AI-internal/useful-scripts/cleanroom.sh clone, build and compare inputs only
#
# The clone, the built environment and the logs live under AI-internal/useful-scripts/repo/ and
# are gitignored; the findings are copied to AI-generated/validation/<date>_cleanroom-artefacts/,
# which is tracked.
#
# **Files that legitimately differ are declared, not discovered.** Wall-clock measurements,
# timestamps and the commit a build was made at are not results; comparing them would produce a
# failure on every run and train the reader to ignore the output. They are listed in VARYING
# below, reported separately, and everything else is compared byte for byte.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="$ROOT/AI-internal/useful-scripts/repo"
STAMP="$(date +%Y-%m-%d)"
ART="$ROOT/AI-generated/validation/${STAMP}_cleanroom-artefacts"
LOG="$ROOT/AI-internal/useful-scripts/cleanroom_console.log"

# Results whose content is a measurement of this machine or this moment, not of the analysis.
VARYING=(
  "analysis/06_stability/results/run_costs.csv"
  "analysis/06_stability/results/run_costs_summary.json"
  "analysis/06_stability/results/run_log.csv"
  "analysis/06_stability/results/run_log_v2.csv"
  "analysis/06_stability/results/run_log_holdout.csv"
  "analysis/06_stability/results/run_summary.json"
  "analysis/06_stability/results/run_summary_v2.json"
  "analysis/06_stability/results/run_summary_holdout.json"
  "analysis/06_stability/results/run_status_holdout.csv"
  "analysis/06_stability/results/manifest_freeze_check.json"
  "analysis/06_stability/results/holdout_freeze_check.json"
  "analysis/06_stability/results/holdout_runner_verification.json"
)

say() { echo "[cleanroom] $*" | tee -a "$LOG"; }

: > "$LOG"
mkdir -p "$ART"
say "root   $ROOT"
say "clone  $WORK"
say "date   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
say "HEAD   $(git -C "$ROOT" rev-parse --short HEAD)"

if [[ -n "$(git -C "$ROOT" status --porcelain)" ]]; then
  say "REFUSING: the working tree is dirty. A clean-room run must start from a commit, or it"
  say "          compares against results that are not the ones in the repository."
  exit 2
fi

say "--- clone ---"
rm -rf "$WORK"
git clone -q "$ROOT" "$WORK" || { say "clone failed"; exit 1; }
say "cloned at $(git -C "$WORK" rev-parse --short HEAD)"

# Before anything runs: do the checked-out bytes match the ones every digest was computed over?
say "--- inputs: clone vs. repository, byte for byte ---"
INPUT_DIFFS=0
while IFS= read -r f; do
  if ! cmp -s "$ROOT/$f" "$WORK/$f"; then
    say "DIFFERS ON CHECKOUT: $f"
    INPUT_DIFFS=$((INPUT_DIFFS + 1))
  fi
done < <(git -C "$ROOT" ls-files 'analysis/**/*.csv' 'analysis/**/*.json')
say "$INPUT_DIFFS tracked input file(s) differ before anything ran"

say "--- build the environment from nothing ---"
if ! (cd "$WORK" && bash environment/install-env.sh) >>"$LOG" 2>&1; then
  say "environment build FAILED — see $LOG"
  exit 1
fi
say "environment built"
(cd "$WORK" && python3 -m venv .venv && .venv/bin/pip -q install --upgrade pip) >>"$LOG" 2>&1
say "machinery .venv built"

if [[ "${SKIP_RUN:-}" == "1" ]]; then
  say "SKIP_RUN=1 — stopping before analysis/run.sh"
else
  say "--- run the whole analysis ---"
  START=$(date +%s)
  (cd "$WORK" && bash analysis/run.sh) >>"$LOG" 2>&1
  RUN_STATUS=$?
  say "analysis/run.sh exited $RUN_STATUS after $(( $(date +%s) - START ))s"
fi

say "--- compare results ---"
SAME=0; DIFF=0; MISSING=0; VARIED=0
DIFFLIST="$ART/differences.txt"
: > "$DIFFLIST"
is_varying() { local p="$1"; for v in "${VARYING[@]}"; do [[ "$p" == "$v" ]] && return 0; done; return 1; }

while IFS= read -r f; do
  case "$f" in analysis/*/results/*|analysis/results/*) ;; *) continue ;; esac
  if [[ ! -f "$WORK/$f" ]]; then
    echo "MISSING IN CLONE  $f" >> "$DIFFLIST"; MISSING=$((MISSING + 1)); continue
  fi
  if cmp -s "$ROOT/$f" "$WORK/$f"; then
    SAME=$((SAME + 1))
  elif is_varying "$f"; then
    echo "VARIES (declared)  $f" >> "$DIFFLIST"; VARIED=$((VARIED + 1))
  else
    echo "DIFFERS            $f" >> "$DIFFLIST"; DIFF=$((DIFF + 1))
  fi
done < <(git -C "$ROOT" ls-files)

say "identical $SAME · differing $DIFF · declared-varying $VARIED · missing in clone $MISSING"
say "differences listed in $DIFFLIST"

say "--- the clone's own invariants ---"
(cd "$WORK" && .venv/bin/python AI-internal/useful-scripts/check_invariants.py) 2>&1 | tee -a "$LOG" \
  | tee "$ART/clone_invariants.txt" | tail -20

cp "$LOG" "$ART/console.log" 2>/dev/null || true
{
  echo "{"
  echo "  \"date\": \"$STAMP\","
  echo "  \"head\": \"$(git -C "$ROOT" rev-parse --short HEAD)\","
  echo "  \"input_files_differing_on_checkout\": $INPUT_DIFFS,"
  echo "  \"results_identical\": $SAME,"
  echo "  \"results_differing\": $DIFF,"
  echo "  \"results_declared_varying\": $VARIED,"
  echo "  \"results_missing_in_clone\": $MISSING"
  echo "}"
} > "$ART/summary.json"
say "artefacts in $ART"
[[ $DIFF -eq 0 && $MISSING -eq 0 && $INPUT_DIFFS -eq 0 ]]
