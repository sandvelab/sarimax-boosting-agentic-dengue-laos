# reconnaissance

Scripts that establish facts about an external system this project depends on but does not
control. They are machinery rather than analysis: nothing here answers a claim in
`analysis/`, and no number from here reaches the manuscript. What they produce is the
evidence behind a batch report.

They live outside the claim tree deliberately. The tree holds the analysis of dengue
incidence in Laos; "what does `chap eval` actually compute" is a question about the
instrument, not about the disease, and giving it a node would put a fact about the platform
on the same footing as a finding about the data.

| Script | What it establishes |
|---|---|
| `capture_chap_surface.sh` | The installed `chap-core`'s CLI surface, and one end-to-end `chap eval` smoke run on a pinned example dataset and a pinned example model |
| `describe_evaluation.py` | What a Chap evaluation `.nc` contains, and the CRPS behind it at global, per-region, per-split and per-cell resolution — computed with chap-core's own metric classes, never reimplemented |
| `score_evaluation.py` | The routine form of the above: every table this project reports from one evaluation file — CRPS at four resolutions, MAE and both interval-coverage metrics per province, and what the headline mean is a mean over |
| `run_ewars_reference.sh` | That the reference model of the plan's §2 runs on the development dataset, pinned by image digest, at the scheme batch 3 fixed — with its score, its calibration and its cost |
| `ewars_reproducibility.sh` | How far the reference's score moves between identical runs. It is unseeded, so this bounds what any comparison against it can mean |
| `reference_spread.py` | The three spreads that bound a comparison against the reference: Monte Carlo, across splits, across regions |
| `measure_native_cost.sh` | What an evaluation run costs for a native Python model of the kind our own candidates will be — the unit the budget needs |

The first two write to `AI-generated/chap-reconnaissance/` and the rest to
`AI-generated/method-reconnaissance/`; both folders carry a `provenance.md` naming the
commit, the pins and the invocation for every file. Re-running a script rebuilds its outputs
— with one exception that is itself a finding: the reference model calls no `set.seed`, so
`run_ewars_reference.sh` reproduces its recipe and not its numbers.

The reference model's scripts need a running Docker daemon; its image is amd64-only and runs
under emulation on arm64.

Invoke from the repository root:

```bash
bash AI-internal/reconnaissance/capture_chap_surface.sh
bash AI-internal/reconnaissance/run_ewars_reference.sh
bash AI-internal/reconnaissance/ewars_reproducibility.sh
bash AI-internal/reconnaissance/capture_model_library.sh
bash AI-internal/reconnaissance/measure_native_cost.sh
```
