result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/persistence_backtest.py
        sha256:3cf5d6f99505e9e802348f462d98d145a223c1bab1bc829dd1b236b09b621e92
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/persistence_backtest.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
environment: environment/ (project main)
         lock.txt sha256:1d10c3af0cce41440634defbe5b77b0fa30243333df2fd9493015ba2e197278a
seeds: none — persistence is a deterministic transcription of the training window's last
        observed value; no fitting, no randomness anywhere in the computation.
commit: (pending — this batch's After commit for 01_persistence)
instructions-commit: 595c32d
node: analysis/03_baselines/01_persistence
produced: 2026-09-20
alternatives-considered: CRPS needs a distributional forecast and persistence has none
  natively (plan requires every model scored the same Gaussian way, `crps.py`). Considered:
  (1) a fixed, arbitrary sigma across all cells — rejected as a free parameter with no basis
  in the data; (2) sigma from the province's full-history variance — rejected because it
  would leak information beyond what a persistence forecaster observes at that split's
  training cutoff; (3) sigma as the standard deviation of the training window's own one-step
  differences (`value[t] - value[t-1]`), i.e. the actual historical spread of persistence's
  own error, computed fresh per province per split from data available at that point — this
  is what the script does. A province/split with fewer than two training observations falls
  back to a floor of 1e-6 (matching stage 1's sigma floor) rather than an undefined std.
agency: agent-autonomous

---
section appended 2026-09-23 (batch 20, at the outsider test's finding) — **the environment
changed after this record was written, and the record had not caught up.**

environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
         changed at fa71b3b (batch 5, 2026-09-20): scikit-learn 1.9.1 and its dependencies added
         for the tree-based stage-2 candidate; every package this node's scripts import is at the
         same version in both lockfiles. The section above names the batch-2 lockfile
         (sha256:1d10c3af…), which is the one this result was produced under.
re-run: not re-run at fa71b3b. The result was reproduced byte for byte under the current lockfile
         by the clean-room run of 2026-09-22 (a fresh clone, the environment built from
         lock.txt; `AI-generated/validation/2026-09-22_cleanroom-artefacts/`), and again by the
         release-time run of 2026-09-23.
why-it-was-missed: `/validate invariants`' hashes check verified the digests in `script:` blocks
         and not the lockfile digest in the `environment:` block; it now verifies both (batch 20).
agency: agent-autonomous.
