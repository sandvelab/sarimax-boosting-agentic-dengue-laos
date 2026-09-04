# Provenance — every pool row's reconstruction, settled once the whole set has run

```
result:              results/pool_reconstruction.json
script:              scripts/reconstruct_pools.py
                     sha256:f483f8c1ba36d68f97e9275f8f98d5a165e3d596555f8c88a4ee3b92947adbac
                     it re-uses the rule rather than restating it: it imports
                     stored_evaluations() and matching_evaluation() from
                     analysis/03_models/03_candidate/c_ensemble/scripts/check_pool.py
                     sha256:4f450f3f2fa62962171a1f4947712afdfd799687ab252e7aa93a139ca464b5f4
                     and re-runs that script, as a subprocess with COMBO set, exactly as
                     c_ensemble/run.sh runs it
invocation:          "$PYTHON" scripts/reconstruct_pools.py
                     (from 05_stability/, via run.sh, as its last step; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/03_models/03_candidate/c_ensemble/results/*/
                       {members,model_spec,pool_check}.json and eval.nc
                     and, through check_pool.py, each member node's
                       results/*/model_spec.json and eval.nc
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none of its own; the reconstruction it drives uses the pool's
                     allocation seed, recorded in check_pool.md
commit:              9a0f8e7
instructions-commit: 595c32d (AGENTS.md and .claude/ unchanged by this batch)
node:                analysis/05_stability
produced:            2026-09-04, batch 28
```

**What it establishes.** That the pool's second path is a property of the analysis and not
of the order the analysis was run in. **Eleven of the 51 pool rows can be rebuilt from their
members' own separate evaluations; forty cannot, and the reason is structural**: those rows
move a fork *inside* one of the members, and the tree evaluates a member on its own only
under the family fork's own combination, so no run of this analysis ever produces that
member's separate evaluation under that configuration. The file names which rows those are
and why, so the absence is a recorded decision rather than a gap.

Across the eleven, the residual between the rebuilt pool and the pool that ran is **0.016 to
0.136 CRPS** — largest on the holdout rows, where the scores are four times the size — and
it is the sampling error of the pool's own allocation, which takes a different seeded
subsample of each member's thousand draws than the model did.

**Why this step exists at this node.** A candidate family runs on its own only under a
stability row, so on a run of `analysis/run.sh` from nothing the main path's pool is checked
hours before its members have been evaluated separately, records truthfully that the
reconstruction could not be done, and nothing revisits it. Batch 16 left exactly that record
on the headline holdout row, where it read as a statement that the reconstruction was
impossible. This is the one place in the tree that runs after every combination, so it is
where that can be put right — and it is the shape this node already has twice, in the second
passes of `plan_manifest.py` and `collect_conclusions.py`, which exist because a first pass
cannot know what has not run yet.

**What it costs.** Nothing on a tree that has not moved: it compares each file's named
evaluations with the rule's and re-runs `check_pool.py` only where they differ. The second
invocation in this batch rewrote no file, took 1.2 s, and returned a byte-identical
`pool_reconstruction.json`. The first rewrote 49 files in 2 min 28 s.

alternatives-considered: running the sweep from `analysis/run.sh` after `05_stability`
(rejected — `AGENTS.md` §2 makes a node's `run.sh` a list of its children's main scripts and
its own scripts, and the root calling a script four levels down is not either of those,
where this node's scripts already drive every other node's); writing the reconstruction into
a file of this node's own instead of back into each `pool_check.json` (rejected — the
reconstruction is the ensemble node's claim and two claims already cite it there, and
splitting it would move a reported number into a second file to avoid rewriting the first);
recording in this file which rows it re-ran (rejected — that is a fact about one invocation,
not about the analysis, and putting it here would make this file differ between a cold run
and a warm one for reasons that are not results; it is printed to the run log instead).
agency: agent-autonomous.
information: agent-retrieved.
