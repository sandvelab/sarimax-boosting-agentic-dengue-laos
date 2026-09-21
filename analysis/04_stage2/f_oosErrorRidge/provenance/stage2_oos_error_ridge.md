result: results/per_cell_scores.csv · results/conclusion.json · results/ridge_coefficients.csv
script: scripts/01_stage2_oos_error_ridge.py
        sha256:b0b641be7709456b2c2cab972b9ef25999bc2814b21f7e2e1f9fbb081dd291c8
        ../../scripts/lib/stage2_oos.py
        sha256:04dbf43aa5b4b4d7868859f7be35f15a6a4060a9f728b3a89a5fd7511cafcb41
        ../../scripts/lib/residual_features.py
        sha256:c6339fc4b5bc37e4c9102e64e76f56a5d57ea3de7ab9fe0aa1e20b6d66dbc513
        ../../scripts/lib/stage1_model.py  (specification constants only)
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/01_stage2_oos_error_ridge.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (verification reference only, as for every stage-2 sibling)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn -- ridge regression and SARIMAX maximum likelihood are deterministic.
verification: re-derived stage-1 forecast vs 02_stage1's stored per_cell_scores.csv: 408/408
        cells, max|Δmean| = 0.0, max|Δse| = 0.0 (results/conclusion.json).
commit: d8f9b07
instructions-commit: 595c32d
node: analysis/04_stage2/f_oosErrorRidge
produced: 2026-09-20
design (the judgment calls, each with its basis; the script's docstring carries the full
        argument):
  - target = stage 1's h-step forecast error inside the training window, parameters fixed,
    from every origin after the 24-month warm-up (`pseudo_oos_errors`), standardised by stage
    1's own predictive se and winsorised at +/-3 -- ~4,700-5,700 rows per split;
  - features = lib/stage2_oos.FEATURES (horizon and target-month indicators; log-compressed
    forecast level relative to the province's residual scale, a below-zero indicator and the
    level x horizon interaction; province log mean; last and last-three standardised residuals
    at the origin; their cross-province mean; trailing-12-month incidence anomaly; trailing-24
    zero fraction); no climate;
  - family = ridge, alpha 10 on standardised features (RIDGE_ALPHA), one pooled fit per split;
  - combination = stage 1 mean + zhat*se, zhat clipped to +/-3, result clipped at zero
    (CLIP_AT_ZERO); the unclipped mean is stored per cell so 02_compare_to_stage1.py can score
    the clip and the correction separately; sigma unchanged from stage 1.
alternatives-considered:
  - Training on the in-sample one-step residual, as candidates a-e did: rejected on
    05_residualStructure's finding that it is essentially white (results/error_structure.json,
    "insample_residual_acf_final_split") and on the stacking literature's warning against
    fitting a second level on in-sample fits.
  - A true rolling refit for the in-window errors: rejected on cost (see
    05_residualStructure/provenance/error_structure.md); the fixed-parameter errors are mildly
    optimistic, which is recorded rather than hidden.
  - Per-horizon separate models (Ben Taieb & Hyndman 2014's design literally): horizon enters
    as indicators plus a level x horizon interaction instead, to keep one pooled fit; a
    per-horizon version is a natural perturbation.
  - Including lag-1..3 climate anomalies: rejected -- 05_residualStructure found no usable
    correlation with the error (|Spearman| <= 0.05 for temperature and humidity, -0.04 for
    rainfall) and the literature finds climate adds little beyond incidence at 1-3 months
    (Johansson et al. 2016, 2019; Benedum et al. 2020). Logged as a fork not taken.
  - Scaling sigma (a spread correction) as part of stage 2: rejected for this batch --
    05_residualStructure shows even an oracle per-horizon factor fixed on the test cells raises
    mean CRPS from 26.05 to 35.65 while reaching 89.5% coverage, and the in-window errors
    would give a factor below 1 (they are over-covered at 93-94%); the coverage deficit is a
    heavy tail of regime-break cells, not a uniformly narrow interval. Logged as a fork whose
    honest version (a heavier-tailed predictive family) belongs to stage 1's specification.
  - No clipping at zero: the unclipped variant is scored in results/comparison.json
    (25.68 vs 25.63 clipped); clipping is kept because a negative expected count is impossible
    and moving a Gaussian's mean toward a non-negative observation cannot raise its CRPS.
  - ridge alpha: 10 chosen as mild regularisation for ~25 standardised features on ~5,000
    rows; not tuned on the backtest (tuning stage 2's hyperparameters against the one backtest
    is the researcher-degrees-of-freedom failure MOTIVATION.md names). A perturbation.
  - Standardising by the province's in-sample residual scale instead of the se: the se is
    what the correction is multiplied by, so z = error/se keeps fit and correction on one
    scale. Its cost is visible in results/comparison.json: in LA-SV, whose se (200-400) is
    tens of times its 2008-09 level, a zhat of +0.4-0.6 becomes a correction of 130-190
    cases, and the province loses 232 CRPS-units in total. A correction bounded relative to
    the forecast level is the refinement this suggests, not tried here.
agency: agent-autonomous (design, features, family, combination rule); the decision to build
        candidates on a diagnostic and literature basis rather than pick a sixth ad hoc is
        human-set (plan §4b, 2026-09-20).
information: agent-retrieved -- the target change follows Wolpert (1992), Breiman (1996),
        Ben Taieb & Hyndman (2014) and the critique in Taskaya-Temizel & Casey (2005); the
        scale-preserving pooling follows Montero-Manso & Hyndman (2021) and the M5 experience
        (Januschowski et al. 2022); all retrieved by web search this batch and cited in the
        batch report with their verification status.

---
section appended at commit d9d1fba (comment-only changes after the run; nothing re-run):
script: scripts/01_stage2_oos_error_ridge.py
        sha256:a94ab31ef5a48f695e1ea92ececf63fb73b6c719f214a9d894b94e1cac45081b
        (was b0b641be…: one line added, `SEED = None` with a comment saying the script draws
        no randomness, so the seeds invariant's text heuristic sees the statement it looks for)
        ../../scripts/lib/residual_features.py
        sha256:cbe025691c5e58b415720849ca3e30964f24c96f921764d638a9ccd8149bec2c
        (was c6339fc4…: the comment on WARMUP_MONTHS reworded, see
        05_residualStructure/provenance/error_structure.md)
The committed results are those of the d8f9b07 run; no logic changed in either file.

---
section appended at commit e590d27 (run at 926cd1a; human-set follow-up, plan §4b 2026-09-21):
the horizon set stage 2 trains on is now read from the evaluation scheme, not fixed.
script: scripts/01_stage2_oos_error_ridge.py
        sha256:2b6758437a6115707b16e99b593f25805cd188acf56afab1c325edab5f1febac
        (was a94ab31e…: reads the scheme's n_periods via check_horizons and passes it to every
        row builder; conclusion.json gains horizon_months and horizon_source)
        ../../scripts/lib/stage2_oos.py
        sha256:d6f12d8cf9643eab708ed9fc175b372f562dcd9578da4efd19ec7ccf603e0074
        (was 04dbf43a…: N_AHEAD/HORIZONS/FEATURES constants replaced by horizons(n_ahead),
        features(n_ahead), check_horizons(); training_rows/test_rows/design_matrix take
        n_ahead; test_rows refuses a test window of another length)
inputs (added): ../../01_data/03_backtest_scheme/results/schedule_summary.json
        sha256:dc56ddb766c0e73e253236485169d2e97ab8e8aaa648e2319d4587cd603e9ccc
        (n_periods = 3 -- Chap's evaluate default, verified in chap-core's
        cli_endpoints/evaluate.py: BacktestParams(n_periods=3, n_splits=7, stride=1))
outcome: results/per_cell_scores.csv and results/ridge_coefficients.csv byte-identical to the
        d8f9b07 run (git reports no change); results/conclusion.json differs only by the two
        added horizon fields. The scores above stand.
