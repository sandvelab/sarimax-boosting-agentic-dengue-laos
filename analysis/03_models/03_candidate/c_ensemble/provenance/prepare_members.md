# Provenance — the pool's membership

```
result:              main/members.json
                     family_ensemble/members.json
                     weighting_crpsWeighted/members.json
script:              scripts/prepare_members.py
                     sha256:8536629366df2facffe491eb3c405cc4675f73693459e731deb497d8251d1978
invocation:          "$PYTHON" scripts/prepare_members.py, with COMBO set
inputs:              every Chap contract directory under analysis/03_models except this
                     node's own, found by glob rather than listed:
                       01_baselines/01_persistence/a_empiricalChange/scripts/persistence_model
                       01_baselines/02_climatology/a_expandingWindow/scripts/climatology_model
                       03_candidate/a_hierNB/scripts/hier_nb_model
                       03_candidate/b_boosted/scripts/boosted_model
                     and, for the two that take one, the configuration each family's own
                     assembler writes under this combination.
environment:         environment/ (project main)
seeds:               none — this step chooses nothing and draws nothing. Each member's
                     seed is inside the member's own configuration, which this step
                     copies the path and the hash of.
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-28
```

**What it establishes.** Which models the pool contains, where their code is, how to run
them, and the sha256 of every file behind each of them. The document is the pool's
membership as a stored artifact; the model configuration carries its path and its hash,
and the model refuses to run if the two disagree.

**Why the members are discovered and not listed.** A list here would be a second statement
of what models this project has, and the one that decides what the pool contains. The glob
means a model joins the pool by existing in the tree — which is also the property that
makes the node's claim ("a weighted combination of the models this project already has")
true of the code rather than of a comment.

**Why this step runs its siblings' scripts.** `AGENTS.md` §2 sanctions it: the paths not
taken are executed by the stability node, which calls its siblings' main scripts, and this
node's claim is about its siblings in the same way. What it runs is each family's fork
main-path children and that family's own assembler, which write configuration and nothing
else; it never runs a sibling's evaluation. And it runs them only where the combination has
no configuration already, so a combination whose configuration was produced by the family's
own step is left exactly as that step left it.

**Verified rather than assumed.** Under `family_ensemble`, both member families' assembled
`model_configuration.yaml` came out byte-identical to the ones their own nodes had already
written under `main` and `family_boosted` — the same configuration reached by a different
route.

alternatives-considered: copying the members' code into this model's directory (rejected —
four copies that will drift, and the node's whole claim is that these are the models on the
leaderboard rather than versions of them); importing the members' modules in-process
(rejected — their entry points are the platform's contract and their module names collide,
so calling the contract is both truer and simpler); naming each member's evaluation
combination in the configuration (rejected — a combination name is not a property of the
member, and a perturbation that moved a family's fork would then configure the pool's member
from the wrong place; resolving the member's configuration under the running combination
makes the pool follow the perturbation instead).
agency: agent-autonomous

---

## Batch 22 — membership resolves the baseline forks, and says so in a file

```
result:              results/$COMBO/members.json
                     results/$COMBO/member_selection.json
combinations:        main, persistence_negBinomialFloor, climatology_frozenWindow
script:              scripts/prepare_members.py
                     sha256:d8c681cc2623ab0a4f5400eab9608f02a978ad2bbbbba02418f076d8eedebe8b
invocation:          unchanged: "$PYTHON" scripts/prepare_members.py, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 22 and
                     COMBO_BASE=main. Re-run once under COMBO=main with no base, to
                     produce member_selection.json there and to check that members.json
                     did not move.
inputs:              the tree itself: every analysis/03_models/**/scripts/*/MLproject, and
                     the claim.md of every alternatives node above one
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; this step assembles a document and runs no model
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-29
```

**What it establishes, and the defect it removes.** Membership was discovered by globbing
for `MLproject` and taking every contract directory found. That was correct while each
baseline fork had exactly one built child. Batch 22 builds the second child of both, so the
glob would have returned **six** contracts under every combination including `main`, and the
reported model would have become a six-member pool containing two persistence baselines and
two climatologies — silently, at equal weights, with the doubled models carrying half the
pool. Membership now resolves every alternatives fork above a contract to the child this
combination takes, by the same `resolve_glob` lookup `04_score` uses; the family fork is the
one exception, because pooling *its* children is what this node exists to do. A doubled
member name is now a hard failure rather than a doubled weight.

**Verified.** Re-run under `main`, `members.json` is **byte-identical** to the file the
reported analysis was produced with, so the pool's configuration hash and every number
downstream of it are untouched. Under the two batch-22 rows the pool's persistence member is
`b_negBinomialFloor` and its climatology member is `b_frozenWindow` respectively — the
member moves with the perturbation, which is what phase D requires of it
(`results/$COMBO/member_selection.json`).

alternatives-considered: recording the resolution **inside `members.json`**, where the rest
of the membership is. Rejected because the pool's own configuration carries that file's
sha256 and the model refuses to run when the two disagree, so a line of prose added there
re-hashes the reported model's configuration and forces the headline analysis to be re-run in
order to say it. That integrity check is worth its cost and this is the cost. Also
considered: resolving forks by the tree's `main-path` field alone — rejected because it would
not move with the combination, which is the whole point.

agency: agent-autonomous.
