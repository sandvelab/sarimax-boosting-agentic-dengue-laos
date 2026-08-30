# Provenance — the pool's weights, fitted by minimum CRPS

```
result:              weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_weighting.py
                     sha256:b1b0c09fda51d454d92e7c8cca646a64a4be2e189a15b1e95c03ddefe9eaceb7
invocation:          "$PYTHON" scripts/choose_weighting.py, with COMBO set
inputs:              analysis/02_setup/results/<combo>/setup_spec.json — for the forecast
                     horizon, so the validation block is the same shape of problem as an
                     evaluated block
                     analysis/02_setup/results/<combo>/analysis_dataset.csv — for the
                     premise's description of the hold-back, not for any fitted quantity
environment:         environment/ (project main)
seeds:               none here. The weights are fitted inside the model's `train`, by a
                     deterministic solve over the members' validation forecasts, which are
                     drawn from the members' own seeds.
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble/01_weighting/b_crpsWeighted
produced:            2026-08-28
```

**What it establishes.** The alternative weighting, and what estimating the weights costs:
**22.838** against the equal pool's 18.817, a loss of 4.021 CRPS, seven times the resolvable
floor. The fork does not move.

**Where the weights come from.** The last four forecast blocks of the training frame are held
back, every member is refitted without them, each member forecasts them through its own
`predict`, and the weights are the exact minimiser on the simplex of the pool's own CRPS over
those cells — computed from the sample identity `CRPS = E|X − y| − 0.5 E|X − X'|`, which makes
the pooled CRPS a quadratic in the weights, and solved by projected gradient checked against
every vertex and against the equal-weight point. Nothing from the evaluated period is used.

**The solve did not fail; the assumption behind it did.** On the validation year the fitted
weights give 14.227 against 14.253 for the best single member and 17.026 for equal weights.
The member they concentrate on — 0.953 of the pool on candidate 1 — is the worst of the three
non-baseline members on the evaluated period. One year of held-back data does not say which
member will be best on the next two.

**One judgment call, logged rather than forked.** How much of the training frame is held back:
four blocks of the forecast horizon. Shorter than the horizon would fit weights for a problem
the model is not asked to solve; longer takes more training data from the members whose
weights are being fitted; four is the smallest number that gives each member more than one
block to be wrong in. `AGENTS.md` §3 permits a judgment call to be a node or a logged
decision, and this is the second, logged here, in the script's docstring, in the node's claim
and in the option specification the run stored.

alternatives-considered: weights proportional to 1/CRPS (rejected — the members' scores span
roughly 21 to 25, so inverse-score weights would run from about 0.22 to 0.27 and the fork
would measure a rounding error at full compute cost); exponential weights `exp(−ηCRPS)`
(rejected — η is a tuning knob and would have to become a fork or a second logged decision,
where the minimum-CRPS pool is knob-free); making the hold-back length a fork (rejected under
the same argument batch 10 used for the boosting hyper-parameters: it enumerates a tuning grid
whose siblings re-run in phase D and on the holdout, to answer a question about tuning);
fitting the weights on the evaluated cells (never considered admissible — it is the
construction the plan's §3 exists to forbid).
agency: agent-autonomous

---

## Batch 14 — the fork run through the driver, alone and in two pairs

```
result:              $COMBO/model_option_spec.json
combinations:        weighting_crpsWeighted (re-run),
                     provinces_reportingOnly__weighting_crpsWeighted,
                     provinces_mergeVientiane__weighting_crpsWeighted,
                     weighting_crpsWeighted__aggregate_caseWeighted
script:              unchanged from the section above; this batch changed no script here
invocation:          bash .../c_ensemble/01_weighting/b_crpsWeighted/run.sh, with COMBO
                     set by analysis/05_stability/scripts/run_manifest.py and
                     COMBO_BASE=main
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              3fb1280 (the tier-1 row), ba3cf8d (the three pairs)
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble/01_weighting/b_crpsWeighted
produced:            2026-08-30
```

**What it establishes.** This is the **only candidate-internal fork that moves the reported
conclusion at all**, and it moves it more than every setup, scoring and baseline fork put
together. Fitting the pool's weights on a year held back inside the training frame gives
skill **−0.0335** against the main path's +0.1485 — a move of 0.1820 — and takes the pool to
22.838 CRPS, behind the reference at 22.098. Its paired comparison falls to 0.48 standard
errors, which is the comparison ceasing to resolve anything.

Batch 11 measured the same fork as 4.021 CRPS and called it that batch's most useful result.
On the skill scale the whole phase-D set is read on, it is the second largest single-fork
move in the project, behind only replacing the pool with candidate 1.

**This is also the row that found the driver's fork-blindness.** It is the only tier-1 row
whose fork belongs to the family that runs, and the driver called that family's `run.sh`
after the moved child — so the fork's sibling ran too and the pool's assembler refused two
children of one fork, correctly. The failure and the fix are in the driver's own record.

alternatives-considered: none new; the child's construction is batch 11's.

agency: agent-autonomous.
