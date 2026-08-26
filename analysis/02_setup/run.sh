#!/usr/bin/env bash
# Main script for node: 02_setup
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/chapenv/bin/python"

# Sub-analyses: every child runs, in order.
bash "01_population/run.sh"
bash "02_trainingWindow/run.sh"
bash "03_provinces/run.sh"
bash "04_retrain/run.sh"

# Own scripts
"$PYTHON" "scripts/assemble_setup.py"
