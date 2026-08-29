#!/usr/bin/env bash
# Main script for node: 05_stability
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/chapenv/bin/python"


# Own scripts -- in dependency order, not the alphabetical order `node.py rebuild`
# writes. Costs are measured before the manifest is planned from them; conclusions are
# collected after; and the planned-against-actual comparison reads the run record last.
"$PYTHON" "scripts/measure_step_costs.py"
"$PYTHON" "scripts/plan_manifest.py"
"$PYTHON" "scripts/collect_conclusions.py"
"$PYTHON" "scripts/compare_planned_cost.py"

# `scripts/run_manifest.py` -- the driver -- is deliberately NOT called here yet, and
# joins this list in batch 15. `node.py rebuild` will add it back every time it is run
# here; if it appears above, it has been re-added by accident and must come out again.
#
# Two of the manifest's children still have no scripts (batch 22) and fourteen candidate
# and family rows need two defects fixed before they mean what their row says (batch 14).
# Calling the driver from here today would put failed or misleading combinations into the
# tree every time anyone ran `analysis/run.sh`. Batch 15 adds the line below once every
# row can run, which is what makes `analysis/run.sh` reproduce the stability result as
# well as the main one.
#
#   "$PYTHON" "scripts/run_manifest.py"
