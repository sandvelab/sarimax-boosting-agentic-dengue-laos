#!/usr/bin/env bash
# /validate cleanroom, batch 18.
#
# Build the environment from nothing, run analysis/run.sh, and report the differences.
# The comparison is git's: the clone's index is the archived result, so after the run
# `git status` and `git diff` in the clone are the difference report, with no second copy
# of the results to keep in step.
set -uo pipefail

CR="$(cd "$(dirname "$0")" && pwd)"
# The repository to clone: this script lives two levels inside it, so the path is
# derived rather than named. It was a constant naming one machine until batch 19, which
# meant the one harness a reader most wants to re-run only ran here. Found by the
# release scan.
SRC="$(cd "$CR/../.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

log() { echo "[$(date -u +%H:%M:%SZ)] $*"; }

log "=== re-cloning at the current HEAD ==="
rm -rf "$CR/repo"
git clone --quiet "$SRC" "$CR/repo"
cd "$CR/repo"
git rev-parse HEAD > "$CR/cleanroom_head.txt"
log "HEAD $(cat "$CR/cleanroom_head.txt")"

log "=== what the clean checkout carries before anything runs ==="
git ls-files | wc -l | sed 's/^/tracked files: /'
test -e analysis/05_stability/.holdout_opened \
  && log "MARKER PRESENT -- the seal would hold; the fix did not take" \
  || log "no .holdout_opened: the seal releases, phase E will run"

log "=== building the analysis environment from environment/lock.txt ==="
bash environment/install-chap.sh > "$CR/install_env.log" 2>&1
grep -E "^(matches|DOES NOT MATCH)" "$CR/install_env.log" || tail -5 "$CR/install_env.log"
environment/chapenv/bin/chap --version 2>/dev/null | tail -1 | sed 's/^/chap /'

log "=== analysis/run.sh, from cold ==="
START=$(date +%s)
bash analysis/run.sh > "$CR/run.log" 2>&1
STATUS=$?
END=$(date +%s)
log "analysis/run.sh exited $STATUS after $(( (END-START)/60 )) min"
echo "$STATUS" > "$CR/run_exit_status.txt"
echo "$(( END - START ))" > "$CR/run_seconds.txt"

log "=== the differences ==="
git status --porcelain > "$CR/diff_status.txt"
git diff --stat > "$CR/diff_stat.txt"
wc -l < "$CR/diff_status.txt" | sed 's/^/changed paths: /'
log "done"
