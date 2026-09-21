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

---
section appended at commit cbeee04 (comment-only change after the run; nothing re-run):
script: scripts/05_report_distribution.py
        sha256:ce4f65912ad72d5134cf363eb400ca282bbff1efaf2593aae050843f98db882b
        (was 241ba500…: the comment on SENSITIVITY_POINTS reworded; the crossing heuristic
        read the old wording as a value transcribed from another step, which it is not.) The
        committed results are those of the eda4fbc run.

---
section appended at commit ba79a02 (batch 15): **script changed and run for manifest v2, with
the comparison against v1**.
script: scripts/05_report_distribution.py
        sha256:00e30ed97e4151546113484122f3931a1b85dc69257690555026ce72f6045b62
change: (was ce4f6591…) the version, main path and row tag are read from the freeze and the
        manifest summary; groups are assigned by the perturbation a row names independent of
        version (the `@h` tag and v1's `g_` prefix stripped) and extended with the v2 feature
        and bound rows; a version after the first writes `_v<N>` files beside v1's, which are
        left as they were; and, new, `versus_v1`: each v2 row paired with its v1 counterpart by
        perturbation (22 pairs), the shift of its margin in points, whether it moves the size in
        either version, and -- where a v2 row's configuration is identical to a v1 row's,
        checked by comparing the `config` dicts in the two conclusion.json files -- whether the
        two-stage mean CRPS reproduced exactly. SENSITIVITY_POINTS unchanged at 2.
result: results/distribution_v2.json  sha256:9aeda5a303c562148f568ea0f32bec62cabd458b5c330833f803f13278efd524 ·
        results/perturbation_effects_v2.csv  sha256:c4c1217f972c9917064b06322761091b3edd77c59b5a12cb46ccef3344101b3b ·
        results/province_stability_v2.csv  sha256:5561ac7d63d8331da2392acb7c1616ff6668720e65855a153b4d8d9b66668750 ·
        results/horizon_stability_v2.csv  sha256:79cefa90ed903a1050be7974981ded770656b07a9d3197473cfc589958795702 ·
        results/version_comparison_v2.csv  sha256:a247df9378dd992bc37b8ec40a36e23659af2ac8a625003374d32651dd48eb32
invocation: ../../environment/env/bin/python scripts/05_report_distribution.py
inputs: results/conclusions_v2.csv  sha256:27916dca54ddc7a7277cd3f5b6cda6465b9ed45681b0aa842e76ff5003123045
         results/manifest_freeze.json  sha256:a6e1efa271432a42694d4c106aa366a6641a5c52d3ac41d345c3101aeff15d95
         results/manifest_summary.json  sha256:f9427e68414ca876758e57e37b242cc5a8bbcb268f4742fa1f6283ff673acf02
         results/$COMBO/conclusion.json and results/$COMBO/per_cell_scores.csv for main@h and
         the 26 `@h` rows (per-province and per-horizon tables), and for `main` and the 29 v1
         rows (configuration matching)
         results/perturbation_effects.csv  sha256:fb52e7cad42ae4655e36cb1732dd3f724109dcbc6aae6722d8c6543a31b8654c
         results/distribution.json  sha256:038488860377cb8a113086c3459570b63b075245033f287e5e961f7518dd493b
         (v1's report, batch 13, read for the comparison; not rewritten)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: ba79a02
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-22
what it records: the distribution of the margin over the 26 v2 perturbations (26 of 26 beat
        stage 1 with coverage not worse; -10.41% to -1.06%, median -5.91%; 8 rows move the size
        beyond 2 points), by group; province and horizon stability over 27 combinations; the
        tier-1 and tier-3 rows restated; and versus_v1 (20 of 22 paired rows have a larger
        margin around h than around g, median shift -2.33 points; 4 configuration-identical
        rows reproduce v1 exactly). Claims C8-C13 are grounded in these files.
alternatives-considered (this section):
  - Pairing v1 and v2 rows only by configuration, not by name: configuration identity finds
    just four pairs, because every other v2 row differs from its v1 namesake in the feature
    set; pairing by perturbation name is what answers "does the same alternative choice move
    the margin the same way around either main path", so both pairings are written.
  - A different threshold for "moves the size" in v2: rejected -- the same 2 points keep the
    two versions comparable, and the threshold is a column in the output.
agency: agent-autonomous
