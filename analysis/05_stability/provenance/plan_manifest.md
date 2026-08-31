# Provenance — the perturbation manifest

```
result:              results/manifest.csv
                     results/forks.csv
                     results/manifest_notes.json
                     results/tier2_rule.md
script:              scripts/plan_manifest.py
                     sha256:f65032149dfd55953f5c082add7c00547b3db9183132ed6da79905711311be35
                     scripts/lib/inventory.py
                     sha256:71e0687ad3227b07cd569ba167ad3c63fd7cfd9b1636f798a545de72e8c59667
invocation:          "$PYTHON" scripts/plan_manifest.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/**/claim.md — every alternatives node in the tree, which is
                       what the fork inventory is read from
                     analysis/03_models/**/results/*/run_cost.json — 19 measured backtests
                     analysis/04_score/01_collect/results/*/models.csv — which models each
                       combination on disk actually scored
                     analysis/05_stability/results/step_costs.json
                     AI-generated/candidate-forks/*/fork_sweep.json
                     AI-generated/candidate-forks/*/fork_leaderboard.csv
                     AI-generated/candidate-forks/families/family_leaderboard.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The manifest is enumerated, never sampled.
commit:              26dca49
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** The set of analyses phase D runs, fixed before any of them has
run. **17 forks** in the tree; **24 tier-1 combinations** — the main path plus every child
of every fork that the main path does not take, one at a time; **8 tier-2 slots**, whose
occupants are computed from tier 1's own conclusions by `tier2_rule.md`; and **1 tier-0
combination**, `family_ensemble`, which exists on disk, perturbs nothing, and is in the
register because the register has to be complete for the new `combos` invariant to mean
anything.

**Nothing in it is typed.** The forks come from the tree — `lib/inventory.py` walks
`analysis/` for alternatives nodes rather than carrying a list, which is why the count is
17 and batch 5's hand-written inventory said 10. The costs are measured backtests and
measured step times. The informativeness prior is each fork child's own effect from the
phase-C sweeps, and only from a sweep whose recorded base configuration still matches the
family's current one, so a table taken around a main path that has since moved cannot
order this one. The two stage names that are stated rather than derived are in
`STAGE_OVERRIDE` with the reason, and `assert_unique_names` fails the planner if any two
forks ever claim one combination name.

**What the prior does and does not do.** It orders the rows; it selects nothing. The whole
manifest is inside budget — 3.3 hours against 12 — so the order decides what runs first,
not what runs. If a later batch does cut, `manifest_notes.json` names the cut order in
advance: tier 2 from the bottom up, then the reference's repeats on tier-2 setup rows, then
tier-1 rows in rank order and never by kind.

**The tier-2 rule is fixed now and hashed.** `tier2_rule.md` is written by this script
before any tier-1 combination has run, and its sha256 is in `manifest_notes.json`. Choosing
which pairs to explore after seeing tier 1's numbers would be selection with extra steps —
the objection this project makes to an unfrozen holdout manifest, one level down.

**The cost columns move between runs and the row set does not.** They are wall-clock
measurements; see `measure_step_costs.md`. Which combinations the manifest contains, how
they rank and what the rule says are functions of the tree and are stable.

**What the file records as not costed**, because an absence has to be a visible decision:
writing the nine children that have no scripts, which is implementation effort rather than
compute; and acquiring the external Lao population series `popColumn_backCast` needs, which
the repository does not hold and batch 13 must archive before that row can run.

alternatives-considered: keeping batch 5's hand-written inventory and adding the five forks
phase C created — rejected, because the same omission would recur the next time a fork was
added, and computing it from the tree makes a missing fork visible as a missing node rather
than as a line nobody wrote. Ranking informativeness by a hand-assigned score per fork —
rejected in favour of reach plus the measured phase-C effect, because a hand-assigned score
is the agent's opinion about what will matter, entering a file whose purpose is to stop the
agent choosing what matters. Enumerating the full conditional product (over a thousand
analyses) — recorded as cut in `manifest_notes.json`, on batch 5's reasoning. Naming every
combination `<subtree>_<stage>_<child>` for unambiguity — rejected because thirteen
combinations already exist under the short scheme and renaming a combination breaks every
file that points at it.

agency: agent-autonomous, within a human-set frame. That phase D is two tiers over the
forks, that tier 2 is eight pairs chosen by a rule fixed in advance, and that the cut is
recorded with what fell below it are the plan's (`readme-at-start.md`, §Compute budget, and
`AGENTS.md` §4, human-set). Which forks exist, how they are costed and ranked, the 12-hour
budget figure and the tier-2 rule's exact form are the agent's.

---

## Correction within the batch — the storage projection, 2026-08-29

```
result:              results/manifest.csv        (gains a `projected_bytes` column)
                     results/manifest_notes.json (gains a `storage` block)
script:              scripts/plan_manifest.py
                     sha256:6af7be46dfabe494c831ab469918dd5ec59cb6b50208a2d612057be50090a15b
commit:              2e186f6
instructions-commit: cf97b81
produced:            2026-08-29
```

**The section above names a hash that is no longer on disk.** The planner was extended
after that record was written, to project the manifest's stored bytes the same way it
projects its seconds — each row's parts summed from the largest measured example of that
part on disk — because `/annotate-criticality` is asked to cover "the storage the manifest
implies" and a projection typed into a criticality table would be a number with no file
behind it. The earlier hash is `f65032149dfd55953f5c082add7c00547b3db9183132ed6da79905711311be35`
at commit `26dca49`, and git holds that version; **the manifest as committed at `2e186f6`
was produced by the script named here**, not by that one.

Recorded as its own section rather than by correcting the line above, because `AGENTS.md`
§8 says provenance is appended and never overwritten, and because the sequence is the
finding: a script edited after its output has been recorded leaves a record naming bytes
that are not on disk. Batches 10 and 11 each ended this way and each paid for it with a
re-run; here the output is a two-second regeneration, so the cost was the paragraph.

**What did not change**: the row set, the ranking, the tier-2 rule and its sha256, and
every cost in seconds. The projection adds a column and reads no new inputs beyond the
sizes of directories already in the tree.

alternatives-considered: putting the projection in `criticality.md` by hand, which is what
every other `criticality.md` in this repository does — rejected here because the figure is
an aggregate over 24 rows rather than a size anyone can read off a directory listing, and
Rule 1 does not have an exception for annotations. Computing it in a separate script so
this one's hash would have stayed put — rejected as the wrong reason to split a file.

agency: agent-autonomous.


---

## Batch 22 — both baseline children are built

```
result:              results/manifest.csv
                     results/manifest_notes.json
                     results/forks.csv
script:              scripts/plan_manifest.py — unchanged by this batch
invocation:          environment/chapenv/bin/python \
                       analysis/05_stability/scripts/plan_manifest.py
inputs:              the tree, through scripts/lib/inventory.py; results/step_costs.json;
                     each model's results/*/run_cost.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** Re-planned once the two children had scripts. The only change to
the manifest is the `built` column on rows 9 and 10, from `False` to `True` — **no row was
added, removed, renamed or re-ordered**, and the count is still 24 tier-1 rows plus 8 tier-2
slots plus the held row. `0 children have no scripts yet` is now the planner's own statement
of the thing batch 12 recorded as what bound: every reasonable alternative the tree names is
now a path the tree carries.

**Tier 2 stays unselected.** Fourteen tier-1 rows have not been attempted, and batch 13's
rule that the tier-2 rule may not read a partial tier 1 still holds. `tier2_rule.md` is
untouched and its sha256 is unchanged.

alternatives-considered: not re-planning at all, and letting the `built` column stay stale
until batch 14. Rejected — `/validate invariants` compares the manifest against the tree, and
a manifest that says a built child is unbuilt is the drift that check exists to catch.

agency: agent-autonomous.
information: agent-retrieved — read from results/manifest.csv.


---

## Batch 15 — re-planned against a completed manifest, and it did not move

```
result:              results/manifest.csv — byte-identical to what batch 12 froze
                     results/manifest_notes.json — one measured field changed
script:              scripts/plan_manifest.py — unchanged by this batch
invocation:          environment/chapenv/bin/python \
                       analysis/05_stability/scripts/plan_manifest.py
inputs:              the tree (scripts/lib/inventory.py), results/step_costs.json,
                     results/conclusions.csv, results/run_status.csv,
                     analysis/03_models/**/results/*/run_cost.json,
                     AI-generated/candidate-forks/*/fork_sweep.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none
commit:              f3904c5
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes, and why it was worth running.** Batch 15 puts `run_manifest.py` into
`run.sh`, and `run.sh` re-plans the manifest on every run — so before the driver could join
it, the question was whether re-planning moves the frozen file. It does not.
**`manifest.csv` came back byte-identical**, with the same 33 rows, the same ranks and the
same eight tier-2 pairs, now that every row has been attempted and the pair rule reads a
complete tier 1. The one field that changed is `manifest_notes.json`'s
`on_disk_now_results_mb`, from 681.0 to 1126.3, which is a measurement of the disk and not
a plan.

That matters beyond this batch. The criticality note says the manifest is regenerable and
must not be regenerated casually; the reason it is safe to regenerate it inside `run.sh` is
that its inputs — the tree, the frozen rule, and a tier 1 that has now run — no longer
change what it produces. The one input that would move it is `step_costs.json`, which
`measure_step_costs.py` re-measures and which feeds only the rank order and the estimates.

**A gap this run exposed and did not close.** `plan_manifest.py`'s docstring promises a
`--freeze-check` flag that refuses to fill the tier-2 slots if the rule's text has changed
since its hash was recorded. **The flag does not exist**, and could not work as described if
it did: the script writes both the rule and its hash from the same constant on every run, so
comparing them can only ever succeed. What actually evidences the freeze is git — batch 12's
commit of `tier2_rule.md` — and `freeze_holdout_manifest.py`, which this batch added, does
enforce the comparison the flag describes by checking the rule's text against the hash
recorded in the *existing* notes before overwriting them. The docstring is left as it is
because correcting it is a change to a script whose output is the frozen manifest, and this
batch's finding is recorded here rather than smoothed away.

alternatives-considered: not re-planning, and putting the driver into `run.sh` without
knowing whether the surrounding steps preserve the frozen file. Rejected — it is the one
question that had to be answered before batch 15 could make `analysis/run.sh` reproduce the
stability result, and it is answered by running it and diffing, not by reading the code.

agency: agent-autonomous.
information: agent-retrieved — read from results/manifest.csv and `git diff`.
