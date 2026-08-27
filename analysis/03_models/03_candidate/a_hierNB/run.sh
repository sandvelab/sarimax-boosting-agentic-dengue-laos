#!/usr/bin/env bash
# Main script for node: a_hierNB
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../../../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/chapenv/bin/python"

# Sub-analyses: every child runs, in order.
bash "01_observation/run.sh"
bash "02_covariates/run.sh"
bash "03_population/run.sh"
bash "04_fitTime/run.sh"

# Own scripts
"$PYTHON" "scripts/assemble_candidate_config.py"
"$PYTHON" "scripts/run_hier_nb.py"
