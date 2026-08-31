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
# writes. The order is the phase's own: cost the pipeline, plan the set, run tier 1,
# read what it concluded, let the frozen rule pick tier 2 from that, run those, read the
# whole set, and report it.
#
# `plan_manifest.py` and `collect_conclusions.py` each appear twice, and that is what
# makes this node reproducible from nothing rather than from the results already on
# disk. Tier 2 is selected by `tier2_rule.md` from tier 1's conclusions, so on a cold
# run the first planning pass can only leave eight unresolved slots; the second pass,
# after tier 1 has run and been collected, fills them by the rule. Both passes are the
# same script and the same rule -- what differs is that the second has a tier 1 to read.
"$PYTHON" "scripts/measure_step_costs.py"
"$PYTHON" "scripts/plan_manifest.py"
"$PYTHON" "scripts/run_manifest.py" --tier 1
"$PYTHON" "scripts/collect_conclusions.py"
"$PYTHON" "scripts/plan_manifest.py"
"$PYTHON" "scripts/run_manifest.py" --tier 2
"$PYTHON" "scripts/collect_conclusions.py"
"$PYTHON" "scripts/compare_planned_cost.py"
"$PYTHON" "scripts/report_distribution.py"
"$PYTHON" "scripts/fig_skill_distribution.py"
"$PYTHON" "scripts/fig_fork_sensitivity.py"
"$PYTHON" "scripts/fig_pair_interaction.py"
"$PYTHON" "scripts/freeze_holdout_manifest.py"

# The driver joined this list in batch 15, which is what makes `analysis/run.sh`
# reproduce the stability result as well as the reported one. It was held out of it from
# batch 12 to batch 14 because rows with no scripts and rows whose defects made them
# report the wrong thing would have been written into the tree every time anyone ran the
# analysis. Every row can now run, so the reason is gone.
#
# The cost of that: `analysis/run.sh` is about four hours rather than about twenty
# minutes, and most of it is the reference model's four unseeded repeats through an
# amd64 image under emulation. `readme-at-start.md` says so.
