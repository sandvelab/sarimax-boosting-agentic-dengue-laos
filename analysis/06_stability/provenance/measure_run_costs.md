result: results/run_costs.csv · results/run_costs_summary.json
script: scripts/01_measure_run_costs.py
        sha256:4da436e894318e7445d6e6e119c79ce575894a850f93fa34238be599dd950b5c
invocation: ../../environment/env/bin/python scripts/01_measure_run_costs.py
inputs: the main scripts of the nodes it times, each run as `bash run.sh` in its own
        directory under the pinned environment: analysis/02_stage1 and every child of
        analysis/04_stage2 (a_linearLags … g_oosErrorBoosting), in that order. Each node's
        own provenance records name its scripts and inputs; this record does not repeat them.
        No data file is read directly by this script.
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn by this script; the seeded scripts it calls (e, g, and the diagnostics)
        pin their own component seeds.
commit: 5477c02
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-21
what it records: wall-clock seconds per node (total 86.8 s for 8 nodes), exit codes (all 0),
        and whether each node's results/ hashed identically before and after its re-run (all
        did) -- the whole-tree determinism check that falls out of timing by running.
alternatives-considered:
  - Estimating cost from batch 10's ad-hoc `time` observations instead of re-running: rejected
    -- a number read off a terminal has no provenance (AGENTS.md §1), and the re-run also
    delivers the determinism check.
  - Timing each script individually rather than each node's run.sh: run.sh is the unit the
    stability node calls for tier 1, so it is the cost that matters.
  - Repeating each run several times for a variance estimate: not worth it at these
    magnitudes (7-22 s); the budget decision does not turn on seconds.
agency: agent-autonomous
