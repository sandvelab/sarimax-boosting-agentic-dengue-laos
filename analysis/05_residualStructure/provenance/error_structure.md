result: results/test_cells.csv · results/error_structure.json · results/insample_residual_acf.csv
script: scripts/01_error_structure.py
        sha256:403b6f1ed4c9ad6875fcdb42bc893d8f11e15a349fb32981e796e719822c3a60
        ../scripts/lib/residual_features.py
        sha256:c6339fc4b5bc37e4c9102e64e76f56a5d57ea3de7ab9fe0aa1e20b6d66dbc513
        ../scripts/lib/stage1_model.py  (imported for its ORDER/SEASONAL_ORDER constants only)
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
        ../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../environment/env/bin/python scripts/01_error_structure.py
inputs: ../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (the stored test forecast is both the verification reference for the re-derived stage-1
         fit and the source of the out-of-sample errors this node characterises)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn -- this script is deterministic (SARIMAX maximum likelihood, closed-form
        statistics).
verification: stage 1 re-derived per province per split via lib/residual_features.fit_stage1
        (same specification and options as lib/stage1_model) and compared cell for cell with
        02_stage1's stored per_cell_scores.csv before any residual was used: 408/408 cells,
        max|Δmean| = 0.0, max|Δse| = 0.0 (results/error_structure.json,
        "verification_vs_stage1_stored_forecast"). The fixed-parameter in-window multi-step
        prediction (`get_prediction(dynamic=True)`) was checked once, outside the tree, against
        `apply(refit=False)` on the truncated series for one province and origin: means and
        standard errors identical to the printed precision. That check is not a result and is
        recorded here only so the mechanism this module relies on is not taken on faith.
commit: d13abac  (the script as it ran; be0e6e5 was the first version, superseded before its
        results were committed -- see "history" below)
instructions-commit: 595c32d
node: analysis/05_residualStructure
produced: 2026-09-20
history: be0e6e5 ran once and its outputs were inspected but not committed; the summaries were
        found to be dominated by a heavy tail (rms of z 11.6 with 83% coverage) and one
        province's variance owning the synchrony PCA. d13abac added tail-robust statistics
        (medians, 90th-percentile calibration factors, winsorised z, Spearman correlations,
        per-province row standardisation before the PCA), the recency check on in-window spread
        calibration, and the literature-motivated incidence features (inc_anom3, nat_inc_anom3,
        cum12_anom, cum36_anom, zero_frac24). The committed results are d13abac's.
alternatives-considered:
  - Characterising the in-sample one-step residual only (what every earlier stage-2 candidate
    trained on) rather than the out-of-sample h-step error: rejected as the central question is
    what a stage 2 must *correct*, which is the h-step error; both are reported so the
    difference between them is itself a result (the one-step residual is essentially white;
    the h-step errors are not).
  - A true rolling refit inside each training window for the in-window errors instead of
    fixed-parameter dynamic prediction: rejected on cost (17 provinces x 8 splits x ~100
    origins of SARIMAX fits) for a diagnostic; the fixed-parameter version is mildly optimistic
    and that is stated wherever it is used.
  - Moment-based spread statistics (rms of z) alone: kept but paired with quantile-based ones
    after the first run showed the tail makes the rms meaningless here.
  - Pearson correlation alone for feature screening: paired with Spearman and with the
    winsorised-z Pearson for the same reason.
  - Plots of the error distribution by horizon and month: not produced, because matplotlib is
    not in the pinned environment and adding it is a /pin-environment change this batch did
    not want to make for a diagnostic node; the plotted values would be test_cells.csv.
agency: agent-autonomous (what to characterise and how); the decision to run a diagnostic
        analysis before building further candidates is human-set (plan §4b, 2026-09-20).
information: agent-retrieved -- the choice of incidence features (recent-incidence anomaly,
        cumulative incidence as a susceptibility proxy, zero fraction as reporting level, the
        national mean) follows the dengue-forecasting literature retrieved by web search during
        this batch (Cousien et al. 2019; Cuong et al. 2013; Lauer et al. 2018; Areed et al.
        2025; Khampapongpane et al. 2014; van Panhuis et al. 2015; Kiang et al. 2021), cited in
        the batch report with what could and could not be verified.

---
section appended at commit d9d1fba (comment-only changes after the run; nothing re-run):
script: scripts/01_error_structure.py
        sha256:06e481d2afd4ce2f2dbd4ecb8b6e13b4b07d0558df40d6e650639f24ffb8f5b0
        (was 403b6f1e…: one line added, `SEED = None` with a comment saying the script draws
        no randomness, so the seeds invariant's text heuristic sees the statement it looks for)
        ../scripts/lib/residual_features.py
        sha256:cbe025691c5e58b415720849ca3e30964f24c96f921764d638a9ccd8149bec2c
        (was c6339fc4…: the comment on WARMUP_MONTHS reworded; the crossing heuristic read the
        old wording as a value transcribed from another step, which it is not)
The committed results are those of the d13abac run; no logic changed in either file.
