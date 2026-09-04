#!/usr/bin/env bash
# Main script for node: analysis
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd ".." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/chapenv/bin/python"

# Sub-analyses: every child runs, in order.
bash "01_data/run.sh"
bash "02_setup/run.sh"
bash "03_models/run.sh"
bash "04_score/run.sh"
bash "05_stability/run.sh"
bash "06_external/run.sh"

# Own scripts
"$PYTHON" "scripts/conclude.py"
