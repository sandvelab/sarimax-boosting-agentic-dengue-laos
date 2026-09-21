result: results/distribution.json · results/perturbation_effects.csv · results/province_stability.csv · results/horizon_stability.csv
script: scripts/05_report_distribution.py
        sha256:241ba5008d5276baf922879dccffb96c3094bbeff07bdc6fe66bd054048762fb
invocation: ../../environment/env/bin/python scripts/05_report_distribution.py
inputs: results/conclusions.csv  sha256:0ab568d113ef6c542ea26a988857648b1f1d2a180bc5cccafa098ab39f131b1d
         results/$COMBO/conclusion.json and results/$COMBO/per_cell_scores.csv for `main` and
         every tier-2 combination (this node's own outputs from 03_run_combinations.py; the
         per-province and per-horizon tables are read from them)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: eda4fbc
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-21
what it records: the distribution of the two-stage-vs-stage-1 margin over the 29 tier-2
        perturbations (quantiles, sign flips, coverage), grouped by judgment call (stage 1
        specification; window, scheme and data; stage-2 target and combination rule; features;
        family hyperparameters and seed; training-error construction); which rows move the
        margin's size by more than SENSITIVITY_POINTS = 2 percentage points from the main
        path's; per-province and per-horizon stability across main + 29 combinations; tier 1
        and tier 3 restated. Claims C1-C7 in Human-AI-collaboration/claims/claims.md are
        grounded in these files.
alternatives-considered:
  - A formal test (paired, across splits or cells) of each perturbation's margin: not done --
    eight splits and 371 correlated cells give no honest sampling distribution, and the
    question the stability node asks is about instability under reasonable alternative
    choices, not sampling noise (AGENTS.md §4); the distribution of margins is the answer.
  - A different "moves the size" threshold (1 or 3 points): 2 was chosen because every
    hyperparameter and seed row falls inside it and every stage-1 and error-construction row
    that changes the margin falls outside; the threshold is a column in the output, so a
    reader can re-cut.
  - Weighting rows by informativeness rank in the summary: rejected -- the rank was a plan for
    what to run, not a prior on what to believe; every run row counts once.
  - Plots of the margin distribution: not produced (no plotting library in the pinned
    environment; the plotted values would be perturbation_effects.csv).
agency: agent-autonomous
