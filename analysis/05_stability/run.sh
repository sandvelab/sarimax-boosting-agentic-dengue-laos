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
# Freezes the phase-E set the first time and verifies it every time after, writing
# results/holdout_freeze_check.json and nothing else. It exits non-zero if the frozen set
# is one this tree can no longer reproduce, which stops the run before the holdout half
# below can be told it ran something it did not.
"$PYTHON" "scripts/freeze_holdout_manifest.py"

# Phase E. The frozen set, on the held-out year, and then the two datasets side by side.
# The driver is given the manifest it may not change. `run.sh` re-plans the development
# manifest above on every run, because the tree is what that manifest is derived from and
# `/validate invariants` requires the two to agree. It does *not* re-freeze the holdout
# one: batch 15 established that both came back byte-identical, and batch 18 established
# that this was a property of the tree not having changed rather than of anything
# enforcing it — one added fork child turned thirty-three frozen rows into thirty-four.
# Since batch 24 the frozen file is authoritative and the last step of the development
# half above verifies it instead of rebuilding it, so the set this runs is the one fixed
# before the year was opened rather than one this invocation decided.
#
# A row already recorded as run is not run again (plan §3). The seal takes two conditions
# and needs both: the row is recorded as `ran` in the versioned `run_status_holdout.csv`,
# and the gitignored `.holdout_opened`, at this node's root, says this tree is the one that
# opened the year. A clean checkout carries the first and not the second, so the whole set
# runs, which is what keeps `analysis/run.sh` a reproduction of phase E rather than a
# description of it. Batch 18's clean-room check found that the versioned condition alone
# had made it the description: every row was skipped and the outputs came back identical.
"$PYTHON" "scripts/run_manifest.py" --dataset holdout
"$PYTHON" "scripts/collect_conclusions.py" --dataset holdout
"$PYTHON" "scripts/compare_planned_cost.py" --dataset holdout
"$PYTHON" "scripts/report_distribution.py" --dataset holdout
"$PYTHON" "scripts/pair_holdout_development.py"
"$PYTHON" "scripts/holdout_fig_skill_distribution.py"
"$PYTHON" "scripts/holdout_fig_fork_sensitivity.py"
"$PYTHON" "scripts/fig_holdout_vs_development.py"
"$PYTHON" "scripts/fig_fork_sensitivity_both.py"

# The driver joined this list in batch 15, which is what makes `analysis/run.sh`
# reproduce the stability result as well as the reported one. It was held out of it from
# batch 12 to batch 14 because rows with no scripts and rows whose defects made them
# report the wrong thing would have been written into the tree every time anyone ran the
# analysis. Every row can now run, so the reason is gone.
#
# The cost of that: `analysis/run.sh` is about four hours rather than about twenty
# minutes, and most of it is the reference model's four unseeded repeats through an
# amd64 image under emulation. `readme-at-start.md` says so.
#
# Batch 16 added the phase-E half above, on the same argument: the holdout distribution
# is a reported result, and `run.sh` is what reproduces reported results. From cold it
# is about six hours.
