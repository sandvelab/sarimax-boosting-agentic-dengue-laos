result: results/manifest_holdout.csv · results/manifest_holdout_summary.json ·
        results/holdout_freeze.json · results/holdout_freeze_check.json
script: scripts/07_plan_holdout_manifest.py
        sha256:0ca1dbbbd8d686dfcb7938a7fd021e6feaa403f8e267e9f5bcce5979dae6c5b2
        (b0035d70… froze the set; the SENSITIVITY_POINTS comment was then reworded for the
        `crossing` heuristic, which read "unchanged from v1 and v2" on the constant's own line
        as a value carried by hand. Re-planning under the reworded script produced the same
        43 rows, byte for byte -- sha256 835bb52c… both times, recorded in
        results/holdout_freeze_check.json.)
        the row set it freezes, ../scripts/lib/:
        holdout_eval.py sha256:2c7d9990ca2fedd7a651d7a0bc64347e4af25cabd11402f0715169ca6ed87fdf
invocation: ../../environment/env/bin/python scripts/07_plan_holdout_manifest.py
inputs: results/holdout_runner_verification.json
         sha256:44dac8fc94804187f73e905e15db7e13add84436dcd0113d04334a896bded65b
         (the gate; the script refuses to freeze unless it records three identical
         reproductions, and takes the province set, the holdout schedule and the two
         baselines' measured cost from it)
        results/manifest.csv
         sha256:d2c5e813e7215eb908787049546e0e8346c3311ea7b6d6b3ca6fd43c53834ac0
         (the frozen development v2 set -- every tier-2 holdout row copies its node,
         parameter, values, basis and informativeness rank from its development counterpart,
         and a tier-2 row with no counterpart stops the script)
        results/run_log_v2.csv (measured development wall-clock per row, the cost base)
        analysis/01_data/03_backtest_scheme/results/split_schedule.csv (the development
         training months, the denominator of the cost scale factor)
        analysis/04_stage2/ -- the child directories with a claim.md, read to derive the
         tier-1 rows from the tree rather than from a list
        git HEAD at run time, recorded as frozen_at_commit
environment: environment/ (project main)
        lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: 67f998c
instructions-commit: 67f998c
node: analysis/06_stability
produced: 2026-09-22
freeze: results/holdout_freeze.json records manifest_holdout.csv's sha256
        (835bb52cab2e91cc630d420f59b07691cf8a7ddb0990e5079bfbba25d9080ab0), 43 rows, frozen at
        67f998c on 2026-09-22 -- a commit that carries every script the set will be run by and
        no holdout result, which is what `/validate invariants`' `freeze` check asserts against
        git. It also records the sealed holdout file's own digest
        (389e4f4975980588c88a8a0f9d44e6ad903644faf096ebb469e62d89122e100d) so that the file
        phase E opens is the file that was sealed; the digest is of the whole file and no case
        value is read to compute it.
        **Re-running this script does not re-freeze.** With the freeze present it rebuilds the
        set in memory, compares, and writes results/holdout_freeze_check.json instead: the
        frozen file's digest, whether re-planning now yields the same bytes, and two fatal
        lists (frozen rows the tree no longer carries; frozen rows whose configuration digest
        moved). Verified on 2026-09-22: identical, both lists empty.
set: 43 rows. Tier 0, 3 planned -- the pre-registered main path and the two required baselines;
        stage 1 alone needs no row, since every two-stage row's conclusion.json scores it on the
        same cells. Tier 1, 9 rows: the four not-taken `04_stage2` siblings the parametrised
        pipeline expresses (f, g, i, j) planned; a, b, c, d, e not run, with the reason. Tier 2,
        26 planned -- the development v2 perturbations under holdout names, so every judgment
        call measured on development is measured again on the held-out year and the two pair by
        row name. Tier 3, 5 not run, carried forward unchanged.
budget: 33 planned rows estimated at 940 s against the 3,600 s ceiling carried over from phase
        D. The estimate scales each row's measured development wall-clock by 0.569, the ratio of
        total training months between the two schedules (594 against 1,044), since a run's cost
        is dominated by fitting stage 1 once per province per split over its training window.
        The line falls below every planned row: nothing is excluded for budget. The rolling
        refit dominates at an estimated 440 s.
reporting-rule: frozen with the set, in holdout_freeze.json and manifest_holdout_summary.json:
        what counts as the primary answer (plan §2's two bars on main@h__holdout), the required
        baselines, how the spread is reported (a distribution, never a best row, at the same
        two-percentage-point threshold as v1 and v2), the pairing with development, and what
        binds afterwards (nothing added, dropped, re-tuned or re-run once a holdout number has
        been seen; nothing promoted on held-out evidence; a contradicting result is the finding).
alternatives-considered:
  - Freezing only the main path and the baselines: rejected -- plan §3 evaluates the holdout
    "across a perturbation manifest frozen beforehand", and a single row would say whether the
    margin survived without saying what it turns on, which is the finding phase D established.
  - Running the five in-sample-residual siblings (a-e) on the holdout: rejected, recorded as a
    visible absence. Each needs a holdout-capable rewrite of its own node script; all five lose
    to stage 1 alone on development (+0.78% to +7.73%, with e's -0.63% failing the calibration
    bar), and batch 10's diagnostics explain the failure mechanically. The held-out year is spent
    on the configurations whose margin is in question.
  - Changing the main path before the freeze to one of the three v2 rows that scored better on
    development: rejected by the human at the freeze (plan §4b, 2026-09-22). They lie within the
    alternative-seed row's own distance from `h`, and a change now would make the holdout
    evaluate a fourth round of selection on the same 371 development cells.
  - Reopening stage 1 after the no-differencing finding: rejected by the human at the freeze
    (plan §4b, 2026-09-22). `stage1=nodiff_101x100@h__holdout` is in the frozen set either way,
    so the held-out year still measures how much of the margin survives a better stage 1.
  - A cost estimate by re-measuring rather than scaling: rejected -- re-measuring means running
    the rows, which is phase E. The scale factor is derived from two stored schedules and is a
    field in the summary, so a wrong estimate is visible against the run log afterwards.
agency: agent-autonomous (the tiering, the row set, the cost model, the reporting rule and the
        freeze mechanism). Human-set at the freeze: the main path stays `h_levelOnlyBoosting`
        and stage 1 is not reopened (plan §4b, 2026-09-22).
information: none retrieved; every input is a file already in this repository.
