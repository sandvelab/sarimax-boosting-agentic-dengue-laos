# Provenance — the phase-D result

```
result:              results/distribution.json
                     results/distribution_rows.csv
                     results/sensitivity_by_fork.csv
script:              scripts/report_distribution.py
                     sha256:f5ad21823a0a6602715b429b4ae90f5ee40437fd2fbd795d2e7977dbaee83981
invocation:          "$PYTHON" scripts/report_distribution.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python. No COMBO: this node's outputs
                     describe every combination and belong to none.)
inputs:              analysis/05_stability/results/conclusions.csv
                     analysis/05_stability/results/forks.csv
                     analysis/05_stability/results/manifest_notes.json
                     analysis/05_stability/results/run_status.csv
                     analysis/results/main/conclusion.json
                     analysis/04_score/03_compare/results/main/paired_summary.csv
                     analysis/04_score/03_compare/results/main/comparison_notes.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every number is an arithmetic summary of stored scores;
                     project seed 20260822 has no surface here.
commit:              9ad6578
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** `/perturb report`: the distribution of conclusions over the
thirty-two analyses the frozen manifest named and ran, and the ranking of the seventeen
forks by how far the reported conclusion moves when each is taken differently. It is the
phase-D deliverable, and the plan calls the second half of it the most valuable single
output of this project.

**The reported skill score is +0.1485 and sits thirteenth of thirty-two**, in a distribution
running −0.0724 to +0.2320 with a median of +0.1469. Our model beats the reference on 27 of
the 32 and both required baselines on 27. The five rows where a required baseline wins are
exactly the five case-weighted ones; the five where the reference wins are the five that
replace our model or refit its weights. No choice about the data, the evaluation, the
scoring or the baselines takes our model below the reference on any row.

**The yardstick is measured, not chosen.** "Does the conclusion move" needs a scale, and
choosing one would be the kind of judgment call this node exists to expose. The reference
model is unseeded and was scored four times, and `03_compare` scores our model against each
repeat separately: those four skill scores span **0.0218**, which is how far the reported
conclusion moves when nothing changes but the reference's own sampler. It is the skill-space
twin of the 0.565 CRPS floor the project has quoted since batch 7 and comes from the same
four repeats. Both are read from files.

**Six of seventeen forks move the conclusion further than that band**: the model family
(0.2209), the pool's own weighting (0.1820), the weighting of the headline mean (0.0835),
the province filter (0.0376), the construction of the persistence baseline (0.0279) and the
training window (0.0219, which is the band itself to within 0.0001 and is reported as the
borderline case it is). **Eleven do not**, and nine of those eleven are the candidate-internal
forks phase C spent three batches selecting among.

**Mean CRPS is reported within a weighting and never across one.** A re-weighted mean is
over a different set of weights: 18.55–23.70 unweighted, 28.58 population-weighted,
88.48–112.26 case-weighted. Putting those on one axis would report a spread that is an
artefact of the unit. The skill score is a ratio and is comparable across all of them,
which is the reason `readme-at-start.md` gives for reporting a ratio in the first place.

alternatives-considered: **a fixed threshold for "moves the conclusion"** — rejected,
because a number chosen here would be a silent judgment call inside the node whose job is
to make judgment calls visible, and because the reference's own re-run spread is available
as a measurement. **The CRPS noise floor (0.565) as the yardstick instead** — rejected: it
is in CRPS and the conclusion is in skill, and the weighting fork makes CRPS
non-comparable across rows, so it could not have been applied to six of the thirty-two rows
at all. It is carried in `distribution.json` beside the band rather than dropped.
**Reporting quartiles of the skill distribution** — not done: with thirty-two rows drawn
from a manifest rather than from a population, a quartile invites reading the set as a
sample of something. Minimum, median and maximum are reported, and the per-row table is
beside them.

agency: agent-autonomous. The choice of yardstick and the decision to partition CRPS by
weighting are both the agent's, on this batch.
information: agent-retrieved — every value read from the files named above.

---

## The phase-E half (batch 16)

```
result:              results/holdout_distribution.json
                     results/holdout_distribution_rows.csv
                     results/holdout_sensitivity_by_fork.csv
script:              scripts/report_distribution.py
                     sha256:9ac25cf68345ed1d113fac700ab6b6f24832a6f8d554905b5cf0050911633675
invocation:          "$PYTHON" scripts/report_distribution.py --dataset holdout
                     (from 05_stability/, via run.sh)
inputs:              analysis/05_stability/results/holdout_conclusions.csv
                     analysis/05_stability/results/forks.csv
                     analysis/05_stability/results/holdout_freeze.json
                     analysis/05_stability/results/run_status_holdout.csv
                     analysis/results/main__holdout/conclusion.json
                     analysis/04_score/03_compare/results/main__holdout/paired_summary.csv
                     analysis/04_score/03_compare/results/main__holdout/comparison_notes.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every number is an arithmetic summary of stored scores.
commit:              609e1be
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: judge the holdout's forks against development's noise band, so the
                     two rankings are on one scale. Rejected: the band is a measurement of
                     the reference's own sampler on a given dataset, and importing it would
                     let one analysis decide what counts as a move in another. Each dataset
                     is judged against its own — 0.0218 on development, 0.0140 here.
agency:              agent-autonomous.
```

**What it establishes.** On the held-out year the distribution runs **−0.5038 to +0.2026**
around a reported **+0.0868**, which sits **eighteenth of thirty-two**. Our model beats the
reference on **26 of 32** and both required baselines on 27, against 27 and 27 on
development. The spread is **0.706 wide against development's 0.304** — more than twice —
and the five rows the reference wins are no longer the five that replace our model: four of
the six are rows that filter the provinces.

**Five of seventeen forks move the conclusion further than this dataset's noise band**, and
the ranking is not development's. The province filter goes from 0.0376 to **0.2696**, the
largest fork effect anywhere in the project; the family fork more than halves, to 0.0949;
the pool's own weighting fork, worth 0.1820 on development, falls to 0.0121 and below the
band. `covariates` — a candidate-internal fork worth 0.0081 on development — clears it here.
