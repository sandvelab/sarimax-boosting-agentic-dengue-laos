# Batch 17 — the claim collection completed, and the report that descends to the values

Generated from [[26-08-22_dengueForecastingCase]] — iteration 17

**State: done — produced.**

Two of Rule 8's and Rule 9's obligations were still standing at the end of phase D and E's
first batch: the claim collection held only the twenty-one statements phases D and E had
produced, and the hierarchical report had never been built. Both are now done.

**The collection is 39 claims.** Eighteen were added here — C22–C39 — and they are the half
the file did not have: what the analysis established about the data, the evaluation and the
models, and what did not work. The headline development result now exists as a claim rather
than as a number in a conclusion file that nothing pointed at.

**The report is 1 175 pages and it goes four levels below the tree.** From the reported skill
score to the national mean each model was scored at, to that mean by province, to each
province month by month, to the per-cell CRPS everything above is an average of — for each of
the 65 combinations that were scored, on both datasets. Every figure on every page is
displayed from the file the analysis wrote. Nothing in it recomputes an aggregate, so it
cannot disagree with the analysis about a number.

---

## 1. What was produced

| | |
|---|---|
| Claims added | **18** — C22 to C39 |
| Claims total | **39**, every one resolving to a file that exists, every one carrying a node and an agency |
| Report pages | **1 175** — 69 node pages, one per node in the tree; 65 combination pages; 1 040 province pages |
| Links in it | **9 046**, of which **0** are broken |
| Build | **1.6 s**, 18 MB, `.venv/bin/python AI-internal/useful-scripts/build_hierarchical_report.py` |
| Reproducible | two builds into different directories are **byte-identical**, README included |

## 2. What the eighteen claims are

The collection had a shape problem rather than a size one. Batch 15 wrote twelve claims and
batch 16 nine, all of them about the perturbation set and the held-out year — so the file
recorded how far the conclusion survived its alternatives without ever recording the
conclusion, and recorded that the model family is what the result is sensitive to without
recording what the families scored.

| Claims | What they cover |
|---|---|
| C22, C23 | The development headline, and the fact that its margin cannot separate the two models: 3.282 CRPS against a split-clustered standard error of 1.726 |
| C24 | The reference model's own re-run floor — 0.565 CRPS, below which nothing is attributable to a model |
| C25, C26, C38 | What pooling bought (1.954 CRPS over the best member, against a registered premise that said it would not), what fitting the pool's weights cost (4.021), and that the pool holds no model code of its own — checked by rebuilding it from its members' stored forecasts |
| C27, C28 | The negative one: candidate 1 never beat the reference and is the lowest of the thirty-two development analyses. Candidate 2 beat it alone |
| C29 | The reported model is cheaper than the model it beats — 59.5 s against 241–285 s per repeat |
| C30, C31 | Why the 25–75 coverage figures are not readable on this dataset, and that both required baselines lose to the reference, so the baselines are not the bar that binds |
| C32, C33, C34 | What the metric is actually a mean over; three statements in the dataset's own schema that do not describe the file; the zeros and the declining completeness |
| C35, C36 | The partition verified rather than assumed, and the backtest scheme fixed before any model ran |
| C37 | Every model we wrote reproduces byte-identically; the reference cannot be made to |
| C39 | The cost model tested as a prediction for the first time, on the phase-E half: right at the total, 1.15, and wrong on the rows again |

**One discipline point, and it changed what several claims say.** `readme-at-start.md` states
that the pool sits 1.90 standard errors from the reference. No file holds that number — the
paired difference and its standard error are both stored, and the ratio between them is not.
A claim asserting 1.90 would be a number computed in the agent's context and written into the
record, which is exactly the failure `AGENTS.md` §1 describes and which looks like nothing on
the page. C23 therefore gives the two stored figures and leaves the division to the reader.
The same rule shaped C29 and C31.

**Fifty stored results are cited by no claim**, of which twenty-four are figures and their
plotted values, which illustrate claims already made. The other twenty-six are
characterisation tables and cost intermediates. That is `claims.py audit`'s own count and it
is not a defect: not every stored file is a statement.

## 3. The report, and what makes it hierarchical

Through batch 16 the builder produced one page per node with a flat list of that node's
files. That was right when there was one combination and stopped being right at sixty-five:
the reported analysis appeared as one file listing among sixty-four perturbations of itself,
and there was no way to get from a reported mean to the values it averaged.

**Four levels below the tree, one directory per combination.**

1. **The conclusion** as `conclusion.json` states it — skill score, both CRPS figures,
   coverage, the paired difference, its standard error, and what this backtest can resolve.
2. **National** — the mean each model is reported at, from `metrics_summary.csv`, with the
   same mean cut by split and by horizon.
3. **Province** — each province's own mean for every model, from `crps_by_location.csv`.
4. **Month, and the values** — every evaluated month for that province: the count observed,
   the split and horizon it belongs to, each model's CRPS, and whether the outcome fell
   inside each model's 10–90 interval. From `metrics_cell.csv`, which is linked at the foot
   of the page.

**Three things the build does not do, on purpose.**

It **does not recompute anything**. Every number is read from the file that holds it. A
report that derived its own means could disagree with the analysis and look right doing it.
The cost is that it can only show what the analysis stored — there is no per-split,
per-province breakdown below the province page, because the aggregation node does not write
one. That is the diagnostics gap batch 22 opened and batches 14, 15 and 16 declined to close,
seen from the display end.

It **does not name a child of the weighting fork**. Which aggregation a combination was
scored under is discovered — the one child of `04_score/02_aggregate` with results under that
combination — which is the rule every downstream step in the tree already follows.

It **does not list what the repository declines to version**. See §4.

**The tree pages gained the claims.** Each node now carries the claims from the collection
whose `node:` is that node, with each grounds path linked to the file it names. Rules 8 and 9
were built as separate machinery and this is where they meet: descending the tree, a reader
reaches the statement and the values it rests on in the same place.

## 4. What went wrong, kept

**The report was presenting somebody else's wheels as a node's scripts.** `c_ensemble`'s
"Scripts" section was **6 117 files**, of which 11 are the node's. The rest is the virtual
environment `uv` builds inside the model's contract directory the first time chap-core runs
it, plus `__pycache__`. The first build was 21 MB and three node pages were over 200 KB
apiece.

The fix is not a list of names to skip. The builder asks git — `ls-files --others --ignored
--exclude-standard --directory` — and shows nothing the repository declines to version. What
is not part of the method is not part of the report, and the two cannot drift apart, because
there is one place that decides.

**The first build crashed on a province with no evaluable cell.** `crps_by_location.csv`
carries an empty mean for Xaisomboun rather than a zero, which is correct — it contributes
nothing to the metric and a zero would be a score. Sorting on it raised. The fix sorts blanks
last and prints them as an em dash; reading an empty mean as zero would have put a
perfect-looking province at the top of every table.

## 5. Decisions taken in this batch

| Decision | Agency |
|---|---|
| A claim states the figures a file holds and never a ratio between two of them that no file computes | agent-autonomous |
| The detail pages are built for every scored combination, not only for `main` — the reported analysis must not be the only one a reader can descend | agent-autonomous |
| The report shows exactly what git tracks, by asking git rather than by carrying a skip list | agent-autonomous |
| `.gitignore` ignores the report's contents rather than its directory, so its `provenance.md` can be versioned | agent-autonomous |
| The folder's `README.md` is generated with the report; its `provenance.md` is not | agent-autonomous |

## 6. Compliance for this batch

| Rule | Status |
|---|---|
| 1 — provenance | `AI-generated/hierarchical-report/provenance.md`, with the script's hash, the inputs, the commit and what the build establishes |
| 2 — no manual editing of outputs | Nothing hand-edited. The claims were appended by `claims.py`, the report written by its builder; the one hand-written file in the report folder is its provenance record, and it is append-only |
| 3 — environment | Unchanged. The report reads files and runs no analysis, so `environment/` is not involved; the build is `.venv/bin/python` |
| 4 — version control | Committed before the build and again after, and the change to `.gitignore` is named in the message as a change to the method's own files |
| 5 — intermediates | Nothing new to store; the report stores no numbers of its own by design |
| 6 — seeds | Nothing here draws |
| 7 — plots | No new figures |
| 8 — hierarchical report | **Done.** This batch |
| 9 — claims | **Done.** Eighteen added, 39 total, every one resolving |
| 10 — release | Not this batch; batch 19 |
| `/validate invariants` | Passes |

## 7. What this batch did *not* do

**It ran no analysis and moved no number.** Nothing in `analysis/` changed. That is the point
of a batch that comes after the holdout has been opened: plan §3 forbids re-running anything
once a holdout number has been seen, and a batch that reports what the analysis found must
not be able to change it.

**It did not write the manuscript.** Rule 9's second step — claims to text — is batch 19's,
and the case write-up it produces is what `/claims check-text` will be run against.

**It did not run `/validate cleanroom` or `/validate outsider`.** Both are batch 18's, and
the clean-room run is the largest untested claim in the repository: `analysis/run.sh` is now
about six hours and has never been run end to end from a clean environment.

## 8. What is still unknown

- **Whether a reader who is not the agent can find what they want in 1 175 pages.** The link
  check says every path resolves; nothing says the structure is legible. `/validate outsider`
  in batch 18 is the first time anyone but the author will look at it.
- **Whether the claim collection is complete.** Forty-nine stored results are cited by
  nothing. Most are illustrations or intermediates, and the way to find out about the rest is
  to write the case study and see what it needs — which is batch 19, and is the reason Rule 9
  makes the collection precede the text rather than follow it.

## 9. For the human

- **The project's findings are now all in one file.** `Human-AI-collaboration/claims/claims.md`
  — 39 statements, each bound to the result grounding it, each with its scope and its agency.
  Nothing enters the manuscript that is not there. It is worth a read before batch 19 writes
  from it, because what is in it now is what the case write-up can say.
- **The report opens at `AI-generated/hierarchical-report/index.html`.** It is gitignored and
  rebuilt in about two seconds by `/hierarchical-report`. Start at the reported conclusion and
  click through to `detail/main/` — that path is the whole of Rule 8 in four clicks.
- **One thing you may want to overrule.** C23 reports the paired difference and its standard
  error separately rather than the 1.90 standard errors `readme-at-start.md` states, because
  no file holds the ratio. The alternative is a two-line script at `04_score/03_compare` that
  computes and stores it, after which the claim can say 1.90. That is a change to the analysis
  and phase E forbids re-running anything, so the honest options are the current phrasing or
  nothing — unless you read a script that divides two stored numbers as outside the freeze, in
  which case say so and batch 18 can add it.
- **Batch 16's open question stands.** The case write-up has to say where this setup was more
  trouble than it was worth. Batch 18 or 19 is the moment to say if you want that judgment to
  be yours.
