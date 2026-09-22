#!/usr/bin/env bash
# Main script for node: 03_baselines
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §8, Python), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/env/bin/python"

# Sub-analyses: every child runs, in order.
bash "01_persistence/run.sh"
bash "02_climatology/run.sh"

# Own scripts
"$PYTHON" "scripts/comparison.py"
