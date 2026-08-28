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


# Own scripts
"$PYTHON" "scripts/measure_step_costs.py"
"$PYTHON" "scripts/plan_manifest.py"
"$PYTHON" "scripts/collect_conclusions.py"

# `scripts/run_manifest.py` -- the driver -- is deliberately NOT called here yet, and
# joins this list in batch 15.
#
# Nine of the manifest's children have no scripts, and twelve of the built ones need two
# defects fixed before they mean what their row says (manifest_notes.json, and batch 12's
# report §5). Calling the driver from here today would put a dozen failed or misleading
# combinations into the tree every time anyone ran `analysis/run.sh`. Batches 13, 22 and
# 14 run it with `--batch`, one part of the manifest each; batch 15 adds the line below
# once every row runs, which is what makes `analysis/run.sh` reproduce the stability
# result as well as the main one.
#
#   "$PYTHON" "scripts/run_manifest.py"

