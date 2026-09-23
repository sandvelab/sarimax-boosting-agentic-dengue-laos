Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 20)

# Reproducibility report — what this repository can establish about how its results came about

Every count below is read from `inventory.json` in this folder, written by
`AI-internal/useful-scripts/repro_inventory.py` at the commit named there. The inventory
establishes shape: how many records exist, which fields each carries, whether every pointer
resolves. It cannot establish that a record is true. Section 5 was written by reading, and it is
the section a critical reader should start with.

## 1. What was produced

The analysis is a tree of 23 nodes under `analysis/`, each an analytical question with the
scripts that address it, the results they wrote and a provenance record per result. Three nodes
are sub-analyses parents; one, `04_stage2`, is an alternatives node with ten children of which one
(`h_levelOnlyBoosting`) is the main path and nine are paths not taken, all kept complete and
runnable; nineteen nodes are leaves. The tree holds 43 node scripts and 9 shared library modules,
23 run scripts, 299 result files, and 103 scored results — a `per_cell_scores.csv` with its
`conclusion.json` — for stage 1, both baselines, the ten stage-2 candidates and every development
and held-out stability combination. No node overrides the project environment.

At each level of the tree the answer is in the node's `claim.md`, and the claim collection
(`Human-AI-collaboration/claims/claims.md`) holds 32 claims that together cover every node with a
result. What they say, in one paragraph: stage 1, a per-province SARIMAX(1,1,1)×(1,0,0)₁₂,
scores mean CRPS 26.05 on the development backtest and beats both required baselines; the five
stage-2 candidates trained on its in-sample residual fail, because that residual is white; the
five trained on its multi-step out-of-sample error succeed, and the pre-registered one scores
24.35 (−6.53%) with coverage improved; the sign of that margin survives all 26 development
perturbations and its size turns on stage 1 and on the construction of the training errors; on
the held-out year, opened once, the ensemble scores 99.20 against stage 1's 128.51 (−22.81%)
with the sign surviving all 26 frozen perturbations, while seasonal climatology scores 77.29 on
the same cells and every model's coverage collapses on an epidemic year. Two documents were
written from the collection: a short overview (1,450 words, 13 claims cited) and the full
manuscript (about 7,200 words, all 32 claims cited).

## 2. What is tracked, and how

The chain from a sentence in the manuscript to a command runs through five links, and each link
is a file.

**Sentence → claim.** The manuscript's provenance sidecar has 127 statement rows. 85 rest on a
named claim; 37 are marked `method:` and rest on a stored file (a node's `claim.md`, a
`conclusion.json`, a freeze or opening record, the plan); 5 are literature or interpretation
rows whose grounding is stated in the row. The overview's sidecar has 48 rows, 35 on claims and
12 on method files.

**Claim → result.** The 32 claims carry 67 pointers to result files, and all 67 resolve to a
file that exists. Every claim carries a scope qualifier; 28 carry an `alternatives` field naming
what would have supported a different statement; 17 are scoped to the held-out year. 31 are
`agent-autonomous` and one (C26, stage 1's documented weaknesses) is `human-set`, because the
decision it reports was the human's.

**Result → script, inputs, environment, seed, commit.** 41 provenance records, holding 48
dated sections (a record that is appended to when its script changes has more than one). All
41 carry all ten required fields: result, script with digest, exact invocation, inputs with
digests, environment, seeds, the commit the code was at, the commit the instructions were at,
node and date. 40 carry `alternatives-considered`; all 41 carry `agency`; 13 carry
`information`. The records name 26 distinct run commits and 3 distinct instruction-set commits.
The invariant checker verifies, at every commit, that every digest a record gives is the current
digest of the file it names.

**Environment.** One declarative specification, one lockfile of 18 packages at exact versions
under CPython 3.13, one build script that installs from the lockfile and reports any difference
between what it built and the lock. No container image, by decision: the pipeline is native
Python with no compiled platform-specific runner.

**Commits.** 268 commits from the first on 2026-08-23 to the release; 35 "Before" and 26
"After" commits bracket analysis runs so that each result corresponds to a commit; 2 commits are
labelled as methodological changes to the instruction files, which are tracked (`AGENTS.md`,
`CLAUDE.md`, `.claude/settings.json`) together with the 17 skill files.

**Verification of the chain, not only its presence.** All eleven invariant checks hold at the
release commit. The first clean-room run (2026-09-22, at commit `cbb2a26`) built the
environment from nothing in a fresh clone, ran the whole analysis and found 288 results
byte-identical, 10 declared as varying (wall-clock and timestamps), 0 missing and 1 differing,
which was a stopwatch embedded in a report file and was fixed before the release commit. An
outsider test on 2026-09-23 found twelve defects in the instructions and records, ten of which
were fixed before release. The release-time clean-room run and outsider test are recorded in
`AI-generated/validation/` and summarised in the batch-20 report.

## 3. The veridical section

**What was explored.** Ten stage-2 candidates, differing in family (linear, ridge, Bayesian
ridge, gradient-boosted trees, random forest), in input (lag-12 residual and month; with climate
covariates; the full forecast-time feature set; the level-only set), in pooling (per province;
pooled across provinces), in the error trained on (in-sample one-step residual; in-window
multi-step out-of-sample error), and in the combination (additive; additive and bounded). One
diagnostic node characterising stage 1's errors and estimating how much of them is predictable
at all. A stability node whose development manifest has 70 rows: 1 gate, 9 tier-1 siblings, 26
tier-2 perturbations planned around the main path, 29 tier-2 rows from the earlier run around the
previous main path kept as superseded, and 5 tier-3 alternatives not run, each with its reason.
The held-out manifest has 43 rows: 33 planned and run (3 tier-0, 4 tier-1, 26 tier-2) and 10 not
run with reasons (the five in-sample-residual siblings and the five tier-3 alternatives).

**On what basis each choice was made.** Stage 1's order was a first default and is recorded as
such; stage 2's main path was chosen by a rule written before the last candidate's result was
seen, recorded in the plan's decision log and the node's claim; the perturbations were ranked by
expected informativeness and costed, and the budget line fell below every planned row; the
held-out evaluation design and reporting rule were frozen with the manifest. The two freezes are
dated and hashed: the development manifest at commit `cef9a18` (2026-09-21) and the held-out
manifest at `67f998c` (2026-09-22), and the single opening of the held-out year is recorded at
commit `8eda4fd` (2026-09-22, 33 of 33 rows).

**How stable the conclusions were.** Sign-stable in every combination run: 29 of 29 in the first
development set, 26 of 26 in the second, 26 of 26 on the held-out year, with coverage never worse.
Size-unstable in a recorded way: on development the margin turns on stage 1's specification and
on how the training errors are constructed (eight rows move it by more than two points), not on
the stage-2 family's tuning; on the held-out year sixteen rows move it, and it turns above all on
the second stage's input, where the two level-only configurations gain about 23% and every
full-feature configuration 4% or less. Three development rows and three held-out rows scored
better than the main path and none was promoted.

**What was left unexplored and why.** The five tier-3 alternatives: a log-transformed stage 1
and a count or heavier-tailed predictive family (both need a verified metric extension; the second
is the most consequential absence, being the one change identified as able to repair coverage);
a multiplicative combination rule (undefined near zero); an ENSO covariate (a new acquisition and
a governance decision); Chap-native evaluation (decided against at the outset). The five
in-sample-residual siblings on the held-out year (each would need a holdout-capable rewrite; all
lose on development; the diagnostics explain why). Interactions between perturbations. Hyperparameter
search. A per-province or partially pooled stage 2, which the province pattern suggests.

## 4. The agency record

Three sources record who decided what, and they agree.

| Source | human-set | agent-autonomous | mixed | open |
|---|---|---|---|---|
| Plan decision log (§4b), 69 rows | 12 | 50 | 5 | 2 |
| Provenance records, 41 | 0 | 37 | 4 | — |
| Claims, 32 | 1 | 31 | 0 | — |

The human investigator set the architecture, target, data and sealed year; reused the
evaluation scheme for comparability; excluded any external reference; bound stage 2's horizon
set to the scheme's; after each negative result chose to keep exploring stage 2, including
trying climate covariates, adapting a community model and running the systematic diagnostic
iteration; fixed stage 1 as documented-not-repaired; asked for stage 2 to be explored further and
one configuration annotated before the freeze; kept that configuration and left stage 1 unreopened
at the freeze; asked for the overview article; and settled which instruction set governs the
repository. The four mixed provenance records are the ones whose configuration was the agent's
and whose existence was the human's (the two further stage-2 candidates, the weaknesses document,
the stability plan). Everything else, including stage 1's order, every candidate's design, the
selection rule, the manifests, the budgets, the held-out design and the reporting rule, was the
agent's. The two open items are the human's: whether to build the predictive-family fork now that
the year is open, and the push and citable deposit of this release.

Information gathering is recorded in 13 of 41 records (9 `agent-retrieved`, 4 stated otherwise)
and in the decision log where a step rested on it: the literature search, the Chap repository
listing, the upstream data licence check, the reference re-verification.

## 5. What does not hold

**The checks verify shape, not content.** All eleven invariants pass, every digest matches,
every claim resolves. None of that says a record names the script that actually ran, that a
claim's pointer supports its statement, or that a sentence's sidecar row is the right claim. One
error of exactly that kind was caught in the overview article by reading the check-text flags,
and one imprecision in the manuscript the same way. There is no check that would have caught
either.

**28 of 41 records have no `information` field.** The specification requires it where a step
rested on gathered information; for most steps here nothing was gathered, but an absent field is
indistinguishable from an omitted one. One record (`04_stage2/i_boundedBoosting/provenance/compare_to_stage1.md`)
has no `alternatives-considered` field.

**The instruction set in force was not the one recorded, for batches 1–19.** Every record's
`instructions-commit` names the commit of this repository's `AGENTS.md` and `.claude/`; none can
name the parent directory's `CLAUDE.md`, which was loaded into every session until 2026-09-23
because the tracked settings file's exclusion placeholders were never substituted. The file
concerned cross-vault housekeeping and nothing in it was acted on, so no stored number moved,
but the published statement of the method was short by one file until the decision log recorded
it. The exclusion now lives in a gitignored local file, so a cloner inherits the same
unprotected default and must perform the setup step.

**Development-set selection happened three times on the same 371 cells**, and the diagnostics
that informed the successful candidates read those cells. The development scores carry the
optimism that implies; the held-out year is the only guard, and on this year the margin was
larger, not smaller. That is one year.

**Reproduction re-opens the sealed year.** Because the opening record is tracked and the
working-tree seal is not, a clean-room clone that runs the whole analysis writes opening number 2
in its own copy. That is the designed behaviour and it is what the seal's two halves are for, but
a reader who counts openings in a clone will count two.

**CSV writers are non-uniform in line endings**, settled by `.gitattributes` rather than by
fixing the writers, because fixing them would change the bytes of the sealed held-out file and
re-freeze phase E after the year was opened. A future contributor who "fixes" one writer without
re-hashing every record that names its output breaks the digest chain.

**Prior-project text remains in two machinery files**: comments in `check_invariants.py` citing
the prior project's batch numbers and a dead manifest path, and a dead headline block in the
report generator guarded by a file-existence check. Both render nothing and change no verdict;
both were left because changing the checker or the generator in the release batch would make the
release's checks a different program from the one that passed.

**The history carries a credential-shaped filename and the tree carries the author's
home-directory path.** `.claude/settings.local.json` was tracked from the prior project's first
commit until it was removed; its content was three permission grants, one naming an absolute
path, and no secret. The path appears in four tracked files that record which instruction file
was in context. The author's name and e-mail are in every commit's metadata since the first
push, so neither discloses anything new; both are recorded rather than removed, and the history is
not rewritten because every provenance record cites its commit hashes.

**Stage 1's determinism was spot-checked on one fit**, not all 136, on the reasoning recorded in
its provenance record. The seed audit that record asks for was not run.

**The environment's builder is not itself pinned.** The lockfile pins 18 packages; the build
script calls `uv`, whose version is not recorded, and the machinery's own `.venv` is built from
whatever `pip` resolves at the time. The analysis reproduced byte for byte across two builds
eighteen commits apart, so nothing has moved yet.

**Seven of the eight references were not re-read at writing time.** The manuscript characterises
them as the batch-10 literature record does, which read them once; only their bibliographic
details were re-verified, and the one whose characterisation was checked against its abstract
needed correcting.

**The hierarchical report's by-province and by-month tables are computed for display**, not
stored, and each page says so. The secret scan skipped 22 history lines over 4,000 characters as
data and counted them. The five in-sample-residual candidates' held-out behaviour is not measured.
The stability rows change one thing at a time. The by-decision agency table above is a count of
labels, and a label can be wrong in the same way a record can.

**Not yet done at the time of this report**: the push of the release commits and the deposit of a
citable, versioned snapshot with a persistent identifier, both of which are the human's steps.
