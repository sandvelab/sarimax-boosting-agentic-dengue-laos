result: results/comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:0b6c8c588ca9cded3fefe456eb1fec70673f405541748f5edec1a896e1469cb0
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv  sha256:4ada133b7ddd96f9e702855cd7b2736267e355b6ca2afd0cc69445ad08f11c9d
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: 90add4c  (the script as it ran for the committed result; d8f9b07's version ran once
        before the per-split breakdown was added, and its comparison.json was superseded before
        being committed)
instructions-commit: 595c32d
node: analysis/04_stage2/f_oosErrorRidge
produced: 2026-09-20
what it reports: mean CRPS and 90% coverage for stage 1 alone and the candidate on the same
        371 cells; the combination-rule decomposition (stage 1 / stage 1 clipped at zero /
        corrected unclipped / corrected and clipped) from the per-cell columns; by horizon; by
        split with the count of splits improved and the share of cells improved; by province.
alternatives-considered:
  - Reporting only the headline pair, as earlier siblings did: rejected because this candidate
    changes two things (correction, clip) and the reader must see them apart; and because
    05_residualStructure showed the error mass sits in a few provinces, so a per-province and
    per-split table is what says whether a mean gain is broad or a few cells.
  - A formal paired test across splits: not done -- eight splits; the count of splits improved
    (4 of 8 here) and the share of cells improved (56.6%) are reported as counts, and the
    stability phase is where the spread across choices is measured.
agency: agent-autonomous
