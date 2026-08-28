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
