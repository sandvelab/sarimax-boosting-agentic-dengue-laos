result: results/stage1_weaknesses.json
script: scripts/03_stage1_weaknesses.py
        sha256:0734177a643c191777d5451c2142d0a06edf956f26b0d8737a2e3af919283bc0
invocation: ../../environment/env/bin/python scripts/03_stage1_weaknesses.py
inputs: results/test_cells.csv  sha256:017b69726c347172db2c64d712d0744f6a2183c3108a1de2bed73bc1373ae33c
         results/error_structure.json  sha256:46c15d49d00bc37759fd6d6caee7d4969c80a5c1348bf1d2ded932c0031b85c7
         ../02_stage1/results/conclusion.json  sha256:9c7243461554d34aa46e6601258995b19cd0f56301da5519316e476c38b4e693
         ../03_baselines/results/comparison.json  sha256:8a57810b773805fa30fc34f69db8b0867c7f9ad5bf0965e9528b1daf2fa1ff83
         (all produced earlier in analysis/run.sh's order; the stability node's
         alternative-specification scores are cited by path in the text, not read)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: 95a78fc
instructions-commit: 595c32d
node: analysis/05_residualStructure
produced: 2026-09-21
what it records: six weaknesses of stage 1 as specified -- W1 heavy-tailed standardised error
        behind the coverage deficit, W2 negative means, W3 a standard error that does not scale
        with the level, W4 systematic multi-step bias by level and season, W5 the 2008-09
        reporting-regime breaks, W6 an unselected first-default specification -- each with
        evidence (numbers and the file they come from), its effect on the forecasts, whether a
        stage 2 can address it, and the stage-1 fork that would address it and was not taken.
alternatives-considered:
  - Repairing any of them at stage 1: ruled out by the human (plan §4b, 2026-09-21: "do not
    repair anything in stage 1 -- that should be sarimax"); the project's question is whether
    a second stage earns its place on top of a SARIMAX, so the first stage is the premise.
  - Documenting them in prose only (02_stage1/claim.md): the prose is there too, but a list
    whose every number is read from a result file is what Rule 1 asks for, and it is what a
    manuscript section on limitations will be written from.
  - Placing this script in 02_stage1: rejected -- it reads this node's diagnostics, which run
    after 02_stage1 in analysis/run.sh; placing it there would break the tree's run order.
agency: agent-autonomous (the list and its wording); the decision not to repair is human-set.
information: agent-retrieved for the reporting-system context in W5 (Khampapongpane et al.
        2014, from batch 10's literature search).
