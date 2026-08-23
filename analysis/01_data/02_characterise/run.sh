#!/usr/bin/env bash
# Main script for node: 02_characterise
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
"$PYTHON" "scripts/characterise_development.py"
"$PYTHON" "scripts/check_backtest_scheme.py"
"$PYTHON" "scripts/fig_cases_seasonality.py"
"$PYTHON" "scripts/fig_cases_timeline.py"
"$PYTHON" "scripts/fig_completeness.py"
"$PYTHON" "scripts/fig_covariate_lag_correlation.py"
"$PYTHON" "scripts/fig_province_burden.py"
