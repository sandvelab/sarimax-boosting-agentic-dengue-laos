result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/01_stage2_pooled_random_forest.py
        sha256:2d5256d4a51ff4155d464e01da8bc7901756225a4b51f0a93cbc4f981bcdaeb8
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/project_seed.py
        sha256:8cf8c777a92e0d43663854423c4a6854675ea150613d42b5d08f69de14b18a5b
        ../../scripts/lib/stage1_model.py
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
invocation: ../../../environment/env/bin/python scripts/01_stage2_pooled_random_forest.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (verification reference, not a value the score is carried from -- see "verification" below)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: project 20260920; component seed 1366484878 = component_seed("04_stage2/e_pooledRandomForest").
        This is real randomness (RandomForestRegressor's bootstrap resampling and per-split
        feature subsampling, unlike b_gradientBoosting's no-real-randomness configuration),
        pinned via random_state and n_jobs=1. Verified per /seed by running the script twice
        end to end and diffing results/per_cell_scores.csv and results/conclusion.json byte
        for byte -- identical both times (recorded in this batch's commit message,
        `db3369e`). Not re-run automatically inside the script itself: a fixed seed already
        guarantees this deterministically, and doubling every future invocation's cost to
        re-demonstrate a property already proven once is not this project's convention (contrast
        b_gradientBoosting, which embeds a lightweight in-script check because its own claim --
        no real randomness regardless of seed -- needed checking on every run to keep holding
        as that script's `GBM_PARAMS` might change; this one's claim is that the seed
        reproduces, which does not need re-demonstrating at each run once verified).
verification: this script re-derives stage 1's forecast (lib/stage1_model.py) per province per
        split, exactly as every stage-2 sibling does, and compares its re-derived (mean, se)
        against 02_stage1's stored per_cell_scores.csv cell for cell before trusting the
        residuals: 408/408 cells verified, max|Δmean|=0.0, max|Δse|=0.0 (bit-identical),
        recorded in results/conclusion.json.
commit: db3369e
instructions-commit: 595c32d
node: analysis/04_stage2/e_pooledRandomForest
produced: 2026-09-20
alternatives-considered: this is an adaptation of an externally sourced model
        (chap-models/rwanda_random_forest), and the deviations from its original design are
        the alternatives that matter here, all logged in the script's own module docstring
        rather than repeated in full here: (1) input set -- d_linearClimate's lag-12
        residual/calendar/climate features, not the original repo's lag-1..3 climate and
        lag-1..3 target features, rejected as leakage-unsafe for this project's 3-month test
        window; (2) no population/log1p incidence transform -- this project's stage-2 contract
        predicts a residual, not a raw count, so the original repo's malaria-incidence-rate
        framing does not apply; (3) a fixed, modest hyperparameter configuration
        (n_estimators=200, max_depth=5, min_samples_leaf=5, max_features="sqrt") rather than
        the original repo's RandomizedSearchCV (60 iterations, trees up to 1000, depth up to
        40) -- rejected as expensive and risky to reproducibility inside an 8-split backtest,
        in the same spirit b_gradientBoosting's own shallow/conservative defaults were chosen
        over a search. What was kept: the pooled-fit idea itself (one shared model across all
        provinces per split), which is this candidate's actual contribution to the tree.
agency: agent-autonomous (all three deviations above, and the choice of rwanda_random_forest
        among the chap-models repos inspected); the decision to try a chap-models model at all,
        and to keep exploring stage-2 candidates rather than move to phase D, is human-set
        (plan §4b, this batch).
information: agent-retrieved (chap-models org repo listing and rwanda_random_forest's
        train.py/README fetched via `gh api` and read directly, not recalled from training
        data); human-pointed (the human named the `github.com/chap-models` org as the source
        to draw from).
