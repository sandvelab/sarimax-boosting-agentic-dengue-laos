result: results/predictability.csv · results/predictability.json
script: scripts/02_predictability.py
        sha256:a49453c61df0368ef69199c22d0a45035b91441a04e806833e3f3463f53b5856
        ../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../scripts/lib/project_seed.py
        sha256:8cf8c777a92e0d43663854423c4a6854675ea150613d42b5d08f69de14b18a5b
invocation: ../../environment/env/bin/python scripts/02_predictability.py
inputs: results/test_cells.csv  sha256:017b69726c347172db2c64d712d0744f6a2183c3108a1de2bed73bc1373ae33c
         (this node's own output from 01_error_structure.py; nothing is read from the terminal)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: project 20260920; component seed 3209744922 = component_seed("05_residualStructure"),
        used for RandomForestRegressor, GradientBoostingRegressor (subsample < 1) and the
        numpy Generator that permutes the target (30 permutations per configuration). Verified
        per /seed by a full second run diffed byte for byte against the first
        (predictability.csv and predictability.json) -- see the batch report for the outcome.
commit: 35a28f9
instructions-commit: 595c32d
node: analysis/05_residualStructure
produced: 2026-09-20
design: leave-one-split-out cross-validation over the 8 backtest splits on the 371 scored
        test cells; target z = error/se winsorised at +/-3; 14 feature sets x 4 families = 56
        configurations; "chance" made concrete as the 95th percentile of the same model's skill
        on a permuted target. Skill is reported on the winsorised target (what was fit), on the
        raw z, and -- the objective -- as mean CRPS in case units after adding zhat*se to stage
        1's mean, with 90% coverage and the negative-mean share.
what this is not: a candidate's score. It trains on later splits' errors to predict earlier
        ones, so it is exploratory; its role is to say which features and families deserve a
        leakage-safe candidate, and how large a gain to expect. Logged in the plan's §4b.
alternatives-considered:
  - Fitting the raw z rather than the winsorised z: rejected after the first error-structure
    run showed |z| up to 164 from the 2008-09 reporting-regime breaks; a least-squares fit to
    that target is a fit to five cells.
  - Standardising the error by the province's in-sample residual scale instead of stage 1's
    predictive se: the se is what the correction is multiplied back by, so z = error/se keeps
    the fit and the correction on one scale; the residual-scale version is available in
    test_cells.csv (`scale`) for a later perturbation.
  - More permutations (100+) for a tighter chance threshold: 30 was chosen to keep the run
    near 15 minutes; the threshold's role is a sanity bound, not a hypothesis test.
  - A single hold-out year instead of leave-one-split-out: eight folds use all 371 cells and
    match the backtest's own structure.
agency: agent-autonomous
information: agent-retrieved -- the permutation-based chance reference and the
        stacking-style out-of-fold design follow the literature retrieved this batch (Wolpert
        1992; Breiman 1996; Firmino et al. 2014), cited in the batch report.
