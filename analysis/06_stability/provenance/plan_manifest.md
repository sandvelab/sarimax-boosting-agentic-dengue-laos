result: results/manifest.csv · results/manifest_summary.json · results/manifest_freeze.json
script: scripts/02_plan_manifest.py
        sha256:52cd84a81e1fe998abe8d4979426db8893d96da2463a0bb553707893e9c8ca8d
invocation: ../../environment/env/bin/python scripts/02_plan_manifest.py
inputs: results/run_costs.csv  sha256:820035470974fd98e55b8099e2da4df04b3d203ee9a78cd1eeeeb2aee68487bc
         (this node's own output from 01_measure_run_costs.py -- every est_cost_s in the
         manifest derives from it)
         the tree itself: every analysis/**/claim.md with `kind: alternatives`, read for its
         main-path and children to derive the tier-1 rows (at planning time: analysis/04_stage2,
         main path g_oosErrorBoosting, six not-taken siblings)
         git HEAD at run time, recorded as frozen_at_commit
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: 62d16bf  (the script as it ran for the committed result; 5477c02's version ran once
        before a comment was reworded for the crossing heuristic and produced a byte-identical
        manifest.csv -- sha256 ba01a061… both times; only frozen_at_commit moved)
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-21
freeze: results/manifest_freeze.json records manifest.csv's sha256
        (ba01a061bfbe0a4f3e636d4a747b2a3bffe8d2cd1f673342af790fb2bdc9340b), 40 rows, frozen at
        62d16bf on 2026-09-21. A later change to the development manifest is a recorded
        decision in the plan's §4b, not an edit.
alternatives-considered:
  - Making every tier-2 perturbation an alternatives node instead of a manifest row (AGENTS.md
    §4 prefers nodes): rejected for the 29 parametric rows on cost -- each node costs a
    scaffold, a contract check and a provenance record, and most rows change one constant.
    The combination-runner design (results/<combination>/ inside this node, as the invariant
    checker's `combos` check expects) keeps every path recorded and runnable at a fraction of
    that cost. Where a perturbation turns out to matter, promoting it to a node is the right
    follow-up.
  - A budget set by the human before costing: plan §4 left it to phase D; the measured costs
    (87 s for the whole tree) make any plausible budget non-binding, so a provisional one-hour
    ceiling was set and flagged for revision rather than blocking on a question whose answer
    cannot change what is run.
  - Ranking by cost alone or by alphabetical order: rejected -- AGENTS.md §6 asks for a rank by
    expected informativeness with the cut recorded; the rank and its reason are columns in the
    manifest so the ordering is on record before any result is.
  - Running the tier-2 rows in this batch, since they are cheap: rejected -- the runner must
    first be verified against the main path's stored per-cell scores, and the plan's §3 wants
    the set frozen before it is run, so that what is reported is a measurement, not a
    selection. Batch 12 runs; batch 13 reports.
  - Including the tier-3 rows as planned work: rejected -- each needs machinery not built
    (a verified metric extension, a combination design, a data acquisition) or reopens a
    plan §4 decision; they are listed with reasons so the line is visible.
agency: agent-autonomous (the enumeration, ranking, budget and freeze); the tier-3
        predictive-family fork is flagged for the human's decision.
information: agent-retrieved -- Chap's evaluate defaults (n_periods 3, n_splits 7, stride 1)
        for the `scheme=chap_default_7x1` row were read from chap-core's
        cli_endpoints/evaluate.py via the GitHub API on 2026-09-21; Ben Taieb & Hyndman (2014)
        and Wang et al. (2013), cited in two rows' bases, come from batch 10's literature
        search (batch report b10).
