#!/usr/bin/env bash
# Main script for node: 06_stability
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/env/bin/python"


# Own scripts
"$PYTHON" "scripts/01_measure_run_costs.py"
"$PYTHON" "scripts/02_plan_manifest.py"
"$PYTHON" "scripts/03_run_combinations.py"
"$PYTHON" "scripts/04_collect_conclusions.py"
"$PYTHON" "scripts/05_report_distribution.py"
# Phase E's machinery and its frozen set. 06 gates the holdout pipeline against this
# repository's stored development results; 07 freezes the set the held-out year is
# evaluated across, and on every later run verifies that set instead of rewriting it.
# Neither script reads a case value from the holdout file.
"$PYTHON" "scripts/06_verify_holdout_runner.py"
"$PYTHON" "scripts/07_plan_holdout_manifest.py"
