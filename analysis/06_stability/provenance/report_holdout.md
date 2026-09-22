result: results/conclusions_holdout.csv · results/distribution_holdout.json ·
        results/perturbation_effects_holdout.csv · results/province_stability_holdout.csv ·
        results/horizon_stability_holdout.csv · results/development_comparison_holdout.csv ·
        results/holdout_year_context.json
script: scripts/09_collect_holdout.py
        sha256:79f8447e3953eaf7dfdb89e70c288dc06d6de542ddcd259139a8d2ec00de5857
        scripts/10_report_holdout.py
        sha256:646e03434df2ca1ae79c5839d879e683edf41b28c212b3a74603861e5e3a0a64
        scripts/11_characterise_holdout_year.py
        sha256:872a01a2b4fba3e1400519f4ce944534d935e1d32a737df8f04eb68e85e710b2
invocation: ../../environment/env/bin/python scripts/09_collect_holdout.py
        ../../environment/env/bin/python scripts/10_report_holdout.py
        ../../environment/env/bin/python scripts/11_characterise_holdout_year.py
inputs: results/manifest_holdout.csv
         sha256:835bb52cab2e91cc630d420f59b07691cf8a7ddb0990e5079bfbba25d9080ab0
        results/holdout_freeze.json (the reporting rule is read from it at run time and copied
         into distribution_holdout.json, so the report can be checked against the rule rather
         than against a memory of it)
        results/$COMBO/conclusion.json and results/$COMBO/per_cell_scores.csv for the 33 rows
         that ran (written by 08_run_holdout.py)
        results/conclusions_v2.csv and results/distribution_v2.json (the development v2 measures
         every row is paired with)
        analysis/04_stage2/h_levelOnlyBoosting/results/per_cell_scores.csv (the development
         span 11_characterise_holdout_year.py describes the held-out year against)
environment: environment/ (project main)
        lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn. Nothing is recomputed from raw data; every number is read from a file
        another script wrote.
commit: 8eda4fd
instructions-commit: 8eda4fd
node: analysis/06_stability
produced: 2026-09-22
the-rule: frozen in batch 16, before the year was opened, and followed here without
        modification: the primary answer is plan §2's two bars on the main path; the required
        baselines are reported beside both stages on the same cells; the tier-2 rows are reported
        as a distribution and never as a best row, at the same two-percentage-point threshold as
        v1 and v2; every row is paired with its development counterpart; and nothing is added,
        dropped, re-tuned, re-run or promoted after a held-out number has been seen. Nothing was.
correction: 09_collect_holdout.py left every row that ran carrying the manifest's `planned`
        status instead of `run`, so its first table reported 0 rows run. Fixed and re-run before
        anything was read from it; no held-out number was produced, changed or reported by the
        faulty version, which wrote only status strings.
what-11-is-and-is-not: a description of the opened year -- its case load beside the development
        span's, per month and per province. It adds no row to the frozen set, re-tunes nothing
        and re-runs nothing. Without it the held-out CRPS figures cannot be read at all, since
        every model scores several times worse there than on development, and a reader could not
        tell whether the second stage helped because it is good or because there was an unusual
        amount left to correct. Written as its own result so it cannot be mistaken for part of
        the frozen comparison.
alternatives-considered:
  - Reporting the margin without characterising the year: rejected -- true and useless, for the
    reason above.
  - Adding rows to the set once the baseline result was seen (a stage 1 that might close the gap
    to climatology): rejected, and this is exactly what the frozen rule forbids. The gap is
    reported as the finding (claim C17) and what would have to change is recorded as not run.
  - Promoting a better-scoring held-out row: rejected. Three tier-2 rows beat the main path on
    the held-out year (no winsorisation -29.25%, the looser bound -28.72%, a higher learning rate
    -25.77%); none is promoted, because the holdout measures a pre-registered configuration and
    selecting on it would destroy the only unused data this project has.
agency: agent-autonomous (the collection, the report and the characterisation); the rule they
        follow was frozen in batch 16.
information: none retrieved; every input is a file already in this repository.
