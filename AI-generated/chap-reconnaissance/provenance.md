# provenance — chap-reconnaissance

One section per generated file, per `AGENTS.md` §8. **Append; never overwrite an existing
section.**

These files are not results of the analysis and do not live in a claim tree node, so they
carry no node-level provenance record. The binding of file to script, invocation, pin and
commit is the same either way, and this file is where it is kept.

---

## All files in this folder — batch 2, 2026-08-23

```
script:              AI-internal/reconnaissance/capture_chap_surface.sh
                     sha256:2330df6029eb60f0289ff2b804c915d9ca4c3c74e99367a74f6991e944adc932
                     AI-internal/reconnaissance/describe_evaluation.py
                     sha256:30373e74d5799ce3d6d8dd1a2fc0013b3e8f6fdc0ed585f12ce7b5b29025931a
invocation:          bash AI-internal/reconnaissance/capture_chap_surface.sh
                     (run from the repository root; the shell script calls describe_evaluation.py)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     built by environment/install-chap.sh, resolved in environment/lock.txt
inputs:              chap-core example dataset example_data/hydromet_5_filtered.csv at tag v2.1.0
                     sha256:f488eaae00007d7762d7f382ae37bc287540b0e0de217d9202b963a21a504588
                     dhis2-chap/minimalist_example_uv at commit a67d427bfde1341be6618e64c9a4a9a2c79cec2a
seeds:               none. The smoke-test model is an ordinary least-squares fit and draws
                     no random numbers; the project seed 20260822 has no surface here.
commit:              2ef682d
instructions-commit: 15b4ba9
produced:            2026-08-23
```

**What these files are for.** Batch 2 had to establish five things about the platform before
any modelling can start: whether it installs, whether `chap eval` accepts a local model
directory, what the reported CRPS is computed over, whether per-region and per-split values
are recoverable, and what a Chap-compatible model must implement. Answering those from the
running tool and storing the answers is what this folder is.

**What they are not.** No number here says anything about dengue in Laos. The dataset is an
unrelated five-region example shipped with chap-core, and the model is a linear regression
that emits one sample per forecast, which makes its CRPS numerically equal to its MAE. The
files exist to show the chain runs and to expose the shape of what it produces.

**alternatives-considered.** The smoke test could have used `monthly_data.csv`, which is the
single-region example closest to what the documentation walks through. `hydromet_5_filtered.csv`
was taken instead because it has five regions, monthly periods, and a `population` column,
which is the shape of the Lao dataset — and because the question that most needed answering
was whether *per-region* values are recoverable, which a single-region example cannot
answer. The R example model (`minimalist_example_r`) was the other obvious choice and was
rejected only for cost: it builds an `renv` library, where the `uv` model resolves in
seconds, and the contract it demonstrates is the same one.

A second route existed for the metric question: read the CRPS out of `chap export-metrics`
and break it down by hand. It was rejected because a CRPS we computed ourselves is exactly
the number we could most easily bend without it being visible. `describe_evaluation.py`
therefore calls chap-core's own `CRPSMetric` and changes only the dimensions it aggregates
over, so the score stays the platform's at every resolution.

**agency:** agent-autonomous. Batch 2's aims are the plan's; how to establish them was not
specified and every choice above was the agent's.

**information:** agent-retrieved — the Chap documentation, the `chap-core` source as
installed, and the model repositories on GitHub. `Archive/case-source-material/chapOrientation.md`
is human-pointed and named the five questions.

**Reproducibility, checked rather than asserted.** `capture_chap_surface.sh` was run twice
in succession at this commit. Every metric file came back byte-identical. Two attributes of
`smoke_eval.nc` did not: `created_date`, which is a wall-clock stamp, and `split_periods`
and `org_units`, which chap-core serialises from unordered sets and which therefore come
out in a different order each run. Nothing numeric moves, but a byte-comparison of two
`.nc` files from identical runs will report a difference — which `/validate cleanroom`
needs to know before it compares outputs against archived ones in phase E.
