# Provenance — the phase-E answer: the two datasets on one axis

```
result:              results/holdout_vs_development.csv
                     results/holdout_vs_development.json
                     results/fork_sensitivity_both.csv
script:              scripts/pair_holdout_development.py
                     sha256:a7595ccfb60db109db366f9685b612ae6c6a9666f959ef261b44e1f08c72ece3
invocation:          "$PYTHON" scripts/pair_holdout_development.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python. No COMBO: this node's outputs
                     describe every combination and belong to none.)
inputs:              analysis/05_stability/results/manifest_holdout.csv
                     analysis/05_stability/results/conclusions.csv
                     analysis/05_stability/results/holdout_conclusions.csv
                     analysis/05_stability/results/distribution.json
                     analysis/05_stability/results/holdout_distribution.json
                     analysis/05_stability/results/sensitivity_by_fork.csv
                     analysis/05_stability/results/holdout_sensitivity_by_fork.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every number is an arithmetic summary of stored scores; the one
                     statistic computed rather than copied is a rank correlation, written
                     here rather than imported because scipy is not in the pinned
                     environment and one function is not a reason to add it.
commit:              609e1be
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: join the two halves on the combination names. Rejected: the frozen
                     manifest carries each row's development conclusion in its own columns,
                     fixed before the year was opened, and joining on that is what makes the
                     comparison one that could not be selected afterwards. Names are labels
                     and a rename would break the arithmetic silently.
                     Also considered: report only the reported analysis's own development-to-
                     holdout gap. Rejected because a single gap cannot distinguish a model
                     that over-fitted from a year that was harder, and the distribution and
                     the reference's own CRPS on each dataset are what separate them.
agency:              agent-autonomous for the statistics; human-set for the requirement that
                     the two be reported side by side and that a large gap be reported
                     plainly rather than explained away (plan, phase E).
```

**What it establishes.** The reported analysis scores **+0.1485 on development and +0.0868
on the held-out year**, a gap of **−0.0617**. It still beats the reference model and both
required baselines on 2010. **2010 was a much harder year**: the reference model, which
nobody here tuned, scores 84.026 mean CRPS on it against 22.098 on development, which is why
the conclusion is reported as a ratio and why raw CRPS is not compared across the two.

**28 of the 32 analyses did worse on the year they had not seen**, median gap −0.056. The
holdout spread is **0.706 wide against development's 0.304**.

**The development ranking barely transfers**: Spearman rank correlation between the two
skill scores across the 32 analyses is **+0.396**. The ranking of the *forks* transfers
better, at **+0.679**, and **14 of 17 forks agree** on whether they move the conclusion at
all — the province filter, the model family, the training window and the headline weighting
matter on both; the persistence construction and the pool's own weighting matter only on
development; the hierarchical model's covariate set matters only on 2010.

**The frozen pairing is verified, not assumed.** Every development figure in the manifest
still equals what `conclusions.csv` says today, to 1e-9. The script stops rather than
reporting a comparison whose development half has moved since the set was frozen.

---

## 2026-09-03 — the frozen figure is reported, not re-asserted (batch 30)

```
result:              results/holdout_vs_development.csv    (byte-identical)
                     results/fork_sensitivity_both.csv     (byte-identical)
                     results/holdout_vs_development.json   (frozen_pairing_verified only)
script:              scripts/pair_holdout_development.py
                     sha256:c58009cbf0a8f4e8afc4b588c38133c1f039b53cd54171841f6a35fa74b90881
invocation:          "$PYTHON" scripts/pair_holdout_development.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              unchanged from the section above
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none
commit:              78fd76a
instructions-commit: 595c32d
node:                analysis/05_stability
produced:            2026-09-03
defence:             AI-internal/useful-scripts/check_pairing_defence.py
                     -> AI-generated/validation/26-09-03_pairingDefence.json (5 of 5 pass)
alternatives-considered: keep the assertion and widen the tolerance to the width of the
                     noise band. Rejected: the band is itself a draw of the same unseeded
                     model — 0.021778, 0.043084 and 0.034944 over three draws — so the
                     tolerance would be a number that moves, and a check whose threshold
                     is redrawn on every run is not a check. The distinction that holds is
                     categorical rather than numeric: a figure that drifted against a
                     pairing that moved.
                     Also considered: freeze the development `beats_all_baselines` beside
                     the row so it too could be read rather than re-derived. Rejected here
                     — it would rewrite `manifest_holdout.csv`, which plan §3 binds and
                     `holdout_freeze.json` records the digest of. It is reported in the
                     output as the one development figure still read from today's table.
agency:              agent-autonomous.
```

**What changed.** The script required every frozen `development_skill_score` to still equal
`conclusions.csv` to `1e-9`. That figure divides by the reference model, which is unseeded,
so the assertion could hold only on a tree whose development half had not been re-run: it
passed exactly where it was not needed, and it stopped batch 27's clean-room run at the last
script in the tree with all 32 held-out analyses already scored.

Two differences are now separated. A **drifted figure** is reported under
`frozen_pairing_verified.frozen_figures_that_drifted`, with the largest move and the band
that dataset's own four repeats of the reference define. A **moved pairing** — a frozen row
whose development twin the table no longer concludes — is fatal, and stops the run before
anything is written. `freeze_holdout_manifest.py` had already drawn that line minutes
earlier in the same run, under `drift_under_an_unchanged_set`.

**`development_beats_reference` now comes from the freeze.** `conclude.py` defines it as
`ours.mean_crps < reference.mean_crps`, and both sides are frozen beside the row, so it is
derived from `manifest_holdout.csv` rather than read from today's `conclusions.csv` —
reproducing the archived value on all 32 rows. On batch 27's clean-room conclusions one row
flips and the reported development count read 28 rather than 27, so this was a reported
phase-E figure following a re-derived table. `development_beats_all_baselines` cannot be
derived from the freeze — the baselines' own CRPS is not frozen beside the row — and the
output names it as the one development figure that is still re-derived.

**What did not change.** `holdout_vs_development.csv` and `fork_sensitivity_both.csv` are
byte-identical to the archive. In `holdout_vs_development.json` every reported number is
unchanged; the diff is confined to the `frozen_pairing_verified` block and two lines that
say where the two development counts come from.
