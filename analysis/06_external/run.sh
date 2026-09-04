#!/usr/bin/env bash
# Main script for node: 06_external
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/chapenv/bin/python"


# Own scripts -- plan the set before running it, run it, then report it. The plan is
# committed before the run: `AGENTS.md` §6 asks for the cost of each unit, the ranking and
# where the line fell, and an estimate written after the clock has stopped is not an
# estimate.
"$PYTHON" "scripts/plan_external.py"
"$PYTHON" "scripts/run_external.py"
"$PYTHON" "scripts/report_external.py"
"$PYTHON" "scripts/fig_external_skill.py"
