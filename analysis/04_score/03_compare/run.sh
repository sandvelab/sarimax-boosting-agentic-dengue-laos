#!/usr/bin/env bash
# Main script for node: 03_compare
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/chapenv/bin/python"


# Own scripts
"$PYTHON" "scripts/compare_models.py"
"$PYTHON" "scripts/fig_accuracy_and_spread.py"
"$PYTHON" "scripts/fig_crps_by_location.py"
"$PYTHON" "scripts/fig_paired_vs_reference.py"
