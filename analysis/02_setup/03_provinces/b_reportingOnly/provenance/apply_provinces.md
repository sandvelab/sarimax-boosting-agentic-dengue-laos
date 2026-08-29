# Provenance — the provinces with no evaluable cell removed before the platform

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_provinces.py
                     sha256:112ca61a602026fa95883910435d2d5af1ca5db32c4479876a884a279ed6d1c7
invocation:          "$PYTHON" scripts/apply_provinces.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=provinces_reportingOnly.)
inputs:              the analysis dataset produced by whichever child of 02_trainingWindow
                     ran in this combination — resolved by search, not by name, and its
                     sha256 recorded in results/$COMBO/setup_spec.json as `input_sha256`
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage is a predicate on a location column.
commit:              40b6936
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/03_provinces/b_reportingOnly
produced:            2026-08-29
```

**What it establishes.** Two provinces are removed — **LA-VI and LA-XN** — leaving 16
provinces and 2 304 rows of the 2 592 that entered, and the same **371** evaluable cells
(`results/$COMBO/setup_spec.json`). The metric is a mean over exactly what it was a mean over
on the main path; what changed is the training frame, which no longer contains a province of
structural zeros and a province that stopped reporting in 2005.

**The difference from the main path is not cosmetic.** `a_chapFilter` leaves both provinces in
the file and lets chap-core's region filter drop LA-VI at evaluation time. A province dropped
at evaluation is still a province the models trained on: a hierarchical model has been pooling
across 144 structural zeros, and a boosted model has been fitting to them. Removing them
earlier is a different analysis, not a tidier spelling of the same one.

**Which provinces go is derived.** The script applies the rule — a province with no non-missing
`disease_cases` inside the evaluated span read from the stored scheme — rather than naming the
two codes. A province that went silent for some other reason would be caught by the rule
instead of missed by a constant, and the rule itself is written into the specification.

alternatives-considered: **hard-coding LA-VI and LA-XN** — rejected as above; the pair is a
consequence of a rule and not an input. **Removing only LA-VI**, the one the platform itself
rejects — rejected because it would make this child a re-spelling of the main path rather than
an alternative to it: LA-XN is the province that survives the filter and contributes nothing,
which is exactly the case the fork is about. **Removing provinces by a data-quality judgment**
— for instance a minimum number of reporting months — rejected because it is a judgment about
data quality made by the party whose score depends on it, which is the objection `a_chapFilter`
was chosen to avoid; the rule here is mechanical and refers only to whether a cell can be
scored at all.

agency: agent-autonomous. That the two provinces behave this way was established from the data
by batch 3 and recomputed by `a_chapFilter` on every run; that removing them before the platform
is the alternative worth running was fixed by batch 5's fork design and batch 12's claim. The
removal rule and its derivation are the agent's.
information: agent-retrieved — both the silent provinces and the evaluated span come from files
the run reads, not from memory.
